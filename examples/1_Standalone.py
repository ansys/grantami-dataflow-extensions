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

# ## Introduction

# An example that uses the PyGranta Data Flow Framework to interact with a resource that
# isn't part of a standard Granta MI system.

# This example script logs the record identifying information, which is received from
# MI Data Flow. This could be replaced with any other business logic which can make use of the data provided by
# MI Data Flow. To perform operations that rely on additional information from a Granta MI system, see the other examples in this
# package.

# ### Useful links ###
# * [Recommended script structure](../user_guide/index.rst#recommended-script-structure)
# * [Business logic development best practice](../user_guide/index.rst#business-logic-development-best-practice)

# <div class="alert alert-warning">
#
# **Warning:**
#
# The `step_logic()` function generates the dataflow payload, and explicitly calls the `get_payload_as_str()` method
# with `include_credentials=False` to avoid logging credentials. If you are using Basic or OIDC
# Authentication and require these credentials for your business logic, inject these credentials into the
# `dataflow_payload["AuthorizationHeader"]` value in the `testing()` function directly, for example via an environment
# variable.
# </div>

# ## Example script

# +
import logging
import traceback

from ansys.grantami.dataflow_framework import MIDataflowIntegration

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
    """Contains the business logic to be run as part of the workflow.

    Replace the code in this module with your custom business logic."""

    # Get the payload from the integration option
    payload = dataflow_integration.get_payload_as_string(
        include_credentials=False,
    )

    # Log the payload. All log messages will appear in the Data Flow log.
    logger.info("Writing dataflow payload.")
    logger.info(payload)


if __name__ == "__main__":
    # main()  # Used when running the script as part of a workflow
    testing()  # Used when testing the script manually
