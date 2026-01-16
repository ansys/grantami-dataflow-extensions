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

from base64 import b64encode
import os
from pathlib import Path


class ScriptingToolkitVersionConfig:
    """Centralized configuration for Scripting Toolkit version-based testing."""

    ALLOWED_VERSIONS = {"4.x", "latest"}
    ENV_VAR = "SCRIPTING_TOOLKIT_TEST_VERSION"

    def __init__(self):
        raw_value = os.getenv(self.ENV_VAR, "latest")
        self.version: str = raw_value if raw_value else "latest"
        if self.version not in self.ALLOWED_VERSIONS:
            raise ValueError(
                f"{self.ENV_VAR} must be one of {self.ALLOWED_VERSIONS}, but got '{self.version}'."
            )

    def requires_version(self, *versions: str) -> bool:
        """Check if current version matches any of the specified versions."""
        return self.version in versions


SCRIPTING_TOOLKIT_CONFIG = ScriptingToolkitVersionConfig()


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
