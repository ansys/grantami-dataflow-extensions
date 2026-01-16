# Copyright (C) 2025 - 2026 ANSYS, Inc. and/or its affiliates.
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

from unittest.mock import ANY

from common import HTTP_SL_URL, HTTPS_SL_URL, PASSWORD, USERNAME, access_token
from mocks.scripting_toolkit import (
    OIDCSessionBuilder,
    SessionBuilder,
    SessionConfiguration,
    _SessionBuilder,
)
import pytest

timeout_params = pytest.mark.parametrize("timeout", [None, 1_000_000])
max_retries_params = pytest.mark.parametrize("retries", [None, 10])

pytestmark = pytest.mark.scripting_toolkit_version("latest")


def _reset_mocks():
    """Reset all mocks before each test."""
    SessionBuilder.reset_mock()
    SessionConfiguration.reset_mock()
    _SessionBuilder.with_autologon.reset_mock()
    _SessionBuilder.with_credentials.reset_mock()
    _SessionBuilder.with_oidc.reset_mock()
    OIDCSessionBuilder.with_access_token.reset_mock()


@timeout_params
@max_retries_params
class TestScriptingToolkitSession:
    def test_windows_https(self, timeout, retries, windows_https, debug_caplog):
        _reset_mocks()
        kwargs = self._kwargs(timeout, retries)
        _ = windows_https.dataflow_integration.get_scripting_toolkit_session(**kwargs)

        SessionConfiguration.assert_called_once_with(
            timeout=timeout,
            max_retries=retries,
        )
        SessionBuilder.assert_called_once_with(HTTPS_SL_URL, session_configuration=ANY)
        _SessionBuilder.with_autologon.assert_called_once()

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using Windows authentication." in debug_caplog.text

    def test_windows_http(self, timeout, retries, windows_http, debug_caplog):
        _reset_mocks()
        kwargs = self._kwargs(timeout, retries)
        _ = windows_http.dataflow_integration.get_scripting_toolkit_session(**kwargs)

        SessionConfiguration.assert_called_once_with(
            timeout=timeout,
            max_retries=retries,
        )
        SessionBuilder.assert_called_once_with(HTTP_SL_URL, session_configuration=ANY)
        _SessionBuilder.with_autologon.assert_called_once()

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using Windows authentication." in debug_caplog.text

    def test_basic_https(self, timeout, retries, basic_https, debug_caplog):
        _reset_mocks()
        kwargs = self._kwargs(timeout, retries)
        _ = basic_https.dataflow_integration.get_scripting_toolkit_session(**kwargs)

        SessionConfiguration.assert_called_once_with(
            timeout=timeout,
            max_retries=retries,
        )
        SessionBuilder.assert_called_once_with(HTTPS_SL_URL, session_configuration=ANY)
        _SessionBuilder.with_credentials.assert_called_once_with(
            username=USERNAME,
            password=PASSWORD,
        )

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using Basic authentication." in debug_caplog.text

    def test_basic_http(self, timeout, retries, basic_http, debug_caplog):
        _reset_mocks()
        kwargs = self._kwargs(timeout, retries)
        _ = basic_http.dataflow_integration.get_scripting_toolkit_session(**kwargs)

        SessionConfiguration.assert_called_once_with(
            timeout=timeout,
            max_retries=retries,
        )
        SessionBuilder.assert_called_once_with(HTTP_SL_URL, session_configuration=ANY)
        _SessionBuilder.with_credentials.assert_called_once_with(
            username=USERNAME,
            password=PASSWORD,
        )

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using Basic authentication." in debug_caplog.text

    def test_oidc_https(self, timeout, retries, oidc_https, debug_caplog):
        _reset_mocks()
        kwargs = self._kwargs(timeout, retries)
        _ = oidc_https.dataflow_integration.get_scripting_toolkit_session(**kwargs)

        SessionConfiguration.assert_called_once_with(
            timeout=timeout,
            max_retries=retries,
        )
        SessionBuilder.assert_called_once_with(HTTPS_SL_URL, session_configuration=ANY)
        _SessionBuilder.with_oidc.assert_called_once()
        OIDCSessionBuilder.with_access_token.assert_called_once_with(token=access_token)

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

    def test_windows_https_deprecated_property(self, windows_https, debug_caplog):
        _reset_mocks()
        with pytest.warns(match=self.warning_message):
            _ = windows_https.dataflow_integration.mi_session

        SessionBuilder.assert_called_once_with(HTTPS_SL_URL, session_configuration=ANY)
        _SessionBuilder.with_autologon.assert_called_once()

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using Windows authentication." in debug_caplog.text

    def test_windows_http(self, windows_http, debug_caplog):
        _reset_mocks()
        with pytest.warns(match=self.warning_message):
            _ = windows_http.dataflow_integration.mi_session

        SessionBuilder.assert_called_once_with(HTTP_SL_URL, session_configuration=ANY)
        _SessionBuilder.with_autologon.assert_called_once()

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using Windows authentication." in debug_caplog.text

    def test_basic_https(self, basic_https, debug_caplog):
        _reset_mocks()
        with pytest.warns(match=self.warning_message):
            _ = basic_https.dataflow_integration.mi_session

        SessionBuilder.assert_called_once_with(HTTPS_SL_URL, session_configuration=ANY)
        _SessionBuilder.with_credentials.assert_called_once_with(
            username=USERNAME,
            password=PASSWORD,
        )

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using Basic authentication." in debug_caplog.text

    def test_basic_http(self, basic_http, debug_caplog):
        _reset_mocks()
        with pytest.warns(match=self.warning_message):
            _ = basic_http.dataflow_integration.mi_session

        SessionBuilder.assert_called_once_with(HTTP_SL_URL, session_configuration=ANY)
        _SessionBuilder.with_credentials.assert_called_once_with(
            username=USERNAME,
            password=PASSWORD,
        )

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using Basic authentication." in debug_caplog.text

    def test_oidc_https(self, oidc_https, debug_caplog):
        _reset_mocks()
        with pytest.warns(match=self.warning_message):
            _ = oidc_https.dataflow_integration.mi_session

        SessionBuilder.assert_called_once_with(HTTPS_SL_URL, session_configuration=ANY)
        _SessionBuilder.with_oidc.assert_called_once()
        OIDCSessionBuilder.with_access_token.assert_called_once_with(token=access_token)

        assert _scripting_toolkit_logged(debug_caplog.text)
        assert "Using OIDC authentication." in debug_caplog.text


def _scripting_toolkit_logged(log):
    return "Creating MI Scripting Toolkit session." in log
