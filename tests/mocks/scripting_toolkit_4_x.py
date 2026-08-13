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

VERSION = "4.0.0"
module = ModuleType("GRANTA_MIScriptingToolkit")
module.__version__ = VERSION

granta_module = ModuleType("granta")
granta_module.__version__ = VERSION


def connect(
    service_layer_url: str,
    user_name: str = None,
    password: str = None,
    domain: str = None,
    autologon: bool = None,
    timeout: int = 300000,
    oidc: bool = False,
    auth_token: str = None,
    store_password: bool = False,
    max_retries: int = 0,
    *args,
    **kwargs,
):
    pass

granta_module.connect = connect

# Attach to module (only types used directly by dataflow-extensions)
module.granta = granta_module
