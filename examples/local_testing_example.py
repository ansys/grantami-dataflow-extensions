import requests

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
-------------------------------------------------Troubleshooting--------------------------------------------------------
A working directory is created at the server in: C:\windows\TEMP\ with files __stderr__ and __stdout__ that should contain Python's error tracing and prints to console that can be useful
"""


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


    step_logic(workflow_stream)


def step_logic(workflow_stream):
    """
    This function is where the business logic should be put. It makes an arbitrary request to an external test server.
    """




    print("Updated MI database")  # This output will be visible in the api/logs page


if __name__ == "__main__":

