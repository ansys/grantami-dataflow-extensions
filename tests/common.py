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

from base64 import b64encode
from dataclasses import dataclass
import json
from pathlib import Path

from ansys.grantami.dataflow_toolkit.mi_dataflow import _AuthenticationMode

CERT_FILE = "test_cert.crt"
CERT_PATH_ABSOLUTE = Path(__file__).parent / CERT_FILE
CERT_PATH_RELATIVE = Path(CERT_FILE)

HTTP_URL = "http://my_server_name/mi_dataflow"
HTTPS_URL = "https://my_server_name/mi_dataflow"

HTTP_SL_URL = HTTP_URL.replace("dataflow", "servicelayer")
HTTPS_SL_URL = HTTPS_URL.replace("dataflow", "servicelayer")

WORKFLOW_ID = "67eb55ff-363a-42c7-9793-df363f1ecc83"
WORKFLOW_DEFINITION_ID = "Example; Version=1.0.0.0"
TRANSITION_NAME = "Python_83e51914-3752-40d0-8350-c096674873e2"

USERNAME = "username"
PASSWORD = "secret_password"

encoded_credentials = b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode("ascii")
basic_header = f"Basic {encoded_credentials}"

access_token = "0123456789abcdefghijkl"
oidc_header = f"Bearer {access_token}"

dict_test_cases = {}


@dataclass(frozen=True)
class TestCase:
    payload: dict | str
    auth_mode: _AuthenticationMode | None = None


windows_http_payload = {
    "WorkflowId": WORKFLOW_ID,
    "WorkflowDefinitionId": WORKFLOW_DEFINITION_ID,
    "TransitionName": TRANSITION_NAME,
    "Record": {
        "Database": "MI_Training",
        "Table": "Metals Pedigree",
        "RecordHistoryGuid": "d2f51a3d-c274-4a1e-b7c9-8ba2976202cc",
    },
    "WorkflowUrl": HTTP_URL,
    "AuthorizationHeader": "",
    "ClientCredentialType": "Windows",
    "Attributes": {
        "Record": {"Value": ["d2f51a3d-c274-4a1e-b7c9-8ba2976202cc+MI_Training"]},
        "TransitionId": {"Value": "9f1bf6e7-0b05-4cd3-ac61-1d2d11a1d351"},
    },
    "CustomValues": {},
}
dict_test_cases["windows_http"] = TestCase(
    payload=windows_http_payload,
    auth_mode=_AuthenticationMode.INTEGRATED_WINDOWS_AUTHENTICATION,
)

windows_https_payload = windows_http_payload.copy()
windows_https_payload["WorkflowUrl"] = HTTPS_URL
dict_test_cases["windows_https"] = TestCase(
    payload=windows_https_payload,
    auth_mode=_AuthenticationMode.INTEGRATED_WINDOWS_AUTHENTICATION,
)

basic_http_payload = {
    "WorkflowId": WORKFLOW_ID,
    "WorkflowDefinitionId": WORKFLOW_DEFINITION_ID,
    "TransitionName": TRANSITION_NAME,
    "Record": {
        "Database": "MI_Training",
        "Table": "Metals Pedigree",
        "RecordHistoryGuid": "d2f51a3d-c274-4a1e-b7c9-8ba2976202cc",
    },
    "WorkflowUrl": HTTP_URL,
    "AuthorizationHeader": basic_header,
    "ClientCredentialType": "Basic",
    "Attributes": {
        "Record": {"Value": ["d2f51a3d-c274-4a1e-b7c9-8ba2976202cc+MI_Training"]},
        "TransitionId": {"Value": "9f1bf6e7-0b05-4cd3-ac61-1d2d11a1d351"},
    },
    "CustomValues": {},
}
dict_test_cases["basic_http"] = TestCase(
    payload=basic_http_payload,
    auth_mode=_AuthenticationMode.BASIC_AUTHENTICATION,
)

basic_https_payload = basic_http_payload.copy()
basic_https_payload["WorkflowUrl"] = HTTPS_URL
dict_test_cases["basic_https"] = TestCase(
    payload=basic_https_payload,
    auth_mode=_AuthenticationMode.BASIC_AUTHENTICATION,
)

oidc_http_payload = basic_http_payload.copy()
oidc_http_payload["ClientCredentialType"] = "None"
oidc_http_payload["AuthorizationHeader"] = oidc_header
dict_test_cases["oidc_http"] = TestCase(
    payload=oidc_http_payload,
    auth_mode=_AuthenticationMode.OIDC_AUTHENTICATION,
)

oidc_https_payload = oidc_http_payload.copy()
oidc_https_payload["WorkflowUrl"] = HTTPS_URL
dict_test_cases["oidc_https"] = TestCase(
    payload=oidc_https_payload,
    auth_mode=_AuthenticationMode.OIDC_AUTHENTICATION,
)

digest_http_payload = basic_http_payload.copy()
digest_http_payload["ClientCredentialType"] = "Digest"
dict_test_cases["digest_http"] = TestCase(
    payload=digest_http_payload,
)
digest_https_payload = digest_http_payload.copy()
digest_https_payload["WorkflowUrl"] = HTTPS_URL
dict_test_cases["digest_https"] = TestCase(
    payload=digest_https_payload,
)

str_test_cases = {
    k: TestCase(json.dumps(v.payload), auth_mode=v.auth_mode) for k, v in dict_test_cases.items()
}
