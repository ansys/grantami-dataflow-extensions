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

# # PyGranta RecordLists example

# ## Introduction

# An example that uses the PyGranta Data Flow Extensions package to interact with a Granta MI Record List as part of a
# Data Flow step. The code below shows how to add the workflow record to a record list.  However, the principles shown
# here can be applied to any PyGranta package.

# ### Useful links
# * [Recommended script structure](../user_guide/index.rst#recommended-script-structure)
# * [Business logic development best practice](../user_guide/index.rst#business-logic-development-best-practice)

# ## Pre-requisites

# This example requires ``ansys-grantami-recordlists``. Install with ``pip install ansys-grantami-recordlists``, or
# consult the [Getting started](https://recordlists.grantami.docs.pyansys.com/version/stable/getting_started/index.html)
# guide for more details.

# ## Example script

# +
import logging
import traceback

from ansys.grantami.recordlists import Connection as RecordListsConnection, RecordListItem

from ansys.grantami.dataflow_extensions import MIDataflowIntegration

# Create an instance of the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add a StreamHandler to write the output to stderr
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def main():
    """
    Initializes the MI Data Flow integration module, runs the business logic,
    and cleans up once execution has completed.
    """

    # Ansys strongly recommend using HTTPS in production environments.
    # If you are using an internal certificate, you should specify the
    # CA certificate with certificate_filename=my_cert_file.crt and add the
    # certificate to the workflow as a supporting file, or use an absolute
    # pathlib.Path object to the file on disk.
    # Refer to the MIDataflowIntegration API reference page for more details.
    dataflow_integration = MIDataflowIntegration(use_https=False)

    try:
        step_logic(dataflow_integration)
        exit_code = 0
    except Exception:
        traceback.print_exc()
        exit_code = 1
    dataflow_integration.resume_bookmark(exit_code)


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
    dataflow_integration = MIDataflowIntegration.from_dict_payload(
        dataflow_payload=dataflow_payload,
        use_https=False,
    )
    step_logic(dataflow_integration)


# These GUIDs cannot be determined by a PyGranta package, so they are hardcoded
# Alternatively, they could be accessed via the Granta MI Scripting Toolkit
DATABASE_GUID = "43a43640-4919-428a-bac9-16efbc4ce6ed"  # MI_Training
TABLE_GUID = "ad27baf0-42e9-4136-bc96-9dbbf116e265"  # Metals Pedigree

# The Record List name could alternatively be provided as a "Custom Script Parameter"
# in Data Flow Designer
RECORD_LIST_NAME = "Data Flow List"


def step_logic(dataflow_integration):
    """Contains the business logic to be executed as part of the workflow.

    In this example, get a record list with the required name and add
    the data flow record to the list.

    Replace the code in this module with your custom business logic.
    """
    connection = dataflow_integration.configure_pygranta_connection(RecordListsConnection)
    client = connection.connect()

    try:
        record_list = next(rl for rl in client.get_all_lists() if rl.name == RECORD_LIST_NAME)
    except StopIteration:
        ValueError(f'Could not find record list with name "{RECORD_LIST_NAME}"')
        return

    payload = dataflow_integration.get_payload_as_dict()
    new_item = RecordListItem(
        database_guid=DATABASE_GUID,
        table_guid=TABLE_GUID,
        record_history_guid=payload["Record"]["RecordHistoryGuid"],
    )
    client.add_items_to_list(record_list=record_list, items=[new_item])
    logger.info("Added item to list")  # This output will be visible in the api/logs page


if __name__ == "__main__":
    # main()  # Used when running the script as part of a workflow
    testing()  # Used when testing the script manually
