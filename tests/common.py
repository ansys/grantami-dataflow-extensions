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
from pathlib import Path
from types import SimpleNamespace

payloads = SimpleNamespace()

HTTP_URL = "http://my_server_name/mi_dataflow"
HTTPS_URL = "https://my_server_name/mi_dataflow"

HTTP_SL_URL = HTTP_URL.replace("dataflow", "servicelayer")
HTTPS_SL_URL = HTTPS_URL.replace("dataflow", "servicelayer")

WORKFLOW_ID = "67eb55ff-363a-42c7-9793-df363f1ecc83"
WORKFLOW_DEFINITION_ID = "Example; Version=1.0.0.0"
TRANSITION_NAME = "Python_83e51914-3752-40d0-8350-c096674873e2"

payloads.windows_http = {
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

payloads.windows_https = payloads.windows_http.copy()
payloads.windows_https["WorkflowUrl"] = HTTPS_URL

USERNAME = "username"
PASSWORD = "secret_password"

encoded_credentials = b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode("ascii")
basic_header = f"Basic {encoded_credentials}"

payloads.basic_http = {
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

payloads.basic_https = payloads.basic_http.copy()
payloads.basic_https["WorkflowUrl"] = HTTPS_URL

payloads.digest_http = payloads.windows_http.copy()
payloads.digest_http["ClientCredentialType"] = "Digest"

payloads.digest_https = payloads.digest_http.copy()
payloads.digest_https["WorkflowUrl"] = HTTPS_URL

CERT_FILE = "test_cert.crt"
CERT_PATH = Path(__file__).parent / CERT_FILE
