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
#
# This import must happen before dataflow_extensions is imported to correctly mock these libraries
from mocks import record_lists, scripting_toolkit  # isort:skip  # noqa: F401

from copy import deepcopy
from dataclasses import dataclass
import json
import logging
from pathlib import Path

from common import (
    CERT_FILE,
    HTTP_URL,
    HTTPS_URL,
    TRANSITION_NAME,
    WORKFLOW_DEFINITION_ID,
    WORKFLOW_ID,
    basic_header,
    oidc_header,
)
import pytest

from ansys.grantami.dataflow_extensions import MIDataflowIntegration
from ansys.grantami.dataflow_extensions._mi_dataflow import _AuthenticationMode


@dataclass
class TestCase:
    payload: dict | str
    use_https: bool | None = True
    verify_ssl: bool | None = True
    certificate_file: Path | str | None = None
    auth_mode: _AuthenticationMode | None = None

    @property
    def payload_str(self) -> str:
        return json.dumps(self.payload)

    @property
    def dataflow_integration(self) -> MIDataflowIntegration | None:
        kwargs = {"dataflow_payload": self.payload}
        if self.use_https is not None:
            kwargs["use_https"] = self.use_https
        if self.verify_ssl is not None:
            kwargs["verify_ssl"] = self.verify_ssl
        if self.certificate_file is not None:
            kwargs["certificate_file"] = self.certificate_file
        try:
            return MIDataflowIntegration.from_dict_payload(**kwargs)
        except (NotImplementedError, ValueError):
            raise RuntimeError("This TestCase object has an incorrect configuration.")


@pytest.fixture(scope="function")
def windows_http() -> TestCase:
    payload = {
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
    return TestCase(
        payload=payload,
        use_https=False,
        auth_mode=_AuthenticationMode.INTEGRATED_WINDOWS_AUTHENTICATION,
    )


@pytest.fixture(scope="function")
def windows_https(windows_http) -> TestCase:
    test_case = deepcopy(windows_http)
    test_case.payload["WorkflowUrl"] = HTTPS_URL
    test_case.use_https = True
    return test_case


@pytest.fixture(scope="function")
def windows_https_use_https_false(windows_https) -> TestCase:
    test_case = deepcopy(windows_https)
    test_case.use_https = False
    return test_case


@pytest.fixture(scope="function")
def windows_https_verify_false(windows_https) -> TestCase:
    test_case = deepcopy(windows_https)
    test_case.verify_ssl = False
    return test_case


@pytest.fixture(scope="function")
def windows_https_custom_cert(windows_https) -> TestCase:
    test_case = deepcopy(windows_https)
    test_case.certificate_file = CERT_FILE
    return test_case


@pytest.fixture(scope="function")
def basic_http(windows_http) -> TestCase:
    test_case = deepcopy(windows_http)
    test_case.payload["ClientCredentialType"] = "Basic"
    test_case.payload["AuthorizationHeader"] = basic_header
    test_case.auth_mode = _AuthenticationMode.BASIC_AUTHENTICATION
    return test_case


@pytest.fixture(scope="function")
def basic_https(basic_http) -> TestCase:
    test_case = deepcopy(basic_http)
    test_case.payload["WorkflowUrl"] = HTTPS_URL
    test_case.use_https = True
    return test_case


@pytest.fixture(scope="function")
def basic_https_use_https_false(basic_https) -> TestCase:
    test_case = deepcopy(basic_https)
    test_case.use_https = False
    return test_case


@pytest.fixture(scope="function")
def basic_https_verify_false(basic_https) -> TestCase:
    test_case = deepcopy(basic_https)
    test_case.verify_ssl = False
    return test_case


@pytest.fixture(scope="function")
def basic_https_custom_cert(basic_https) -> TestCase:
    test_case = deepcopy(basic_https)
    test_case.certificate_file = CERT_FILE
    return test_case


@pytest.fixture(scope="function")
def oidc_http(basic_http) -> TestCase:
    test_case = deepcopy(basic_http)
    test_case.payload["ClientCredentialType"] = "None"
    test_case.payload["AuthorizationHeader"] = oidc_header
    test_case.auth_mode = _AuthenticationMode.OIDC_AUTHENTICATION
    return test_case


@pytest.fixture(scope="function")
def oidc_https(oidc_http) -> TestCase:
    test_case = deepcopy(oidc_http)
    test_case.payload["WorkflowUrl"] = HTTPS_URL
    test_case.use_https = True
    return test_case


@pytest.fixture(scope="function")
def oidc_https_verify_false(oidc_https) -> TestCase:
    test_case = deepcopy(oidc_https)
    test_case.verify_ssl = False
    return test_case


@pytest.fixture(scope="function")
def oidc_https_custom_cert(oidc_https) -> TestCase:
    test_case = deepcopy(oidc_https)
    test_case.certificate_file = CERT_FILE
    return test_case


@pytest.fixture(scope="function")
def digest_http(basic_http) -> TestCase:
    test_case = deepcopy(basic_http)
    test_case.payload["ClientCredentialType"] = "Digest"
    test_case.auth_mode = None
    return test_case


@pytest.fixture(scope="function")
def digest_https(digest_http) -> TestCase:
    test_case = deepcopy(digest_http)
    test_case.payload["WorkflowUrl"] = HTTPS_URL
    test_case.use_https = True
    return test_case


@pytest.fixture(scope="function")
def debug_caplog(caplog):
    caplog.set_level(logging.DEBUG)
    return caplog
