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

# # Granta MI Scripting Toolkit example

# ## Introduction

# An example that uses the PyGranta Data Flow Extensions package to interact with a Granta MI system via the Granta MI
# Scripting Toolkit. This example uploads the data payload received by MI Data Flow to the workflow record. This could
# be replaced with any other business logic which requires access to Granta MI resources.

# ### Useful links
# * [Recommended script structure](../user_guide/index.rst#recommended-script-structure)
# * [Business logic development best practice](../user_guide/index.rst#business-logic-development-best-practice)

# <div class="alert alert-warning">
#
# **Warning:**
#
# The `step_logic()` function generates the dataflow payload, and explicitly calls the `get_payload_as_str()` method
# with `include_credentials=False` to avoid writing credentials to the Granta MI database. If you are using Basic or
# OIDC Authentication and require these credentials for your business logic, inject these credentials into
# the `dataflow_payload["AuthorizationHeader"]` value in the `testing()` function directly, for example via an
# environment variable.
# </div>

# ## Pre-requisites

# This example assumes the workflow has been configured with the 'Metals Pedigree' table in the MI Training database,
# but includes guidance for how to adjust the Python code to work with a different database schema.

# <div class="alert alert-info">
#
# **Info:**
#
# Running this notebook requires the Granta MI Scripting Toolkit package. If you do not have access to the Granta MI
# Scripting Toolkit, contact your System Administrator.
# </div>

# ## Example script

# +
import logging
import traceback

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


def step_logic(dataflow_integration):
    """Contains the business logic to be executed as part of the workflow.

    In this example, identify the record that is the subject of the
    workflow operation, and upload the Data Flow payload to that record.

    Replace the code in this module with your custom business logic.
    """
    payload = dataflow_integration.get_payload_as_dict()
    mi_session = dataflow_integration.mi_session

    db_key = payload["Record"]["Database"]
    db = mi_session.get_db(db_key=db_key)
    record_hguid = payload["Record"]["RecordHistoryGuid"]
    rec = db.get_record_by_id(hguid=record_hguid)

    # Write the json received from the dataflow API to the attribute
    # "Additional Processing Notes"
    data = dataflow_integration.get_payload_as_string(
        indent=True,
        include_credentials=False,
    )

    # To import the payload into a different attribute, change
    # the name here. Specify any long text attribute in the
    # table included in the workflow definition.
    attribute_name = "Additional Processing Notes"
    attribute = rec.attributes[attribute_name]
    attribute.value = data
    rec.set_attributes([attribute])

    # Update record database
    mi_session.update([rec])
    logger.info("Updated MI database")  # This output will be visible in the api/logs page


if __name__ == "__main__":
    # main()  # Used when running the script as part of a workflow
    testing()  # Used when testing the script manually
