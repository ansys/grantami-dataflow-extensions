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

from common import HTTP_SL_URL, HTTPS_SL_URL, PASSWORD, USERNAME, access_token
from mocks.scripting_toolkit import mpy as mpy_mock


def test_windows_https(windows_https, debug_caplog):
    mpy_mock.connect.reset_mock()
    _ = windows_https.mi_session
    mpy_mock.connect.assert_called_once_with(
        HTTPS_SL_URL,
        autologon=True,
    )
    assert _scripting_toolkit_logged(debug_caplog.text)
    assert "Using Windows authentication." in debug_caplog.text


def test_windows_http(windows_http, debug_caplog):
    mpy_mock.connect.reset_mock()
    _ = windows_http.mi_session
    mpy_mock.connect.assert_called_once_with(
        HTTP_SL_URL,
        autologon=True,
    )
    assert _scripting_toolkit_logged(debug_caplog.text)
    assert "Using Windows authentication." in debug_caplog.text


def test_basic_https(basic_https, debug_caplog):
    mpy_mock.connect.reset_mock()
    _ = basic_https.mi_session
    mpy_mock.connect.assert_called_once_with(
        HTTPS_SL_URL,
        user_name=USERNAME,
        password=PASSWORD,
    )
    assert _scripting_toolkit_logged(debug_caplog.text)
    assert "Using Basic authentication." in debug_caplog.text


def test_basic_http(basic_http, debug_caplog):
    mpy_mock.connect.reset_mock()
    _ = basic_http.mi_session
    mpy_mock.connect.assert_called_once_with(
        HTTP_SL_URL,
        user_name=USERNAME,
        password=PASSWORD,
    )
    assert _scripting_toolkit_logged(debug_caplog.text)
    assert "Using Basic authentication." in debug_caplog.text


def test_oidc_https(oidc_https, debug_caplog):
    mpy_mock.connect.reset_mock()
    _ = oidc_https.mi_session
    mpy_mock.connect.assert_called_once_with(
        HTTPS_SL_URL,
        oidc=True,
        auth_token=access_token,
    )
    assert _scripting_toolkit_logged(debug_caplog.text)
    assert "Using OIDC authentication." in debug_caplog.text


def _scripting_toolkit_logged(log):
    return "Creating MI Scripting Toolkit session." in log
