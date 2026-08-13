from pathlib import Path
import sys

from ansys.grantami.dataflow_extensions import _mi_dataflow

tests_path = Path(__file__).parents[3] / "tests"
sys.path.insert(1, str(tests_path))
from mocks import scripting_toolkit  # noqa: E402 F401  # isort: skip

# Get STK interface from tests
mpy = scripting_toolkit.module


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


class SessionBuilder(scripting_toolkit.module.SessionBuilder):
    # Override interface to return a hardcoded session
    def with_autologon(self):
        return Session()


# Override module to use concrete SessionBuilder
mpy.SessionBuilder = SessionBuilder

# Patch import
_mi_dataflow.mpy = mpy
