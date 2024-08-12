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

import json
from pathlib import Path
import sys
from typing import Literal

import pytest

from ansys.grantami.dataflow_toolkit import MIDataflowIntegration
from common import (
    CERT_FILE,
    CERT_PATH,
    HTTP_SL_URL,
    HTTP_URL,
    HTTPS_SL_URL,
    HTTPS_URL,
    TRANSITION_NAME,
    WORKFLOW_DEFINITION_ID,
    WORKFLOW_ID,
    basic_header,
    payloads,
)

# TODO: Test OIDC


class TestInstantiation:
    @pytest.mark.parametrize("payload", [payloads.basic_https, payloads.windows_https])
    @pytest.mark.parametrize("use_https", [True, False])
    @pytest.mark.parametrize("verify_ssl", [True, False])
    @pytest.mark.parametrize("certificate_filename", [None, CERT_FILE])
    def test_https(self, payload, use_https, verify_ssl, certificate_filename, caplog):
        df = MIDataflowIntegration.from_static_payload(
            payload,
            use_https=use_https,
            verify_ssl=verify_ssl,
            certificate_filename=certificate_filename,
        )

        assert df.df_data == payload
        assert self._payload_logged(payload, caplog.text)

        assert self._url_elements_logged(caplog.text)

        assert df._https_enabled is use_https
        assert not ("HTTPS is not enabled. Using plain HTTP." in caplog.text) is use_https

        ssl_verify_enabled = use_https and verify_ssl
        assert df._verify_ssl is ssl_verify_enabled
        if ssl_verify_enabled:
            assert "Certificate verification is disabled." not in caplog.text
        elif use_https:
            assert "Certificate verification is disabled" in caplog.text

        if use_https and verify_ssl and certificate_filename:
            assert df._ca_path == CERT_PATH
            assert f'CA certificate filename "{CERT_FILE}" provided.' in caplog.text
            assert f'Successfully resolved file "{CERT_PATH}"' in caplog.text
        else:
            assert df._ca_path is None

    @pytest.mark.parametrize("payload", [payloads.basic_https, payloads.windows_https])
    def test_https_missing_cert_raises_error(self, payload, caplog):
        with pytest.raises(FileNotFoundError, match='"my_missing_cert.crt"'):
            MIDataflowIntegration.from_static_payload(
                payload,
                certificate_filename="my_missing_cert.crt",
            )
        assert 'CA certificate filename "my_missing_cert.crt" provided.' in caplog.text

    @pytest.mark.parametrize("payload", [payloads.basic_http, payloads.windows_http])
    def test_http(self, payload, caplog):
        df = MIDataflowIntegration.from_static_payload(payload, use_https=False)
        assert df.df_data == payload
        assert self._payload_logged(payload, caplog.text)
        assert self._url_elements_logged(caplog.text)
        assert "HTTPS is not enabled. Using plain HTTP." in caplog.text

    @pytest.mark.parametrize("payload", [payloads.basic_http, payloads.windows_http])
    def test_http_in_https_mode_raises_warning(self, payload, caplog):
        with pytest.warns(UserWarning, match='"use_https" is set to True'):
            MIDataflowIntegration.from_static_payload(payload)
        assert self._payload_logged(payload, caplog.text)
        assert self._url_elements_logged(caplog.text)
        assert "HTTPS is not enabled. Using plain HTTP." in caplog.text

    def _payload_logged(self, payload, log):
        return json.dumps(payload) in log

    def _url_elements_logged(self, log):
        hostname_logged = 'Data Flow hostname: "my_server_name"' in log
        path_logged = 'Data Flow path: "/mi_dataflow"' in log
        return hostname_logged and path_logged


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


@pytest.mark.parametrize("return_code", [0, 1, "-42"])
class TestResumeBookmark:
    def test_windows_https(self, requests_mock, windows_https, return_code, caplog):
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        windows_https.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code)
        assert self._resume_bookmark_logged(caplog.text, return_code)

    def test_windows_https_disable_https(self, requests_mock, return_code, caplog):
        df = MIDataflowIntegration.from_static_payload(payloads.windows_https, use_https=False)
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False)
        assert self._resume_bookmark_logged(caplog.text, return_code, https=False)

    def test_windows_https_disable_verification(self, requests_mock, return_code, caplog):
        df = MIDataflowIntegration.from_static_payload(payloads.windows_https, verify_ssl=False)
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=False)
        assert self._resume_bookmark_logged(caplog.text, return_code)

    def test_windows_https_custom_cert(self, requests_mock, return_code, caplog):
        df = MIDataflowIntegration.from_static_payload(
            payloads.windows_https, certificate_filename=__file__
        )
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=Path(__file__))
        assert self._resume_bookmark_logged(caplog.text, return_code)

    def test_windows_http(self, requests_mock, windows_http, return_code, caplog):
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        windows_http.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False)
        assert self._resume_bookmark_logged(caplog.text, return_code, https=False)

    def test_basic_https(self, requests_mock, basic_https, return_code, caplog):
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        basic_https.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, auth="basic")
        assert self._resume_bookmark_logged(caplog.text, return_code)

    def test_basic_https_disable_https(self, requests_mock, return_code, caplog):
        df = MIDataflowIntegration.from_static_payload(payloads.basic_https, use_https=False)
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False, auth="basic")
        assert self._resume_bookmark_logged(caplog.text, return_code, https=False)

    def test_basic_https_disable_verification(self, requests_mock, return_code, caplog):
        df = MIDataflowIntegration.from_static_payload(payloads.basic_https, verify_ssl=False)
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=False, auth="basic")
        assert self._resume_bookmark_logged(caplog.text, return_code)

    def test_basic_https_custom_cert(self, requests_mock, return_code, caplog):
        df = MIDataflowIntegration.from_static_payload(
            payloads.basic_https, certificate_filename=__file__
        )
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=Path(__file__), auth="basic")
        assert self._resume_bookmark_logged(caplog.text, return_code)

    def test_basic_http(self, requests_mock, basic_http, return_code, caplog):
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        basic_http.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False, auth="basic")
        assert self._resume_bookmark_logged(caplog.text, return_code, https=False)

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

    def _resume_bookmark_logged(self, log, exit_code, https=True):
        exit_code_logged = f"Returning control to MI Data Flow with exit code {exit_code}" in log
        url_logged = f"Resuming bookmark using URL {HTTPS_URL if https else HTTP_URL}"
        return exit_code_logged and url_logged


@pytest.mark.parametrize(
    "fixture_name", ["basic_http", "basic_https", "windows_http", "windows_https"]
)
def test_supporting_files(fixture_name, request):
    df = request.getfixturevalue(fixture_name)
    assert df.supporting_files_dir == Path(sys.path[0])
