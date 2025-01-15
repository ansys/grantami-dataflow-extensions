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

from ansys.grantami.recordlists import Connection, RecordList, RecordListsApiClient


def connect(self):
    return RecordListsApiClient(
        session=None,
        service_layer_url=self._base_service_layer_url,
        configuration=None,
    )


def with_autologon(self):
    return self


def with_credentials(self, username, password, domain=None):
    return self


Connection.connect = connect
Connection.with_autologon = with_autologon
Connection.with_credentials = with_credentials


def get_all_lists(self):
    return [
        RecordList(
            identifier="",
            name="Data Flow List",
            created_timestamp=None,
            created_user=None,
            published=False,
            is_revision=False,
            awaiting_approval=False,
            internal_use=False,
        )
    ]


def add_items_to_list(self, record_list, items):
    pass


RecordListsApiClient.get_all_lists = get_all_lists
RecordListsApiClient.add_items_to_list = add_items_to_list
