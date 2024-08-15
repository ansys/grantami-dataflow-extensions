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

from types import ModuleType
from unittest.mock import Mock

scripting_toolkit = ModuleType("GRANTA_MIScriptingToolkit")

mpy = Mock()
mpy.__version__ = "4.0.0"


def connect(*args, **kwargs):
    session = Mock()

    def get_db(*args, **kwargs):
        db = Mock()

        def get_record_by_id(*args, **kwargs):
            record = Mock()
            record.attributes = {}

            attribute = Mock()
            attribute.name = "Additional Processing Notes"
            attribute.value = ""
            record.attributes["Additional Processing Notes"] = attribute

            def set_attributes(*args, **kwargs):
                pass

            record.set_attributes = set_attributes
            return record

        db.get_record_by_id = get_record_by_id
        return db

    session.get_db = get_db

    def update(*args, **kwargs):
        pass

    session.update = update
    return session


mpy.connect = Mock(wraps=connect)
scripting_toolkit.granta = mpy

import sys

sys.modules["GRANTA_MIScriptingToolkit"] = scripting_toolkit
