# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
MI Data Flow Toolkit module.

Provides generic functionality for parsing step information provided by Data Flow.
Allows direct access to this data or supports spawning a Scripting Toolkit session.
"""

import base64
import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict, Tuple, Type, TypeVar, cast
from urllib.parse import urlparse
import warnings

from ansys.openapi.common import ApiClientFactory, SessionConfiguration
import requests  # type: ignore[import-untyped]

try:
    from requests_negotiate_sspi import HttpNegotiateAuth  # type: ignore
except ImportError:
    pass

try:
    from GRANTA_MIScriptingToolkit import granta as mpy  # type: ignore
except ImportError:
    pass


def _get_dataflow_logger(logger_level: int) -> logging.Logger:
    r"""
    Return a logger with an attached StreamHandler.

    Parameters
    ----------
    logger_level : int
        The level to use for the logger. See the documentation in the Python logging
        module for more details.

    Returns
    -------
    logging.Logger
        The logger with attached StreamHandler.

    Notes
    -----
    The StreamHandler is selected because it outputs the log to stdout. This means the
    log can be accessed in the following locations:

    - The console, when running in a testing mode
    - The Data Flow server: C:\windows\TEMP\{}\__stdout__
    - The Data Flow API, at http://my.server.name/mi_dataflow/api/logs (MI 2023R2+) or
       http://my.server.name/mi_workflow_2/api/logs (MI 2023R1 or earlier)
    """
    logger = logging.getLogger("MIDataFlowIntegration")
    logger.level = logger_level
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    if not bool(logger.handlers):
        ch = logging.StreamHandler()
        ch.setLevel(logger_level)
        ch.setFormatter(formatter)
        ch.setStream(sys.stdout)
        logger.addHandler(ch)
    return logger


PyGranta_Connection_Class = TypeVar("PyGranta_Connection_Class", bound=ApiClientFactory)


class MIDataflowIntegration:
    """
    Represents a MI Data Flow session.

    When this class is instantiated, it parses the data provided by Data Flow, enabling Granta MI API client sessions
    to be created.

    Parameters
    ----------
    logging_level : int
        The logging level to apply to the logger.
    use_https : bool, optional
        Whether to use HTTPS if supported by the Granta MI server. Default is ``True``.
    verify_ssl : bool, optional
        Whether to verify the SSL certificate CA. Default is ``True``. Has no effect if ``use_https`` is set to
        ``False``.
    certificate_filename : str | None, optional
        The filename of the CA certificate file. Default is ``None``, which means the certifi public CA store will be
        used. Has no effect if ``use_https`` is set to ``False``.
    dataflow_payload : Dict[str, Any] | None, optional
        A dictionary containing a static copy of a payload previously provided by Data Flow via stdin. Used for testing
        purposes to validate business logic without having to provide the input via stdin. Default is ``None``, which
        means the input will be read from stdin.

    Warns
    -----
    UserWarning
        If ``use_https`` is set to ``True`` and the server does not support HTTPS.

    Notes
    -----
    When a workflow is configured to call a Python script, the workflow execution will be suspended whilst the Python
    script executes. To enable the workflow to continue, call the ``resume_bookmark`` method.

    The following sets of parameters are recommended for common Granta MI deployment configurations:

    * If HTTPS **is not** configured on the server, specify ``use_https = False``.
    * If HTTPS **is** configured on the server with an **internal certificate** and the private CA certificate
      **is not** available, specify ``use_https = False`` or ``use_https = True`` (default) and ``verify_ssl = False``.
    * If HTTPS **is** configured on the server with an **internal certificate** and the private CA certificate **is**
      available, specify ``use_https = True`` (default), ``verify_ssl = True`` (default), and
      ``certificate_filename = "certificate_filename.crt"``.
    * If HTTPS **is** configured on the server with a **public certificate**, specify ``use_https = True`` (default),
      ``verify_ssl = True`` (default), and ``certificate_filename = None`` (default).
    """

    def __init__(
        self,
        logging_level: int = logging.DEBUG,
        use_https: bool = True,
        verify_ssl: bool = True,
        certificate_filename: str | None = None,
        dataflow_payload: Dict[str, Any] | None = None,
    ) -> None:

        # Define properties
        self._logging_level = logging_level

        self._mi_session: mpy.Session | None = None

        # Logger
        self.logger = _get_dataflow_logger(self._logging_level)

        self.logger.debug("")
        self.logger.debug("---------- NEW RUN ----------")

        # Get data from data flow
        if dataflow_payload:
            self.logger.debug('Using data provided in "dataflow_payload"')
            self.df_data = dataflow_payload
        else:
            self.logger.debug("Using data provided in by MI Data Flow")
            self.df_data = self._get_standard_input()
            self.logger.debug(f"Dataflow data received: {json.dumps(self.df_data)}")

        # Parse url
        self.logger.debug("Parsing Data Flow URL")
        url = self.df_data["WorkflowUrl"]
        parsed_url = urlparse(url)
        self._hostname = parsed_url.netloc
        self._dataflow_path = parsed_url.path

        # Configure HTTPS
        server_supports_https = parsed_url.scheme == "https"

        # Check requested HTTPS config is compatible with server
        if use_https and not server_supports_https:
            warnings.warn(
                '"use_https" is set to True, but Granta MI server did not provide an https Data Flow url. Either '
                'specify "use_https=False" in the constructor for this class, or ensure that https is properly '
                "configured on the Granta MI server."
            )
        self._https_enabled = use_https and server_supports_https

        self._verify_ssl = verify_ssl
        self._ca_path = None

        # HTTPS is disabled. Nothing to configure.
        if not self._https_enabled:
            self.logger.debug("HTTPS is not enabled. Using plain HTTP.")

        # HTTPS is enabled, but verification is disabled.
        elif not verify_ssl:
            self.logger.debug("Certificate verification is disabled.")

        # HTTPS is enabled, verification is enabled, and a CA certificate has been provided
        elif certificate_filename:
            self.logger.debug(f"CA certificate '{certificate_filename}' provided.")
            self._ca_path = Path().cwd() / certificate_filename
            if not self._ca_path.is_file():
                raise FileNotFoundError(
                    f'CA certificate "{certificate_filename}" not found. Ensure the filename is '
                    "correct and that the certificate was included in the Workflow definition "
                    "and try again."
                )

        # HTTPS is enabled, verification is enabled, and no CA certificate has been provided
        else:
            self.logger.debug(
                "No CA certificate provided. Using public CAs to verify certificates."
            )

    @property
    def service_layer_url(self) -> str:
        """
        The URL to the Granta MI service layer.

        The URL scheme is set to ``https`` if both the server supports HTTPS and ``use_https = True`` was specified in
        the constructor. Otherwise, the URL scheme is set to ``http``.

        Returns
        -------
        str
            URL to the service layer.
        """
        if self._https_enabled:
            return f"https://{self._hostname}/mi_servicelayer"
        else:
            return f"http://{self._hostname}/mi_servicelayer"

    @property
    def _dataflow_url(self) -> str:
        """
        The URL to Granta MI Data Flow.

        The URL scheme is set to ``https`` if both the server supports HTTPS and ``use_https = True`` was specified in
        the constructor. Otherwise, the URL scheme is set to ``http``.

        Returns
        -------
        str
            URL to Granta MI Data Flow.
        """
        if self._https_enabled:
            return f"https://{self._hostname}/{self._dataflow_path}"
        else:
            return f"http://{self._hostname}/{self._dataflow_path}"

    @property
    def mi_session(self) -> "mpy.Session":
        """
        An MI Scripting Toolkit session which can be used to interact with Granta MI.

        Requires a supported version of MI Scripting Toolkit to be installed.

        Returns
        -------
        mpy.Session
            MI Scripting Toolkit session.

        Raises
        ------
        MissingClientModuleException
            If Scripting Toolkit cannot be imported.
        """
        if self._mi_session is not None:
            return self._mi_session
        try:
            self._mi_session = self._start_stk_session_from_dataflow_credentials()
        except NameError as e:
            raise MissingClientModuleException(
                "Could not find Scripting Toolkit. Ensure Scripting Toolkit is installed "
                "and try again."
            ) from e
        return self._mi_session

    def _start_stk_session_from_dataflow_credentials(self) -> "mpy.Session":
        """
        Create a Scripting Toolkit session based on the Data Flow authentication.

        The credentials provided by Data Flow are re-used, and so explicit credentials are
        not required.

        Returns
        -------
        mpy.Session
            A Scripting Toolkit session object.
        """
        self.logger.debug("Creating MI Scripting Toolkit session.")

        client_credential_type = self.df_data["ClientCredentialType"]

        if client_credential_type == "Basic":
            self.logger.debug("Using Basic authentication.")
            username, password = self._get_basic_creds()
            session = mpy.connect(self.service_layer_url, user_name=username, password=password)

        elif client_credential_type == "None":
            self.logger.debug("Using OIDC authentication.")
            access_token = self._get_oidc_token()
            session = mpy.connect(self.service_layer_url, oidc=True, auth_token=access_token)

        elif client_credential_type == "Windows" and sys.platform == "win32":
            self.logger.debug("Using Windows authentication.")
            session = mpy.connect(self.service_layer_url, autologon=True)

        elif client_credential_type == "Windows" and sys.platform != "win32":
            raise NotImplementedError("Windows auth available on Windows only.")

        else:
            raise NotImplementedError(f'Unknown credentials type "{client_credential_type}"')

        return session

    def configure_pygranta_connection(
        self,
        pygranta_connection_class: Type[PyGranta_Connection_Class],
    ) -> PyGranta_Connection_Class:
        """
        Configure a PyGranta connection object with credentials provided by Data Flow.

        Parameters
        ----------
        pygranta_connection_class : Type[PyGranta_Connection_Class]
            The Connection class to use to create the client object. Must be a **class**, not an
            instance of a class. Must be a PyGranta connection class, which is defined as a subclass
            of the base :class:`~ansys.openapi.common.ApiClientFactory` class.

        Returns
        -------
        PyGranta_Connection_Class
            A configured Connection object corresponding to the provided class. Call the ``.connect()``
            method to finalize the connection.

        Raises
        ------
        TypeError
            If the class provided to this method is not a subclass of
            :class:`~ansys.openapi.common.SessionConfiguration`.

        Examples
        --------
        >>> from ansys.grantami.jobqueue import Connection
        >>> data_flow = MIDataflowIntegration()
        >>> connection = data_flow.configure_pygranta_connection(Connection)
        >>> client = connection.connect()
        >>> client
        <JobQueueApiClient: url: http://my_mi_server/mi_servicelayer>
        """
        self.logger.debug("Creating PyGranta client.")

        if not issubclass(pygranta_connection_class, ApiClientFactory):
            raise TypeError(
                '"pygranta_connection_class" must be a subclass of ansys.openapi.common.ApiClientFactory'
            )

        config = SessionConfiguration(
            cert_store_path=str(self._ca_path),
            verify_ssl=self._verify_ssl,
        )
        # We rename the first argument from 'api_url' to 'servicelayer_url', so use a positional
        # argument to avoid type errors.
        builder = pygranta_connection_class(self.service_layer_url, session_configuration=config)

        client_credential_type = self.df_data["ClientCredentialType"]

        if client_credential_type == "Basic":
            self.logger.debug("Using Basic authentication.")
            username, password = self._get_basic_creds()
            return builder.with_credentials(username=username, password=password)

        elif client_credential_type == "None":
            self.logger.debug("Using OIDC authentication.")
            access_token = self._get_oidc_token()
            return builder.with_oidc().with_token(access_token)  # type: ignore[return-value]

        elif client_credential_type == "Windows" and sys.platform == "win32":
            self.logger.debug("Using Windows authentication.")
            return builder.with_autologon()

        elif client_credential_type == "Windows" and sys.platform != "win32":
            raise NotImplementedError("Windows auth available on Windows only.")

        else:
            raise NotImplementedError(f'Unknown credentials type "{client_credential_type}".')

    def _get_basic_creds(self) -> Tuple[str, str]:
        """
        Extract the username and password from the basic authorization header.

        Returns
        -------
        Tuple[str, str]
            A 2-tuple of the username and password.
        """
        auth_header = self.df_data["AuthorizationHeader"]
        decoded = base64.b64decode(auth_header[6:])
        index = decoded.find(b":")
        username = decoded[:index].decode(encoding="utf-8")
        password = decoded[index + 1 :].decode(encoding="utf-8")
        return username, password

    def _get_oidc_token(self) -> str:
        """
        Extract the OIDC access token from the authorization header.

        Returns
        -------
        str
            The OIDC access token.
        """
        auth_header = cast(str, self.df_data["AuthorizationHeader"])
        access_token = auth_header[7:]
        return access_token

    def _get_standard_input(self) -> dict[str, Any]:
        """
        Parse the data payload from Data Flow to a dictionary.

        Returns
        -------
        dict[str, Any]
            The parsed payload from Data Flow.
        """
        return cast(dict[str, Any], json.load(sys.stdin))

    def _get_workflow_id(self, data: dict[str, Any]) -> str:
        """
        Extract the workflow ID from the parsed data payload.

        Parameters
        ----------
        data : dict[str, Any]
            The parsed payload from Data Flow.

        Returns
        -------
        str
            The workflow ID.
        """
        return cast(str, data["WorkflowId"])

    def resume_bookmark(self, exit_code: str | int) -> None:
        """
        Call the Data Flow API to allow the MI Data Flow step to continue.

        Parameters
        ----------
        exit_code : str | int
            An exit code to inform Data Flow of success or otherwise of the business logic script.
        """
        self.logger.debug(f"Returning control to MI Data Flow with exit code {exit_code}")
        headers = {"Content-Type": "application/json"}
        response_data = json.dumps(
            {
                "Values": {"ExitCode": exit_code},
                "WorkflowDefinitionName": self.df_data["WorkflowDefinitionId"],
                "TransitionName": self.df_data["TransitionName"],
            }
        ).encode("utf-8")

        verify_argument = self._verify_ssl if self._ca_path is None else self._ca_path
        self.logger.debug(f"Resuming bookmark using URL {self._dataflow_url}")

        request_url = f"{self._dataflow_url}/api/workflows/{self._get_workflow_id(self.df_data)}"
        if self.df_data["ClientCredentialType"] in ["Basic", "None"]:
            # MI server setup: Basic authentication or OIDC authentication
            headers["Authorization"] = self.df_data["AuthorizationHeader"]
            response = requests.post(
                url=request_url,
                data=response_data,
                headers=headers,
                verify=verify_argument,
            )
        else:
            # MI server setup: Windows authentication
            response = requests.post(
                url=request_url,
                data=response_data,
                auth=HttpNegotiateAuth(),
                headers=headers,
                verify=verify_argument,
            )
        response.raise_for_status()


class MissingClientModuleException(ImportError):
    """Raised when a client API module is expected but could not be imported."""

    pass
