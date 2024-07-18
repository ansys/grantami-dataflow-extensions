import json

from GRANTA_MIScriptingToolkit import granta as mpy
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


def main():
    """
    Main function that needs to be called when the script is in MI Data Flow Designer
    """
    df = MIDataflowIntegration()
    try:
        # Call the logic
        step_logic(df.mi_session, df.df_data)
        exit_code = 0
    except Exception as e:
        exit_code = 1
    df.resume_bookmark(exit_code)


def testing():
    """
    This function allows to debug the logic outside the MI Data Flow application by passing the workflow_stream below.
    To get a starting workflow_stream, run the script once within Data Flow and get the workflow data stream from the
    workflow logs page (see above)
    """
    session = mpy.connect(service_layer_url="http://localhost/mi_servicelayer", autologon=True)
    workflow_stream = {
        "WorkflowId": "806eacd2-3d9a-4a10-b1c1-acd5f7b36b30",
        "WorkflowDefinitionId": "test8; Version=1.0.0.0",
        "TransitionName": "Python_6e407a8b-f8ec-41fc-8879-618bd7c40cda",
        "Record": {
            "Database": "MI_Training",
            "Table": "Metals Pedigree",
            "RecordHistoryGuid": "d2f51a3d-c274-4a1e-b7c9-8ba2976202cc",
        },
        "WorkflowUrl": "http://localhost/mi_workflow_2",
        "AuthorizationHeader": "",
        "ClientCredentialType": "Windows",
        "Attributes": {
            "Record": {"Value": ["d2f51a3d-c274-4a1e-b7c9-8ba2976202cc+MI_Training"]},
            "TransitionId": {"Value": "93076607-081e-422b-b819-f15fe833a6e3"},
        },
        "CustomValues": {},
    }

    step_logic(session, workflow_stream)


def step_logic(mi_session, workflow_stream):
    """
    This function is where the business logic should be put. It receives the mi session from MI Dataflow, the workflow
    stream JSON and the logger
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
    """
    Code entry point
    Switch between main() and testing() commenting to run debug the business logic
    """
    main()
    # testing()
