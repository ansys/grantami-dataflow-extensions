# Copyright (C) 2025 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from types import ModuleType

VERSION = "5.1.0"
module = ModuleType("ansys.grantami.core")
module.__version__ = VERSION


class SessionConfiguration:
    def __init__(self, timeout=300000, max_retries=0, **kwargs):
        self.timeout = timeout
        self.max_retries = max_retries


class OIDCSessionBuilder:
    def with_access_token(self, token): ...


class SessionBuilder:
    def __init__(self, service_layer_url, session_configuration=None):
        self._service_layer_url = service_layer_url
        self._session_configuration = session_configuration

    def with_autologon(self): ...
    def with_credentials(self, username, password, domain=None, store_password=False): ...
    def with_oidc(self): ...


# Attach to module (only types used directly by dataflow-extensions)
module.SessionConfiguration = SessionConfiguration
module.SessionBuilder = SessionBuilder
