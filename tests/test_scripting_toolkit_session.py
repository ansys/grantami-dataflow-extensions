# Copyright (C) 2025 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from unittest.mock import Mock, NonCallableMagicMock, create_autospec

from common import HTTP_SL_URL, HTTPS_SL_URL, PASSWORD, USERNAME, access_token
from mocks import scripting_toolkit
import pytest

from ansys.grantami.dataflow_extensions import MIDataflowIntegration


@pytest.fixture
def mock_stk(monkeypatch):
    # Using create_autospec ensures instances of class mocks have the expected interface and that methods of the
    # instance have the expected signature
    mock_module = create_autospec(
        spec=scripting_toolkit.module,
        spec_set=True,
    )
    # Autospec does not work recursively. Ensure OIDCSessionBuilder is also compliant with the interface
    mock_oidc_session_builder_kls = create_autospec(spec=scripting_toolkit.OIDCSessionBuilder, spec_set=True)
    mock_oidc_session_builder = mock_oidc_session_builder_kls.return_value
    mock_module.SessionBuilder.return_value.with_oidc.return_value = mock_oidc_session_builder
    # __version__ isn't supported by MagicMock, patch it again
    mock_module.__version__ = scripting_toolkit.VERSION
    monkeypatch.setattr("ansys.grantami.dataflow_extensions._mi_dataflow.mpy", mock_module)
    return mock_module


def test_mock_module_has_strict_interface(mock_stk):
    assert mock_stk.__version__ == "5.1.0"

    builder_kls = mock_stk.SessionBuilder
    with pytest.raises(Exception):
        _ = builder_kls()

    builder = builder_kls(service_layer_url="bla")
    builder_kls.assert_called_once_with(service_layer_url="bla")

    _ = builder.with_autologon()
    builder.with_autologon.assert_called_once_with()

    with pytest.raises(Exception):
        _ = builder.with_credentials()
    _ = builder.with_credentials("a", "b")
    builder.with_credentials.assert_called_once_with("a", "b")

    with pytest.raises(Exception):
        _ = builder.non_existent_method()

    # OIDCSessionBuilder is one-level deeper
    oidc_builder = builder.with_oidc()
    with pytest.raises(Exception):
        _ = oidc_builder.non_existent()
    with pytest.raises(Exception):
        _ = oidc_builder.with_access_token()

    _ = oidc_builder.with_access_token(token="str")
    oidc_builder.with_access_token.assert_called_once_with("str")


@pytest.mark.parametrize("timeout", [None, 1_000_000])
@pytest.mark.parametrize("retries", [None, 10])
class TestScriptingToolkitSession:
    @pytest.mark.parametrize(
        ["test_case_name", "expected_url"],
        [
            ("windows_https", HTTPS_SL_URL),
            ("windows_http", HTTP_SL_URL),
        ],
    )
    def test_windows(self, timeout, retries, test_case_name, debug_caplog, mock_stk, request, expected_url):
        kwargs = self._kwargs(timeout, retries)
        test_case = request.getfixturevalue(test_case_name)
        _ = test_case.dataflow_integration.get_scripting_toolkit_session(**kwargs)

        mock_stk.SessionConfiguration.assert_called_once_with()
        session_configuration_instance = mock_stk.SessionConfiguration.return_value
        self.check_session_config(session_configuration_instance, timeout, retries)
        mock_stk.SessionBuilder.assert_called_once_with(
            expected_url, session_configuration=session_configuration_instance
        )
        builder_instance = mock_stk.SessionBuilder.return_value
        builder_instance.with_autologon.assert_called_once()

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using Windows authentication." in debug_caplog.text

    @pytest.mark.parametrize(
        ["test_case_name", "expected_url"],
        [
            ("basic_https", HTTPS_SL_URL),
            ("basic_http", HTTP_SL_URL),
        ],
    )
    def test_basic(self, timeout, retries, test_case_name, debug_caplog, request, expected_url, mock_stk):
        test_case = request.getfixturevalue(test_case_name)
        kwargs = self._kwargs(timeout, retries)
        _ = test_case.dataflow_integration.get_scripting_toolkit_session(**kwargs)

        mock_stk.SessionConfiguration.assert_called_once_with()
        session_configuration_instance = mock_stk.SessionConfiguration.return_value
        self.check_session_config(session_configuration_instance, timeout, retries)
        mock_stk.SessionBuilder.assert_called_once_with(
            expected_url, session_configuration=session_configuration_instance
        )
        builder_instance = mock_stk.SessionBuilder.return_value
        builder_instance.with_credentials.assert_called_once_with(
            username=USERNAME,
            password=PASSWORD,
        )

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using Basic authentication." in debug_caplog.text

    @pytest.mark.parametrize(
        ["test_case_name", "expected_url"],
        [
            ("oidc_https", HTTPS_SL_URL),
        ],
    )
    def test_oidc_https(self, timeout, retries, test_case_name, debug_caplog, request, expected_url, mock_stk):
        test_case = request.getfixturevalue(test_case_name)
        kwargs = self._kwargs(timeout, retries)
        _ = test_case.dataflow_integration.get_scripting_toolkit_session(**kwargs)

        mock_stk.SessionConfiguration.assert_called_once_with()
        session_configuration_instance = mock_stk.SessionConfiguration.return_value
        self.check_session_config(session_configuration_instance, timeout, retries)
        mock_stk.SessionBuilder.assert_called_once_with(
            expected_url, session_configuration=session_configuration_instance
        )
        builder_instance = mock_stk.SessionBuilder.return_value
        builder_instance.with_oidc.assert_called_once()
        oidc_builder_instance = builder_instance.with_oidc.return_value
        oidc_builder_instance.with_access_token.assert_called_once_with(token=access_token)

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using OIDC authentication." in debug_caplog.text

    def _kwargs(self, timeout, retries):
        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout
        if retries is not None:
            kwargs["max_retries"] = retries
        return kwargs

    def check_session_config(self, session_config, timeout: int | None, retries: int | None):
        if timeout is not None:
            assert session_config.timeout == timeout
        else:
            # Exists on the mock SessionConfiguration but nothing verifiable about it, i.e. is the default value
            # implemented in the class
            assert isinstance(session_config.timeout, NonCallableMagicMock)
        if retries is not None:
            assert session_config.max_retries == retries
        else:
            assert isinstance(session_config.max_retries, NonCallableMagicMock)


class TestDeprecatedScriptingToolkit:
    warning_message = r"This method is deprecated\. Use 'get_scripting_toolkit_session\(\)' instead\."

    @pytest.mark.parametrize(
        ["test_case_name", "expected_url"],
        [
            ("windows_https", HTTPS_SL_URL),
            ("windows_http", HTTP_SL_URL),
            ("basic_https", HTTPS_SL_URL),
            ("basic_http", HTTP_SL_URL),
            ("oidc_https", HTTPS_SL_URL),
        ],
    )
    def test_deprecated_property(
        self, windows_https, debug_caplog, mock_stk, request, test_case_name, expected_url, monkeypatch
    ):
        test_case = request.getfixturevalue(test_case_name)

        mock_v5_method = Mock()
        monkeypatch.setattr(
            MIDataflowIntegration, "_start_stk_session_from_dataflow_credentials_with_session_builder", mock_v5_method
        )

        with pytest.warns(match=self.warning_message):
            _ = test_case.dataflow_integration.mi_session

        mock_v5_method.assert_called_once_with(timeout=None, max_retries=None)


def _scripting_toolkit_logged(log):
    return "Creating MI Scripting Toolkit session." in log
