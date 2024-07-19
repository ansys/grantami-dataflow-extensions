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

# # Standalone example

# This notebook provides a best-practice example for using Data Flow Toolkit to interact with a non-Granta MI resource
# as part of a Data Flow operation.

# The cell below contains an example script that simply prints the record identifying information which is received from
# Data Flow. However, this could be replaced with any other business logic which can make use of the data proided by
# Data Flow. To perform operations that rely on additional information from Granta MI, see the other examples in this
# package.

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
    except Exception:
        exit_code = 1
    df.resume_bookmark(exit_code)


def testing():
    """Contains a static copy of a Data Flow data payload for testing purposes"""
    
    dataflow_payload = {
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

    step_logic(dataflow_payload)


def step_logic(dataflow_payload):
    """Contains the business logic to be executed as part of the workflow."""
    
    db_key = dataflow_payload["Record"]["Database"]
    record_history_guid = dataflow_payload["Record"]["Database"]
    print(
        f"A workflow operating on record '{record_history_guid}'"
        f"in database '{db_key}' has triggered this script"
    )


if __name__ == "__main__":
    # main()  # Used when running the script as part of a workflow
    testing()  # Used when running the script manually

