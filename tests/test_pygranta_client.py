# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

from unittest.mock import patch

from ansys.grantami.recordlists import Connection as RecordListConnection
import pytest

from common import HTTP_SL_URL, HTTPS_SL_URL, PASSWORD, USERNAME

# Don't try and merge a test with its associated '_url' test. The act of mocking the authentication method
# means that the completed client can no longer be returned, so it's not possible to both observe the URL in
# the completed client AND check the arguments it was created with. We must do it with two separate tests.


def test_windows_https(windows_https, debug_caplog):
    with patch.object(RecordListConnection, "with_autologon") as mock:
        windows_https.dataflow_integration.configure_pygranta_connection(
            RecordListConnection
        ).connect()
    mock.assert_called_once_with()
    assert _pygranta_client_logged(debug_caplog.text)
    assert "Using Windows authentication." in debug_caplog.text


def test_windows_https_url(windows_https):
    client = windows_https.dataflow_integration.configure_pygranta_connection(
        RecordListConnection
    ).connect()
    assert client._service_layer_url == HTTPS_SL_URL


def test_windows_http(windows_http, debug_caplog):
    with patch.object(RecordListConnection, "with_autologon") as mock:
        windows_http.dataflow_integration.configure_pygranta_connection(
            RecordListConnection
        ).connect()
    mock.assert_called_once_with()
    assert _pygranta_client_logged(debug_caplog.text)
    assert "Using Windows authentication." in debug_caplog.text


def test_windows_http_url(windows_http):
    client = windows_http.dataflow_integration.configure_pygranta_connection(
        RecordListConnection
    ).connect()
    assert client._service_layer_url == HTTP_SL_URL


def test_basic_https(basic_https, debug_caplog):
    with patch.object(RecordListConnection, "with_credentials") as mock:
        basic_https.dataflow_integration.configure_pygranta_connection(
            RecordListConnection
        ).connect()
    mock.assert_called_once_with(
        username=USERNAME,
        password=PASSWORD,
    )
    assert _pygranta_client_logged(debug_caplog.text)
    assert "Using Basic authentication." in debug_caplog.text


def test_basic_https_url(basic_https):
    client = basic_https.dataflow_integration.configure_pygranta_connection(
        RecordListConnection
    ).connect()
    assert client._service_layer_url == HTTPS_SL_URL


def test_basic_http(basic_http, debug_caplog):
    with patch.object(RecordListConnection, "with_credentials") as mock:
        basic_http.dataflow_integration.configure_pygranta_connection(
            RecordListConnection
        ).connect()
    mock.assert_called_once_with(
        username=USERNAME,
        password=PASSWORD,
    )
    assert _pygranta_client_logged(debug_caplog.text)
    assert "Using Basic authentication." in debug_caplog.text


def test_basic_http_url(basic_http):
    client = basic_http.dataflow_integration.configure_pygranta_connection(
        RecordListConnection
    ).connect()
    assert client._service_layer_url == HTTP_SL_URL


def test_oidc_raises_exception(oidc_https, debug_caplog):
    with pytest.raises(
        NotImplementedError, match="OIDC authentication is not supported with PyGranta packages"
    ):
        oidc_https.dataflow_integration.configure_pygranta_connection(
            RecordListConnection
        ).connect()


def test_invalid_class_raises_exception(windows_https):
    with pytest.raises(TypeError, match='"pygranta_connection_class" must be a subclass'):
        _ = windows_https.dataflow_integration.configure_pygranta_connection(str)


def _pygranta_client_logged(log):
    return "Creating PyGranta client." in log
