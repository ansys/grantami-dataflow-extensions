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
# This import must happen before dataflow_toolkit is imported to correct mock these libraries
from mocks import record_lists, scripting_toolkit  # isort:skip  # noqa: F401

import logging

import pytest

from ansys.grantami.dataflow_toolkit import MIDataflowIntegration
from common import CERT_FILE, dict_test_cases


@pytest.fixture(scope="function")
def windows_http():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["windows_http"].payload, use_https=False
    )


@pytest.fixture(scope="function")
def windows_https():
    return MIDataflowIntegration.from_dict_payload(dict_test_cases["windows_https"].payload)


@pytest.fixture(scope="function")
def windows_https_use_https_false():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["windows_https"].payload, use_https=False
    )


@pytest.fixture(scope="function")
def windows_https_verify_false():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["windows_https"].payload, verify_ssl=False
    )


@pytest.fixture(scope="function")
def windows_https_custom_cert():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["windows_https"].payload, certificate_file=CERT_FILE
    )


@pytest.fixture(scope="function")
def basic_http():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["basic_http"].payload, use_https=False
    )


@pytest.fixture(scope="function")
def basic_https():
    return MIDataflowIntegration.from_dict_payload(dict_test_cases["basic_https"].payload)


@pytest.fixture(scope="function")
def basic_https_use_https_false():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["basic_https"].payload, use_https=False
    )


@pytest.fixture(scope="function")
def basic_https_verify_false():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["basic_https"].payload, verify_ssl=False
    )


@pytest.fixture(scope="function")
def basic_https_custom_cert():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["basic_https"].payload, certificate_file=CERT_FILE
    )


@pytest.fixture(scope="function")
def oidc_https():
    return MIDataflowIntegration.from_dict_payload(dict_test_cases["oidc_https"].payload)


@pytest.fixture(scope="function")
def oidc_https_use_https_false():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["oidc_https"].payload, use_https=False
    )


@pytest.fixture(scope="function")
def oidc_https_verify_false():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["oidc_https"].payload, verify_ssl=False
    )


@pytest.fixture(scope="function")
def oidc_https_custom_cert():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["oidc_https"].payload, certificate_file=CERT_FILE
    )


@pytest.fixture(scope="function")
def digest_http():
    return MIDataflowIntegration.from_dict_payload(
        dict_test_cases["digest_http"].payload, use_https=False
    )


@pytest.fixture(scope="function")
def digest_https():
    return MIDataflowIntegration.from_dict_payload(dict_test_cases["digest_https"].payload)


@pytest.fixture(scope="function")
def debug_caplog(caplog):
    caplog.set_level(logging.DEBUG)
    return caplog
