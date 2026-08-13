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


from unittest.mock import Mock, create_autospec

from common import HTTP_SL_URL, HTTPS_SL_URL, PASSWORD, USERNAME, access_token
import pytest

from ansys.grantami.dataflow_extensions import MIDataflowIntegration
from mocks import scripting_toolkit_4_x


@pytest.fixture
def mock_stk(monkeypatch):
    mock_module = create_autospec(
        spec=scripting_toolkit_4_x.module.granta,
        spec_set=True,
    )
    # __version__ isn't supported by MagicMock, patch it again
    mock_module.__version__ = scripting_toolkit_4_x.VERSION
    monkeypatch.setattr("ansys.grantami.dataflow_extensions._mi_dataflow.mpy", mock_module)
    return mock_module


def test_strict_interface_usage(mock_stk):
    with pytest.raises(Exception):
        mock_stk.non_existent()

    with pytest.raises(Exception):
        mock_stk.connect(non_existent="value")


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
        test_case = request.getfixturevalue(test_case_name)
        kwargs = self._kwargs(timeout, retries)
        _ = test_case.dataflow_integration.get_scripting_toolkit_session(**kwargs)
        mock_stk.connect.assert_called_once_with(
            expected_url,
            autologon=True,
            **kwargs,
        )
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
        mock_stk.connect.assert_called_once_with(
            expected_url,
            user_name=USERNAME,
            password=PASSWORD,
            **kwargs,
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
        mock_stk.connect.assert_called_once_with(
            HTTPS_SL_URL,
            oidc=True,
            auth_token=access_token,
            **kwargs,
        )
        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using OIDC authentication." in debug_caplog.text

    def _kwargs(self, timeout, retries):
        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout
        if retries is not None:
            kwargs["max_retries"] = retries
        return kwargs


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

        mock_v4_method = Mock()
        monkeypatch.setattr(
            MIDataflowIntegration, "_start_stk_session_from_dataflow_credentials_with_connect", mock_v4_method
        )

        with pytest.warns(match=self.warning_message):
            _ = test_case.dataflow_integration.mi_session

        call_kwargs = dict(timeout=None, max_retries=None)
        mock_v4_method.assert_called_once_with(**call_kwargs)


def _scripting_toolkit_logged(log):
    return "Creating MI Scripting Toolkit session." in log
