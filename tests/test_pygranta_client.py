# Copyright (C) 2025 ANSYS, Inc. and/or its affiliates.
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

from unittest.mock import MagicMock, patch

from ansys.grantami.recordlists import Connection as RecordListConnection
from ansys.openapi.common import OIDCSessionBuilder, SessionConfiguration
from common import CERT_PATH_ABSOLUTE, HTTP_SL_URL, HTTPS_SL_URL, PASSWORD, USERNAME, access_token
import pytest

# Don't try and merge a test with its associated '_url' test. The act of mocking the
# authentication method means that the completed client can no longer be returned,
# so it's not possible to both observe the URL in the completed client AND check the
# arguments it was created with. We must do it with two separate tests.


class TestClientWithDefaultConfiguration:
    def test_windows_https(self, windows_https, debug_caplog):
        with patch.object(RecordListConnection, "with_autologon") as mock:
            windows_https.dataflow_integration.configure_pygranta_connection(RecordListConnection).connect()
        mock.assert_called_once_with()
        assert _pygranta_client_logged(debug_caplog.text)
        assert "Using Windows authentication." in debug_caplog.text

    def test_windows_https_url(self, windows_https):
        client = windows_https.dataflow_integration.configure_pygranta_connection(RecordListConnection).connect()
        assert client._service_layer_url == HTTPS_SL_URL

    def test_windows_http(self, windows_http, debug_caplog):
        with patch.object(RecordListConnection, "with_autologon") as mock:
            windows_http.dataflow_integration.configure_pygranta_connection(RecordListConnection).connect()
        mock.assert_called_once_with()
        assert _pygranta_client_logged(debug_caplog.text)
        assert "Using Windows authentication." in debug_caplog.text

    def test_windows_http_url(self, windows_http):
        client = windows_http.dataflow_integration.configure_pygranta_connection(RecordListConnection).connect()
        assert client._service_layer_url == HTTP_SL_URL

    def test_basic_https(self, basic_https, debug_caplog):
        with patch.object(RecordListConnection, "with_credentials") as mock:
            basic_https.dataflow_integration.configure_pygranta_connection(RecordListConnection).connect()
        mock.assert_called_once_with(
            username=USERNAME,
            password=PASSWORD,
        )
        assert _pygranta_client_logged(debug_caplog.text)
        assert "Using Basic authentication." in debug_caplog.text

    def test_basic_https_url(self, basic_https):
        client = basic_https.dataflow_integration.configure_pygranta_connection(RecordListConnection).connect()
        assert client._service_layer_url == HTTPS_SL_URL

    def test_basic_http(self, basic_http, debug_caplog):
        with patch.object(RecordListConnection, "with_credentials") as mock:
            basic_http.dataflow_integration.configure_pygranta_connection(RecordListConnection).connect()
        mock.assert_called_once_with(
            username=USERNAME,
            password=PASSWORD,
        )
        assert _pygranta_client_logged(debug_caplog.text)
        assert "Using Basic authentication." in debug_caplog.text

    def test_basic_http_url(self, basic_http):
        client = basic_http.dataflow_integration.configure_pygranta_connection(RecordListConnection).connect()
        assert client._service_layer_url == HTTP_SL_URL

    def test_oidc_https(self, oidc_https, debug_caplog):
        with patch.object(RecordListConnection, "with_oidc") as mock:
            oidc_https.dataflow_integration.configure_pygranta_connection(RecordListConnection).connect()
        mock.assert_called_once_with()
        assert _pygranta_client_logged(debug_caplog.text)
        assert "Using OIDC authentication." in debug_caplog.text

    def test_oidc_https_auth_token(self, oidc_https, debug_caplog):
        oidc_builder = MagicMock(spec_set=OIDCSessionBuilder)
        with_oidc_mock = MagicMock(return_value=oidc_builder)

        with patch("ansys.openapi.common.ApiClientFactory.with_oidc", with_oidc_mock):
            oidc_https.dataflow_integration.configure_pygranta_connection(RecordListConnection).connect()
        oidc_builder.with_access_token.assert_called_once_with(access_token=access_token)

    def test_oidc_raises_exception(self, oidc_https, debug_caplog):
        with pytest.raises(NotImplementedError, match="OIDC authentication is not supported with PyGranta packages"):
            oidc_https.dataflow_integration.configure_pygranta_connection(RecordListConnection).connect()

    def test_invalid_class_raises_exception(self, windows_https):
        with pytest.raises(TypeError, match='"pygranta_connection_class" must be a subclass'):
            _ = windows_https.dataflow_integration.configure_pygranta_connection(str)


def _autologon_override(self) -> SessionConfiguration:
    # Mock the autologon builder method to return the session configuration active when it is called
    return self._session_configuration


class TestClientWithCustomConfiguration:
    def test_default_config_is_used_if_not_provided(self, windows_https_custom_cert, debug_caplog):
        with patch.object(RecordListConnection, "with_autologon", _autologon_override):
            config_result = windows_https_custom_cert.dataflow_integration.configure_pygranta_connection(
                RecordListConnection,
            )

        assert config_result.verify_ssl is True
        assert config_result.cert_store_path == str(CERT_PATH_ABSOLUTE)

    def test_provided_config_is_used_if_provided(self, windows_https_custom_cert, debug_caplog):
        config = SessionConfiguration(max_redirects=10, retry_count=5, request_timeout=50)

        with patch.object(RecordListConnection, "with_autologon", _autologon_override):
            config_result = windows_https_custom_cert.dataflow_integration.configure_pygranta_connection(
                RecordListConnection,
                config,
            )

        assert config_result.max_redirects == 10
        assert config_result.retry_count == 5
        assert config_result.request_timeout == 50

        assert config_result.verify_ssl is True
        assert config_result.cert_store_path == str(CERT_PATH_ABSOLUTE)

    def test_verify_ssl_is_overridden_if_provided(self, windows_https_custom_cert, debug_caplog):
        config = SessionConfiguration(verify_ssl=False, request_timeout=50)

        with patch.object(RecordListConnection, "with_autologon", _autologon_override):
            config_result = windows_https_custom_cert.dataflow_integration.configure_pygranta_connection(
                RecordListConnection,
                config,
            )

        assert config_result.verify_ssl is True
        assert config_result.cert_store_path == str(CERT_PATH_ABSOLUTE)
        assert config_result.request_timeout == 50

    def test_ca_cert_is_overridden_if_provided(self, windows_https_custom_cert, debug_caplog):
        config = SessionConfiguration(cert_store_path="/home/user/cert.cer", request_timeout=50)

        with patch.object(RecordListConnection, "with_autologon", _autologon_override):
            config_result = windows_https_custom_cert.dataflow_integration.configure_pygranta_connection(
                RecordListConnection,
                config,
            )

        assert config_result.verify_ssl is True
        assert config_result.cert_store_path == str(CERT_PATH_ABSOLUTE)
        assert config_result.request_timeout == 50


def _pygranta_client_logged(log):
    return "Creating PyGranta client." in log
