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

import pytest

from ansys.grantami.dataflow_extensions import MissingClientModuleException


@pytest.mark.parametrize(
    "test_case_name",
    [
        "windows_https",
        "windows_http",
        "basic_https",
        "basic_http",
        "oidc_https",
    ],
)
def test_error_raised_on_missing_toolkit(request, test_case_name):
    test_case = request.getfixturevalue(test_case_name)
    with pytest.raises(MissingClientModuleException, match="Could not find Scripting Toolkit"):
        _ = test_case.dataflow_integration.get_scripting_toolkit_session()


@pytest.mark.parametrize(
    "test_case_name",
    [
        "windows_https",
        "windows_http",
        "basic_https",
        "basic_http",
        "oidc_https",
    ],
)
def test_error_raised_on_missing_toolkit_with_deprecated_property(request, test_case_name):
    test_case = request.getfixturevalue(test_case_name)
    with (
        pytest.raises(MissingClientModuleException, match="Could not find Scripting Toolkit"),
        pytest.warns(UserWarning, match="This method is deprecated"),
    ):
        _ = test_case.dataflow_integration.mi_session
