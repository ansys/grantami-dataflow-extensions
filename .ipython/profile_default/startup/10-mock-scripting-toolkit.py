from types import ModuleType

from ansys.grantami.dataflow_extensions import _mi_dataflow

mpy = ModuleType("ansys.grantami.core")
mpy.__version__ = "5.1.0"


class SessionConfiguration:
    def __init__(self, timeout=300000, max_retries=0, **kwargs):
        self.timeout = timeout
        self.max_retries = max_retries


ATTRIBUTE_NAME = "Additional Processing Notes"


class Attribute:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Record:
    attributes = {ATTRIBUTE_NAME: Attribute(ATTRIBUTE_NAME, "")}

    def set_attributes(self, *args, **kwargs):
        pass


class Database:
    def get_record_by_id(self, *args, **kwargs):
        return Record()


class Session:
    def get_db(self, *args, **kwargs) -> Database:
        return Database()

    def update(self, *args, **kwargs):
        pass


class SessionBuilder:
    def __init__(self, service_layer_url, session_configuration=None):
        self._service_layer_url = service_layer_url
        self._session_configuration = session_configuration

    def with_autologon(self):
        return Session()


# Attach to module
mpy.SessionConfiguration = SessionConfiguration
mpy.SessionBuilder = SessionBuilder

# Patch import
_mi_dataflow.mpy = mpy
