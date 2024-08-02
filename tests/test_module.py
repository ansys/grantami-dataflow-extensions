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

from pathlib import Path
from typing import Literal
from unittest.mock import patch

from ansys.grantami.recordlists import Connection as RecordListConnection
import pytest

from ansys.grantami.dataflow_toolkit import MIDataflowIntegration
from common import (
    HTTP_SL_URL,
    HTTP_URL,
    HTTPS_SL_URL,
    HTTPS_URL,
    PASSWORD,
    TRANSITION_NAME,
    USERNAME,
    WORKFLOW_DEFINITION_ID,
    WORKFLOW_ID,
    basic_header,
    payloads,
)
from mocks.scripting_toolkit import mpy as mpy_mock

# TODO: Test logging
# TODO: Test OIDC
# TODO: Test resume bookmark


class TestInstantiation:
    @pytest.mark.parametrize("payload", [payloads.basic_https, payloads.windows_https])
    @pytest.mark.parametrize("use_https", [True, False])
    @pytest.mark.parametrize("verify_ssl", [True, False])
    @pytest.mark.parametrize("certificate_filename", [None, __file__])
    def test_https(self, payload, use_https, verify_ssl, certificate_filename):
        df = MIDataflowIntegration.from_static_payload(
            payload,
            use_https=use_https,
            verify_ssl=verify_ssl,
            certificate_filename=certificate_filename,
        )
        assert df.df_data == payload
        assert df._https_enabled is use_https
        assert df._verify_ssl is (use_https and verify_ssl)
        if use_https and verify_ssl and certificate_filename:
            assert df._ca_path == Path(__file__)
        else:
            assert df._ca_path is None

    @pytest.mark.parametrize("payload", [payloads.basic_https, payloads.windows_https])
    def test_https_missing_cert_raises_error(self, payload):
        with pytest.raises(FileNotFoundError, match='"my_missing_cert.crt"'):
            MIDataflowIntegration.from_static_payload(
                payload,
                certificate_filename="my_missing_cert.crt",
            )

    @pytest.mark.parametrize("payload", [payloads.basic_http, payloads.windows_http])
    def test_http(self, payload):
        df = MIDataflowIntegration.from_static_payload(payload, use_https=False)
        assert df.df_data == payload

    @pytest.mark.parametrize("payload", [payloads.basic_http, payloads.windows_http])
    def test_http_in_https_mode_raises_warning(self, payload):
        with pytest.warns(UserWarning, match='"use_https" is set to True'):
            MIDataflowIntegration.from_static_payload(payload)


class TestURLs:
    @pytest.mark.parametrize("fixture_name", ["windows_https", "basic_https"])
    def test_service_layer_url_https(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name)
        assert df.service_layer_url == HTTPS_SL_URL

    @pytest.mark.parametrize("fixture_name", ["windows_http", "basic_http"])
    def test_service_layer_url_http(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name)
        assert df.service_layer_url == HTTP_SL_URL

    @pytest.mark.parametrize("fixture_name", ["windows_https", "basic_https"])
    def test_dataflow_url_https(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name)
        assert df._dataflow_url == HTTPS_URL

    @pytest.mark.parametrize("fixture_name", ["windows_http", "basic_http"])
    def test_service_layer_url_http(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name)
        assert df._dataflow_url == HTTP_URL


class TestScriptingToolkitSession:
    def test_windows_https(self, windows_https):
        mpy_mock.connect.reset_mock()
        _ = windows_https.mi_session
        mpy_mock.connect.assert_called_once_with(
            HTTPS_SL_URL,
            autologon=True,
        )

    def test_windows_http(self, windows_http):
        mpy_mock.connect.reset_mock()
        _ = windows_http.mi_session
        mpy_mock.connect.assert_called_once_with(
            HTTP_SL_URL,
            autologon=True,
        )

    def test_basic_https(self, basic_https):
        mpy_mock.connect.reset_mock()
        _ = basic_https.mi_session
        mpy_mock.connect.assert_called_once_with(
            HTTPS_SL_URL,
            user_name=USERNAME,
            password=PASSWORD,
        )

    def test_basic_http(self, basic_http):
        mpy_mock.connect.reset_mock()
        _ = basic_http.mi_session
        mpy_mock.connect.assert_called_once_with(
            HTTP_SL_URL,
            user_name=USERNAME,
            password=PASSWORD,
        )

    @pytest.mark.parametrize("fixture_name", ["digest_http", "digest_https"])
    def test_unknown_creds_raises_exception(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name)
        with pytest.raises(NotImplementedError, match='Unknown credentials type "digest"'):
            _ = df.mi_session


class TestPyGrantaSession:
    """
    Don't try and merge any of these test cases. The act of mocking the authentication method
    means that the completed client can no longer be returned, so we must do it with two separate
    tests.
    """

    def test_windows_https(self, windows_https):
        with patch.object(RecordListConnection, "with_autologon") as mock:
            windows_https.configure_pygranta_connection(RecordListConnection).connect()
        mock.assert_called_once_with()

    def test_windows_https_url(self, windows_https):
        client = windows_https.configure_pygranta_connection(RecordListConnection).connect()
        assert client._service_layer_url == HTTPS_SL_URL

    def test_windows_http(self, windows_http):
        with patch.object(RecordListConnection, "with_autologon") as mock:
            windows_http.configure_pygranta_connection(RecordListConnection).connect()
        mock.assert_called_once_with()

    def test_windows_http_url(self, windows_http):
        client = windows_http.configure_pygranta_connection(RecordListConnection).connect()
        assert client._service_layer_url == HTTP_SL_URL

    def test_basic_https(self, basic_https):
        with patch.object(RecordListConnection, "with_credentials") as mock:
            basic_https.configure_pygranta_connection(RecordListConnection).connect()
        mock.assert_called_once_with(
            username=USERNAME,
            password=PASSWORD,
        )

    def test_basic_https_url(self, basic_https):
        client = basic_https.configure_pygranta_connection(RecordListConnection).connect()
        assert client._service_layer_url == HTTPS_SL_URL

    def test_basic_http(self, basic_http):
        with patch.object(RecordListConnection, "with_credentials") as mock:
            basic_http.configure_pygranta_connection(RecordListConnection).connect()
        mock.assert_called_once_with(
            username=USERNAME,
            password=PASSWORD,
        )

    def test_basic_http_url(self, basic_http):
        client = basic_http.configure_pygranta_connection(RecordListConnection).connect()
        assert client._service_layer_url == HTTP_SL_URL

    @pytest.mark.parametrize("fixture_name", ["digest_http", "digest_https"])
    def test_unknown_creds_raises_exception(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name)
        with pytest.raises(NotImplementedError, match='Unknown credentials type "digest"'):
            _ = df.configure_pygranta_connection(RecordListConnection)

    def test_invalid_class_raises_exception(self, windows_https):
        with pytest.raises(TypeError, match='"pygranta_connection_class" must be a subclass'):
            _ = windows_https.configure_pygranta_connection(str)


@pytest.mark.parametrize("return_code", [0, 1, "-42"])
class TestResumeBookmark:
    def test_windows_https(self, requests_mock, windows_https, return_code):
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        windows_https.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code)

    def test_windows_https_disable_https(self, requests_mock, return_code):
        df = MIDataflowIntegration.from_static_payload(payloads.windows_https, use_https=False)
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False)

    def test_windows_https_disable_verification(self, requests_mock, return_code):
        df = MIDataflowIntegration.from_static_payload(payloads.windows_https, verify_ssl=False)
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=False)

    def test_windows_https_custom_cert(self, requests_mock, return_code):
        df = MIDataflowIntegration.from_static_payload(
            payloads.windows_https, certificate_filename=__file__
        )
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=Path(__file__))

    def test_windows_http(self, requests_mock, windows_http, return_code):
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        windows_http.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False)

    def test_basic_https(self, requests_mock, basic_https, return_code):
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        basic_https.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, auth="basic")

    def test_basic_https_disable_https(self, requests_mock, return_code):
        df = MIDataflowIntegration.from_static_payload(payloads.basic_https, use_https=False)
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False, auth="basic")

    def test_basic_https_disable_verification(self, requests_mock, return_code):
        df = MIDataflowIntegration.from_static_payload(payloads.basic_https, verify_ssl=False)
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=False, auth="basic")

    def test_basic_https_custom_cert(self, requests_mock, return_code):
        df = MIDataflowIntegration.from_static_payload(
            payloads.basic_https, certificate_filename=__file__
        )
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=Path(__file__), auth="basic")

    def test_basic_http(self, requests_mock, basic_http, return_code):
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        basic_http.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False, auth="basic")

    def _verify_request(
        self,
        request,
        return_code: int | str,
        *,
        https: bool = True,
        verify: bool | str = True,
        auth: Literal["basic", "oidc"] | None = None,
    ):
        assert request.scheme == "https" if https else "http"
        assert request.verify == verify
        if auth == "basic":
            assert request.headers["Authorization"] == basic_header
        data = request.json()
        assert data["Values"]["ExitCode"] == return_code
        assert data["WorkflowDefinitionName"] == WORKFLOW_DEFINITION_ID
        assert data["TransitionName"] == TRANSITION_NAME
