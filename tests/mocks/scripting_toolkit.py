# Copyright (C) 2025 - 2026 ANSYS, Inc. and/or its affiliates.
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

import sys
from types import ModuleType
from unittest.mock import Mock

from .common import create_mock_session

scripting_toolkit = ModuleType("ansys.grantami.core")

scripting_toolkit.__version__ = "5.1.0"


# Create mock classes that track calls
class MockSessionConfiguration:
    """Mock for SessionConfiguration class."""

    def __init__(self, timeout=300000, max_retries=0, **kwargs):
        self.timeout = timeout
        self.max_retries = max_retries


class MockOIDCSessionBuilder:
    """Mock for OIDCSessionBuilder class."""

    # Class-level mock to track calls
    with_access_token = Mock()

    def __init__(self, service_layer_url, session_configuration):
        self._service_layer_url = service_layer_url
        self._session_configuration = session_configuration

    def _with_access_token(self, token):
        MockOIDCSessionBuilder.with_access_token(token=token)
        return create_mock_session()


class MockSessionBuilder:
    """Mock for SessionBuilder class."""

    # Class-level mocks to track calls
    with_autologon = Mock()
    with_credentials = Mock()
    with_oidc = Mock()

    def __init__(self, service_layer_url, session_configuration=None):
        self._service_layer_url = service_layer_url
        self._session_configuration = session_configuration or MockSessionConfiguration()

    def _with_autologon(self):
        MockSessionBuilder.with_autologon()
        return create_mock_session()

    def _with_credentials(self, username, password, domain=None, store_password=False):
        MockSessionBuilder.with_credentials(username=username, password=password)
        return create_mock_session()

    def _with_oidc(self):
        MockSessionBuilder.with_oidc()
        oidc_builder = MockOIDCSessionBuilder(self._service_layer_url, self._session_configuration)
        # Replace instance method with one that calls class-level mock
        oidc_builder.with_access_token = oidc_builder._with_access_token
        return oidc_builder


def _create_session_builder(service_layer_url, session_configuration=None):
    """Factory function to create MockSessionBuilder with proper method binding."""
    builder = MockSessionBuilder(service_layer_url, session_configuration)
    # Replace instance methods with ones that call class-level mocks
    builder.with_autologon = builder._with_autologon
    builder.with_credentials = builder._with_credentials
    builder.with_oidc = builder._with_oidc
    return builder


# Create mock for SessionConfiguration that tracks calls
SessionConfiguration = Mock(side_effect=MockSessionConfiguration)

# Create mock for SessionBuilder that tracks calls
SessionBuilder = Mock(side_effect=_create_session_builder)

# Attach to module
scripting_toolkit.SessionConfiguration = SessionConfiguration
scripting_toolkit.SessionBuilder = SessionBuilder

# Export mocks for direct access in tests
OIDCSessionBuilder = MockOIDCSessionBuilder
_SessionBuilder = MockSessionBuilder

sys.modules["ansys.grantami.core"] = scripting_toolkit
SessionBuilder = Mock(side_effect=_create_session_builder)

# Attach to module
scripting_toolkit.SessionConfiguration = SessionConfiguration
scripting_toolkit.SessionBuilder = SessionBuilder

# Export mocks for direct access in tests
OIDCSessionBuilder = MockOIDCSessionBuilder
_SessionBuilder = MockSessionBuilder

sys.modules["ansys.grantami.core"] = scripting_toolkit
