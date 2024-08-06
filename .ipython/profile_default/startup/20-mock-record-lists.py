from ansys.grantami.recordlists import Connection, RecordList, RecordListsApiClient


def connect(self):
    return RecordListsApiClient(
        session=None,
        service_layer_url="http://my_server_name/mi_servicelayer",
        configuration=None,
    )


def with_autologon(self):
    return self


Connection.connect = connect
Connection.with_autologon = with_autologon


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
