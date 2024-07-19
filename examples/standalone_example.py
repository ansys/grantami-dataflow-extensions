import json

from ansys.grantami.dataflow_toolkit import MIDataflowIntegration

"""
########################################### MI Data Flow Example #######################################################
Example script to be used as starting point for Start or End Scripts in MI Data Flow Designer.

Business logic should be implemented in function step_logic which is called by main() or testing() for debugging.

step_logic function takes two arguments:

- mi_session: A Granta MI Python STK session. The credentials used to create this session are the same as those of the
user executing this step.
- workflow_stream: The json response provided by the Data Flow API for this step. The contents can be used to locate
records and use user-provided information in the business logic script.

Switch at the bottom between calling main() or testing() to trigger the step_logic function in production or debugging
respectively.

-------------------------------------------------Logs-------------------------------------------------------------------
Log files can be found by browsing to MI Data Flow logs page:
MI 2023R2   http://my.server.name/mi_dataflow/api/logs
MI 2023R1   http://my.server.name/mi_workflow_2/api/logs

At the server:

MI 2023R2   %LOCALAPPDATA%\Granta Design\MI\logs\MIDataFlowDesigner.log
MI 2023R1   C:\ProgramData\Granta\GRANTA MI\Workflow 2\logs

-------------------------------------------------Troubleshooting--------------------------------------------------------
A working directory is created at the server in: C:\windows\TEMP\ with files __stderr__ and __stdout__ that should contain Python's error tracing and prints to console that can be useful
"""


def step_logic(workflow_stream):
    """
    This function is where the business logic should be put.
    """

    db_key = workflow_stream["Record"]["Database"]
    db = mi_session.get_db(db_key=db_key)
    record_hguid = workflow_stream["Record"]["RecordHistoryGuid"]
    rec = db.get_record_by_id(hguid=record_hguid)

    # Write the json received from the dataflow API to the attribute "Additional Processing Notes"
    rec.attributes["Additional Processing Notes"].value = f"{json.dumps(workflow_stream, indent=4)}"
    rec.set_attributes([rec.attributes["Additional Processing Notes"]])

    # Update record database
    mi_session.update([rec])
    print("Updated MI database")  # This output will be visible in the api/logs page


if __name__ == "__main__":
    df = MIDataflowIntegration()
    try:
        step_logic(df.df_data)
        exit_code = 0
    except Exception as e:
        exit_code = 1
    df.resume_bookmark(exit_code)
