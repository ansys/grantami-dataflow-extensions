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

# # PyGranta RecordLists Example

# This notebook provides a best-practice example for using Data Flow Toolkit to interact a Granta MI Record List as
# part of a Data Flow step. For more information on how to use the PyGranta RecordLists package, see the
# [PyGranta RecordLists documentation](https://recordlists.grantami.docs.pyansys.com/).

# This example uses the PyGranta RecordLists package as an example, and the principles shown here can be applied to any
# PyGranta package.

# ## Script Overview

# The cell below contains an example script that adds the data flow record to a record list.

# The example script includes the following functions:
#
# * `main()`: Instantiates the `MIDataflowIntegration` class, which parses the data passed into this script by Data
#   Flow. Executes the business logic, and resumes the workflow once the business logic has completed.
# * `testing()`: Includes a static payload which can be provided to the `MIDataflowIntegration` constructor in place of
#   real data for testing purposes.
# * `step_logic()`: Contains the actual business logic for the step. Uses the data provided by Data Flow (or defined
#   statically).
#
# Finally, the `if __name__ == "__main__":` block is the entry point for the script. It should be set to call the
# `testing()` function whenever executed outside of Data Flow, but switched to `main()` when added to the workflow
# definition in Data Flow Designer.

# +
import traceback

from ansys.grantami.recordlists import Connection as RecordListsConnection
from ansys.grantami.recordlists import RecordListItem

from ansys.grantami.dataflow_toolkit import MIDataflowIntegration


def main():
    """
    Initializes the Data Flow integration module, runs the business logic,
    and cleans up once execution has completed.
    """

    # It is strongly recommended to use HTTPS in production
    # If you are using an internal certificate, you should specify the
    # CA certificate with certificate_filename=my_cert_file.crt and add the
    # certificate to the workflow as a supporting file.
    df = MIDataflowIntegration(use_https=False)

    try:
        connection = df.configure_pygranta_connection(RecordListsConnection)
        client = connection.connect()
        step_logic(client, df.df_data)
        exit_code = 0
    except Exception:
        traceback.print_exc()
        exit_code = 1
    df.resume_bookmark(exit_code)


def testing():
    """Contains a static copy of a Data Flow data payload for testing purposes"""
    dataflow_payload = {
        "WorkflowId": "67eb55ff-363a-42c7-9793-df363f1ecc83",
        "WorkflowDefinitionId": "Example; Version=1.0.0.0",
        "TransitionName": "Python_83e51914-3752-40d0-8350-c096674873e2",
        "Record": {
            "Database": "MI_Training",
            "Table": "Metals Pedigree",
            "RecordHistoryGuid": "d2f51a3d-c274-4a1e-b7c9-8ba2976202cc",
        },
        "WorkflowUrl": "http://my_server_name/mi_dataflow",
        "AuthorizationHeader": "",
        "ClientCredentialType": "Windows",
        "Attributes": {
            "Record": {"Value": ["d2f51a3d-c274-4a1e-b7c9-8ba2976202cc+MI_Training"]},
            "TransitionId": {"Value": "9f1bf6e7-0b05-4cd3-ac61-1d2d11a1d351"},
        },
        "CustomValues": {},
    }

    # Call MIDataflowIntegration constructor with "dataflow_payload" argument
    # instead of reading data from Data Flow.
    df = MIDataflowIntegration.from_static_payload(
        dataflow_payload=dataflow_payload,
        use_https=False,
    )
    client = df.configure_pygranta_connection(RecordListsConnection).connect()
    step_logic(client, dataflow_payload)


# These GUIDs cannot be determined by a PyGranta package, so they are hardcoded
# Alternatively, they could be accessed via Scripting Toolkit
DATABASE_GUID = "43a43640-4919-428a-bac9-16efbc4ce6ed"  # MI_Training
TABLE_GUID = "ad27baf0-42e9-4136-bc96-9dbbf116e265"  # Metals Pedigree

# The Record List name could alternatively be provided as a "Custom Script Parameter"
# in Data Flow Designer
RECORD_LIST_NAME = "Data Flow List"


def step_logic(client, dataflow_payload):
    """Contains the business logic to be executed as part of the workflow.

    In this example, get a record list with the required name and add
    the data flow record to the list.

    Replace the code in this module with your custom business logic.
    """
    try:
        record_list = next(rl for rl in client.get_all_lists() if rl.name == RECORD_LIST_NAME)
    except StopIteration:
        ValueError(f'Could not find record list with name "{RECORD_LIST_NAME}"')
        return

    new_item = RecordListItem(
        database_guid=DATABASE_GUID,
        table_guid=TABLE_GUID,
        record_history_guid=dataflow_payload["Record"]["RecordHistoryGuid"],
    )
    client.add_items_to_list(record_list=record_list, items=[new_item])
    print("Added item to list")  # This output will be visible in the api/logs page


if __name__ == "__main__":
    # main()  # Used when running the script as part of a workflow
    testing()  # Used when testing the script manually
