# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Scripting Toolkit Script Example

# This notebook provides a best-practice example for using Data Flow Toolkit to interact with Granta MI via Scripting
# Toolkit as part of a Data Flow operation.

# ## Script Overview

# The cell below contains an example script that uploads the data payload received by Data Flow to the workflow record.
# However, this could be replaced with any other business logic which requires access to Granta MI resources.

# The example script includes the following functions:
#
# * `main()`: Instantiates the `MIDataflowIntegration` class, which parses the data passed into this script by Data
#   Flow. Executes the business logic, and resumes the workflow once the business logic has completed.
# * `testing()`: Includes a static payload which can be provided to the business logic in place of real data for testing
#   purposes
# * `step_logic()`: Contains the actual business logic for the step. Uses the data provided by Data Flow (or defined
#   statically).
#
# Finally, the `if __name__ == "__main__":` block is the entry point for the script. It should be set to call the
# `testing()` function whenever executed outside of Data Flow, but switched to `main()` when added to the workflow
# definition in Data Flow Designer.

# ## Additional notes

# This script can be used alongside Data Flow to generate new `dataflow_data` payloads for testing.

# +
import json

from ansys.grantami.dataflow_toolkit import MIDataflowIntegration


def main():
    """
    Initializes the Data Flow integration module, runs the business logic,
    and cleans up once execution has completed.
    """

    df = MIDataflowIntegration()
    try:
        step_logic(df.mi_session, df.df_data)
        exit_code = 0
    except Exception as e:
        exit_code = 1
    df.resume_bookmark(exit_code)


def testing():
    """Contains a static copy of a Data Flow data payload for testing purposes"""

    # This import is only needed when testing
    from GRANTA_MIScriptingToolkit import granta as mpy
    
    session = mpy.connect(
        service_layer_url="http://localhost/mi_servicelayer",
        autologon=True,
    )
    dataflow_data = {
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
            "Record": {
                "Value": ["d2f51a3d-c274-4a1e-b7c9-8ba2976202cc+MI_Training"]
            },
            "TransitionId": {"Value": "93076607-081e-422b-b819-f15fe833a6e3"},
        },
        "CustomValues": {},
    }

    step_logic(session, dataflow_data)


def step_logic(mi_session, dataflow_data):
    """Contains the business logic to be executed as part of the workflow.

    In this example, identify the record that is the subject of the
    workflow operation, and upload the Data Flow payload to that record.
    """

    db_key = dataflow_data["Record"]["Database"]
    db = mi_session.get_db(db_key=db_key)
    record_hguid = dataflow_data["Record"]["RecordHistoryGuid"]
    rec = db.get_record_by_id(hguid=record_hguid)

    # Write the json received from the dataflow API to the attribute
    # "Additional Processing Notes"
    data = json.dumps(dataflow_data, indent=4)
    rec.attributes["Additional Processing Notes"].value = data
    rec.set_attributes([rec.attributes["Additional Processing Notes"]])

    # Update record database
    mi_session.update([rec])
    print("Updated MI database")  # This output will be visible in the api/logs page


if __name__ == "__main__":
    # main()
    testing()

