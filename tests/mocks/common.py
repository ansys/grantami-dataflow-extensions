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

"""Common mock utilities shared across Scripting Toolkit version mocks."""

from unittest.mock import Mock


def create_mock_record():
    """Create a mock Record object."""
    record = Mock()
    record.attributes = {}

    attribute = Mock()
    attribute.name = "Additional Processing Notes"
    attribute.value = ""
    record.attributes["Additional Processing Notes"] = attribute

    record.set_attributes = Mock()
    return record


def create_mock_database():
    """Create a mock Database object with get_record_by_id method."""
    db = Mock()
    db.get_record_by_id = Mock(side_effect=lambda *args, **kwargs: create_mock_record())
    return db


def create_mock_session():
    """Create a mock Session object with get_db and update methods."""
    session = Mock()
    session.get_db = Mock(side_effect=lambda *args, **kwargs: create_mock_database())
    session.update = Mock()
    return session
