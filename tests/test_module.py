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

from common import (
    CERT_FILE,
    CERT_PATH_ABSOLUTE,
    CERT_PATH_RELATIVE,
    HTTP_SL_URL,
    HTTP_URL,
    HTTPS_SL_URL,
    HTTPS_URL,
    TRANSITION_NAME,
    WORKFLOW_DEFINITION_ID,
    WORKFLOW_ID,
    basic_header,
    oidc_header,
)
import pytest

from ansys.grantami.dataflow_toolkit import MIDataflowIntegration


class TestInstantiationFromDict:
    @pytest.mark.parametrize("test_case_name", ["basic_https", "windows_https", "oidc_https"])
    @pytest.mark.parametrize("verify_ssl", [True, False])
    @pytest.mark.parametrize("certificate_filename", [None, CERT_FILE, CERT_PATH_ABSOLUTE, CERT_PATH_RELATIVE])
    def test_https(self, test_case_name, request, verify_ssl, certificate_filename, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        df = MIDataflowIntegration.from_dict_payload(
            test_case.payload,
            verify_ssl=verify_ssl,
            certificate_file=certificate_filename,
        )

        assert df._df_data == test_case.payload
        assert TRANSITION_NAME in debug_caplog.text

        assert self._url_elements_logged(debug_caplog.text)

        assert df._authentication_mode == test_case.auth_mode

        assert df._https_enabled is True
        assert "HTTPS is not enabled. Using plain HTTP." not in debug_caplog.text

        assert df._verify_ssl is verify_ssl
        if verify_ssl:
            assert "Certificate verification is disabled." not in debug_caplog.text
        else:
            assert "Certificate verification is disabled" in debug_caplog.text

        if verify_ssl and certificate_filename:
            assert df._ca_path == CERT_PATH_ABSOLUTE
            if isinstance(certificate_filename, Path) and certificate_filename.is_absolute():
                assert f'CA certificate absolute file path "{CERT_PATH_ABSOLUTE}" provided.' in debug_caplog.text
            elif isinstance(certificate_filename, Path) and not certificate_filename.is_absolute():
                assert f'CA certificate relative file path "{CERT_PATH_RELATIVE}" provided.' in debug_caplog.text
            else:
                assert f'CA certificate filename "{CERT_FILE}" provided.' in debug_caplog.text
            assert f'Successfully resolved file "{CERT_PATH_ABSOLUTE}"' in debug_caplog.text
        else:
            assert df._ca_path is None

    @pytest.mark.parametrize("test_case_name", ["basic_https", "windows_https"])
    @pytest.mark.parametrize("verify_ssl", [True, False])
    @pytest.mark.parametrize("certificate_filename", [None, CERT_FILE, CERT_PATH_ABSOLUTE, CERT_PATH_RELATIVE])
    def test_disable_https(self, test_case_name, request, verify_ssl, certificate_filename, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        df = MIDataflowIntegration.from_dict_payload(
            test_case.payload,
            use_https=False,
            verify_ssl=verify_ssl,
            certificate_file=certificate_filename,
        )

        assert df._df_data == test_case.payload
        assert TRANSITION_NAME in debug_caplog.text

        assert self._url_elements_logged(debug_caplog.text)
        assert df._authentication_mode == test_case.auth_mode
        assert df._https_enabled is False
        assert "HTTPS is not enabled. Using plain HTTP." in debug_caplog.text
        assert df._verify_ssl is False
        assert df._ca_path is None

    def test_oidc_disable_https_raises_exception(self, oidc_https):
        with pytest.raises(ValueError, match="HTTPS cannot be disabled when using OIDC authentication"):
            MIDataflowIntegration.from_dict_payload(
                oidc_https.payload,
                use_https=False,
            )

    @pytest.mark.parametrize("test_case_name", ["basic_https", "windows_https", "oidc_https"])
    def test_https_missing_cert_str_raises_error(self, test_case_name, request, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        with pytest.raises(FileNotFoundError, match=r'"my_missing_cert.crt"'):
            MIDataflowIntegration.from_dict_payload(
                test_case.payload,
                certificate_file="my_missing_cert.crt",
            )
        assert 'CA certificate filename "my_missing_cert.crt" provided.' in debug_caplog.text

    @pytest.mark.parametrize("test_case_name", ["basic_https", "windows_https", "oidc_https"])
    def test_https_missing_cert_relative_path_raises_error(self, test_case_name, request, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        with pytest.raises(FileNotFoundError, match=r'"my_missing_cert.crt"'):
            MIDataflowIntegration.from_dict_payload(
                test_case.payload,
                certificate_file=Path("my_missing_cert.crt"),
            )
        assert 'CA certificate relative file path "my_missing_cert.crt" provided.' in debug_caplog.text

    @pytest.mark.parametrize("test_case_name", ["basic_https", "windows_https", "oidc_https"])
    def test_https_missing_cert_absolute_path_raises_error(self, test_case_name, request, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        path = Path(__file__) / "my_missing_cert.crt"
        with pytest.raises(FileNotFoundError) as e:
            MIDataflowIntegration.from_dict_payload(
                test_case.payload,
                certificate_file=path,
            )
        assert str(path) in str(e.value)
        assert f'CA certificate absolute file path "{path}" provided.' in debug_caplog.text

    @pytest.mark.parametrize("test_case_name", ["basic_https", "windows_https", "oidc_https"])
    def test_incorrect_cert_type(self, test_case_name, request):
        test_case = request.getfixturevalue(test_case_name)
        with pytest.raises(
            TypeError,
            match=r'Argument "certificate_file" must be of type pathlib.Path or str.*float',
        ):
            MIDataflowIntegration.from_dict_payload(
                test_case.payload,
                certificate_file=123.456,
            )

    @pytest.mark.parametrize("test_case_name", ["basic_http", "windows_http"])
    def test_http(self, test_case_name, request, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        df = MIDataflowIntegration.from_dict_payload(test_case.payload, use_https=False)
        assert df._df_data == test_case.payload
        assert TRANSITION_NAME in debug_caplog.text
        assert self._url_elements_logged(debug_caplog.text)
        assert df._authentication_mode == test_case.auth_mode
        assert "HTTPS is not enabled. Using plain HTTP." in debug_caplog.text
        assert df._https_enabled is False

    def test_oidc_in_http_mode_raises_exception(self, oidc_http):
        with pytest.raises(ValueError, match="HTTPS cannot be disabled when using OIDC authentication"):
            MIDataflowIntegration.from_dict_payload(
                oidc_http.payload,
                use_https=False,
            )

    @pytest.mark.parametrize("test_case_name", ["basic_http", "windows_http"])
    def test_http_in_https_mode_raises_warning(self, test_case_name, request, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        with pytest.warns(UserWarning, match='"use_https" is set to True'):
            MIDataflowIntegration.from_dict_payload(test_case.payload)
        assert TRANSITION_NAME in debug_caplog.text
        assert self._url_elements_logged(debug_caplog.text)
        assert "HTTPS is not enabled. Using plain HTTP." in debug_caplog.text

    @pytest.mark.parametrize("test_case_name", ["digest_http", "digest_https"])
    def test_unknown_creds_raises_exception(self, test_case_name, request, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        with pytest.raises(NotImplementedError, match='Unknown ClientCredentialType "Digest"'):
            MIDataflowIntegration.from_dict_payload(test_case.payload)

    def _url_elements_logged(self, log):
        hostname_logged = 'Data Flow hostname: "my_server_name"' in log
        path_logged = 'Data Flow path: "/mi_dataflow"' in log
        return hostname_logged and path_logged

    def test_invalid_dict_raises_exception(self):
        invalid_dict = {"key": "value", "key2": "value2"}
        with pytest.raises(KeyError, match='Key "AuthorizationHeader" not found in provided payload'):
            MIDataflowIntegration.from_dict_payload(invalid_dict)
        pass


class TestInstantiationFromStr:
    @pytest.mark.parametrize("test_case_name", ["basic_https", "windows_https", "oidc_https"])
    @pytest.mark.parametrize("verify_ssl", [True, False])
    @pytest.mark.parametrize("certificate_filename", [None, CERT_FILE, CERT_PATH_ABSOLUTE, CERT_PATH_RELATIVE])
    def test_https(self, test_case_name, request, verify_ssl, certificate_filename, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        df = MIDataflowIntegration.from_string_payload(
            test_case.payload_str,
            verify_ssl=verify_ssl,
            certificate_file=certificate_filename,
        )

        assert self._payload_parsed(test_case.payload_str, df._df_data)
        assert TRANSITION_NAME in debug_caplog.text

        assert self._url_elements_logged(debug_caplog.text)

        assert df._authentication_mode == test_case.auth_mode
        assert df._https_enabled is True
        assert "HTTPS is not enabled. Using plain HTTP." not in debug_caplog.text

        assert df._verify_ssl is verify_ssl
        if verify_ssl:
            assert "Certificate verification is disabled." not in debug_caplog.text
        else:
            assert "Certificate verification is disabled" in debug_caplog.text

        if verify_ssl and certificate_filename:
            assert df._ca_path == CERT_PATH_ABSOLUTE
            if isinstance(certificate_filename, Path) and certificate_filename.is_absolute():
                assert f'CA certificate absolute file path "{CERT_PATH_ABSOLUTE}" provided.' in debug_caplog.text
            elif isinstance(certificate_filename, Path) and not certificate_filename.is_absolute():
                assert f'CA certificate relative file path "{CERT_PATH_RELATIVE}" provided.' in debug_caplog.text
            else:
                assert f'CA certificate filename "{CERT_FILE}" provided.' in debug_caplog.text
            assert f'Successfully resolved file "{CERT_PATH_ABSOLUTE}"' in debug_caplog.text
        else:
            assert df._ca_path is None

    @pytest.mark.parametrize("test_case_name", ["basic_https", "windows_https"])
    @pytest.mark.parametrize("verify_ssl", [True, False])
    @pytest.mark.parametrize("certificate_filename", [None, CERT_FILE, CERT_PATH_ABSOLUTE, CERT_PATH_RELATIVE])
    def test_disable_https(self, test_case_name, request, verify_ssl, certificate_filename, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        df = MIDataflowIntegration.from_string_payload(
            test_case.payload_str,
            use_https=False,
            verify_ssl=verify_ssl,
            certificate_file=certificate_filename,
        )

        assert self._payload_parsed(test_case.payload_str, df._df_data)
        assert TRANSITION_NAME in debug_caplog.text

        assert self._url_elements_logged(debug_caplog.text)
        assert df._authentication_mode == test_case.auth_mode
        assert df._https_enabled is False
        assert "HTTPS is not enabled. Using plain HTTP." in debug_caplog.text
        assert df._verify_ssl is False
        assert df._ca_path is None

    def test_oidc_disable_https_raises_exception(self, oidc_https):
        with pytest.raises(ValueError, match="HTTPS cannot be disabled when using OIDC authentication"):
            MIDataflowIntegration.from_string_payload(
                oidc_https.payload_str,
                use_https=False,
            )

    @pytest.mark.parametrize("test_case_name", ["basic_https", "windows_https", "oidc_https"])
    def test_https_missing_cert_raises_error(self, test_case_name, request, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        with pytest.raises(FileNotFoundError, match='"my_missing_cert.crt"'):
            MIDataflowIntegration.from_string_payload(
                test_case.payload_str,
                certificate_file="my_missing_cert.crt",
            )
        assert 'CA certificate filename "my_missing_cert.crt" provided.' in debug_caplog.text

    @pytest.mark.parametrize("test_case_name", ["basic_http", "windows_http"])
    def test_http(self, test_case_name, request, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        df = MIDataflowIntegration.from_string_payload(test_case.payload_str, use_https=False)
        assert self._payload_parsed(test_case.payload_str, df._df_data)
        assert TRANSITION_NAME in debug_caplog.text
        assert self._url_elements_logged(debug_caplog.text)
        assert df._authentication_mode == test_case.auth_mode
        assert "HTTPS is not enabled. Using plain HTTP." in debug_caplog.text
        assert df._https_enabled is False

    def test_oidc_in_http_mode_raises_exception(self, oidc_http):
        with pytest.raises(ValueError, match="HTTPS cannot be disabled when using OIDC authentication"):
            MIDataflowIntegration.from_string_payload(
                oidc_http.payload_str,
                use_https=False,
            )

    @pytest.mark.parametrize("test_case_name", ["basic_http", "windows_http"])
    def test_http_in_https_mode_raises_warning(self, test_case_name, request, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        with pytest.warns(UserWarning, match='"use_https" is set to True'):
            df = MIDataflowIntegration.from_string_payload(test_case.payload_str)
        assert TRANSITION_NAME in debug_caplog.text
        assert self._url_elements_logged(debug_caplog.text)
        assert "HTTPS is not enabled. Using plain HTTP." in debug_caplog.text
        assert df._https_enabled is False

    def test_invalid_json_raises_exception(self):
        invalid_json_syntax = "Invalid JSON"
        with pytest.raises(ValueError, match="'dataflow_payload' is not valid JSON"):
            MIDataflowIntegration.from_string_payload(invalid_json_syntax)

    def test_invalid_dict_raises_exception(self):
        invalid_json_value = '{"key": "value", "key2": "value2"}'
        with pytest.raises(KeyError, match='Key "AuthorizationHeader" not found in provided payload'):
            MIDataflowIntegration.from_string_payload(invalid_json_value)

    @pytest.mark.parametrize("test_case_name", ["digest_http", "digest_https"])
    def test_unknown_creds_raises_exception(self, test_case_name, request, debug_caplog):
        test_case = request.getfixturevalue(test_case_name)
        with pytest.raises(NotImplementedError, match='Unknown ClientCredentialType "Digest"'):
            MIDataflowIntegration.from_string_payload(test_case.payload_str)

    def _url_elements_logged(self, log):
        hostname_logged = 'Data Flow hostname: "my_server_name"' in log
        path_logged = 'Data Flow path: "/mi_dataflow"' in log
        return hostname_logged and path_logged

    def _payload_parsed(self, payload, df_data):
        return df_data == json.loads(payload)


class TestPayloadAccess:
    @pytest.mark.parametrize("fixture_name", ["windows_https", "windows_http"])
    def test_payload_auth_header_is_empty(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name).dataflow_integration
        data = df.get_payload_as_dict()
        assert not data["AuthorizationHeader"]

    @pytest.mark.parametrize("fixture_name", ["basic_https", "basic_http", "oidc_https"])
    def test_payload_auth_header_is_scrubbed(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name).dataflow_integration
        data = df.get_payload_as_dict()
        assert data["AuthorizationHeader"] == "<HeaderRemoved>"

    @pytest.mark.parametrize(
        "fixture_name", ["basic_https", "basic_http", "windows_https", "windows_http", "oidc_https"]
    )
    def test_payload_serialized_to_str(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name).dataflow_integration
        data = df.get_payload_as_string()
        assert "AuthorizationHeader" in data


class TestURLs:
    @pytest.mark.parametrize("fixture_name", ["windows_https", "basic_https", "oidc_https"])
    def test_service_layer_url_https(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name).dataflow_integration
        assert df.service_layer_url == HTTPS_SL_URL

    @pytest.mark.parametrize("fixture_name", ["windows_http", "basic_http"])
    def test_service_layer_url_http(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name).dataflow_integration
        assert df.service_layer_url == HTTP_SL_URL

    @pytest.mark.parametrize("fixture_name", ["windows_https", "basic_https", "oidc_https"])
    def test_dataflow_url_https(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name).dataflow_integration
        assert df._dataflow_url == HTTPS_URL

    @pytest.mark.parametrize("fixture_name", ["windows_http", "basic_http"])
    def test_dataflow_url_http(self, fixture_name, request):
        df = request.getfixturevalue(fixture_name).dataflow_integration
        assert df._dataflow_url == HTTP_URL


@pytest.mark.parametrize("return_code", [0, 1, "-42"])
class TestResumeBookmark:
    def test_windows_https(self, requests_mock, windows_https, return_code, debug_caplog):
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        windows_https.dataflow_integration.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code)
        assert self._resume_bookmark_logged(debug_caplog.text, return_code)

    def test_windows_https_disable_https(self, requests_mock, windows_https_use_https_false, return_code, debug_caplog):
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        windows_https_use_https_false.dataflow_integration.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False)
        assert self._resume_bookmark_logged(debug_caplog.text, return_code, https=False)

    def test_windows_https_disable_verification(
        self, requests_mock, windows_https_verify_false, return_code, debug_caplog
    ):
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        windows_https_verify_false.dataflow_integration.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=False)
        assert self._resume_bookmark_logged(debug_caplog.text, return_code)

    def test_windows_https_custom_cert(self, requests_mock, windows_https_custom_cert, return_code, debug_caplog):
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        windows_https_custom_cert.dataflow_integration.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=CERT_PATH_ABSOLUTE)
        assert self._resume_bookmark_logged(debug_caplog.text, return_code)

    def test_windows_http(self, requests_mock, windows_http, return_code, debug_caplog):
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        windows_http.dataflow_integration.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False)
        assert self._resume_bookmark_logged(debug_caplog.text, return_code, https=False)

    @pytest.mark.parametrize("fixture_name, auth", [("basic_https", "basic"), ("oidc_https", "oidc")])
    def test_credentialed_https(
        self,
        requests_mock,
        fixture_name,
        auth: Literal["basic", "oidc"],
        request,
        return_code,
        debug_caplog,
    ):
        df = request.getfixturevalue(fixture_name).dataflow_integration
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, auth=auth)
        assert self._resume_bookmark_logged(debug_caplog.text, return_code)

    def test_basic_https_disable_https(self, requests_mock, basic_https_use_https_false, return_code, debug_caplog):
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        basic_https_use_https_false.dataflow_integration.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False, auth="basic")
        assert self._resume_bookmark_logged(debug_caplog.text, return_code, https=False)

    @pytest.mark.parametrize(
        "fixture_name, auth",
        [("basic_https_verify_false", "basic"), ("oidc_https_verify_false", "oidc")],
    )
    def test_credentialed_https_disable_verification(
        self,
        requests_mock,
        fixture_name,
        auth: Literal["basic", "oidc"],
        request,
        return_code,
        debug_caplog,
    ):
        df = request.getfixturevalue(fixture_name).dataflow_integration
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=False, auth=auth)
        assert self._resume_bookmark_logged(debug_caplog.text, return_code)

    @pytest.mark.parametrize(
        "fixture_name, auth",
        [("basic_https_custom_cert", "basic"), ("oidc_https_custom_cert", "oidc")],
    )
    def test_credentialed_https_custom_cert(
        self,
        requests_mock,
        fixture_name,
        auth: Literal["basic", "oidc"],
        request,
        return_code,
        debug_caplog,
    ):
        df = request.getfixturevalue(fixture_name).dataflow_integration
        requests_mock.post(f"{HTTPS_URL}/api/workflows/{WORKFLOW_ID}")
        df.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, verify=CERT_PATH_ABSOLUTE, auth=auth)
        assert self._resume_bookmark_logged(debug_caplog.text, return_code)

    def test_basic_http(self, requests_mock, basic_http, return_code, debug_caplog):
        requests_mock.post(f"{HTTP_URL}/api/workflows/{WORKFLOW_ID}")
        basic_http.dataflow_integration.resume_bookmark(return_code)

        assert requests_mock.call_count == 1
        request = requests_mock.request_history[0]
        self._verify_request(request, return_code, https=False, verify=False, auth="basic")
        assert self._resume_bookmark_logged(debug_caplog.text, return_code, https=False)

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
        elif auth == "oidc":
            assert request.headers["Authorization"] == oidc_header
        data = request.json()
        assert data["Values"]["ExitCode"] == return_code
        assert data["WorkflowDefinitionName"] == WORKFLOW_DEFINITION_ID
        assert data["TransitionName"] == TRANSITION_NAME

    def _resume_bookmark_logged(self, log, exit_code, https=True):
        exit_code_logged = f"Returning control to MI Data Flow with exit code {exit_code}" in log
        url_logged = f"Resuming bookmark using URL {HTTPS_URL if https else HTTP_URL}"
        return exit_code_logged and url_logged


@pytest.mark.parametrize("fixture_name", ["basic_http", "basic_https", "windows_http", "windows_https", "oidc_https"])
def test_supporting_files(fixture_name, request):
    df = request.getfixturevalue(fixture_name).dataflow_integration
    assert df.supporting_files_dir == Path(sys.path[0])
