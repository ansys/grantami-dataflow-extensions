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


mpy.connect = Mock(name="connect", wraps=connect)
scripting_toolkit.granta = mpy

import sys

sys.modules["GRANTA_MIScriptingToolkit"] = scripting_toolkit
