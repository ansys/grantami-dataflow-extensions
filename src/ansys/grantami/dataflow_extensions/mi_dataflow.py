# Copyright (C) 2025 ANSYS, Inc. and/or its affiliates.
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
Granta MI Data Flow Extensions module.

Provides generic functionality for parsing step information provided by MI Data Flow.
Allows direct access to this data or supports spawning a MI Scripting Toolkit session.
"""

import base64
import copy
import enum
from io import StringIO
import json
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

from ._logger import logger

PyGranta_Connection_Class = TypeVar("PyGranta_Connection_Class", bound=ApiClientFactory)


class _AuthenticationMode(enum.Enum):
    """The authentication mode of the Granta MI server."""

    INTEGRATED_WINDOWS_AUTHENTICATION = "Windows"
    BASIC_AUTHENTICATION = "Basic"
    OIDC_AUTHENTICATION = "None"


class MIDataflowIntegration:
    r"""
    Represents a MI Data Flow step at the point at which the Python script is triggered.

    When this class is instantiated, it parses the data provided by MI Data Flow, enabling Granta MI API client sessions
    to be created.

    Parameters
    ----------
    use_https : bool, default ``True``
        Whether to use HTTPS if supported by the Granta MI application server.
    verify_ssl : bool, default ``True``
        Whether to verify the SSL certificate CA. Has no effect if ``use_https`` is set to ``False``.
    certificate_file : str | pathlib.Path | None, default ``None``
        The CA certificate file, provided as either a string or pathlib.Path object. This paraemter can be provided
        in the following ways:

        *  The filename of the certificate provided as a string. In this case, the certificate must be added to the
           workflow definition as a supporting file.
        *  The filename or relative path of the certificate provided as a pathlib.Path object. In this case, the
           certificate must be added to the workflow definition as a supporting file.
        *  The absolute path to the certificate. In this case, the certificate can be stored anywhere on disk, but it
           is recommended to store it in a location that will not be modified between workflows.
        *  ``None``. In this case, the `certifi <https://pypi.org/project/certifi/>`_ public CA store will be used.

        If specified, the certificate will be used to verify PyGranta and MI Data Flow requests. Has no effect if
        ``use_https`` or ``verify_ssl`` are set to ``False``.

    Raises
    ------
    json.JSONDecodeError
        If the string read from stdin is invalid JSON.
    KeyError
        If the JSON read from stdin does not conform to the correct data structure.

    Warns
    -----
    UserWarning
        If ``use_https`` is set to ``True`` and the server does not support HTTPS.

    Notes
    -----
    When a workflow is configured to call a Python script, the workflow execution will be suspended whilst the Python
    script executes. To enable the workflow to continue, call the ``resume_bookmark`` method.

    Examples
    --------
    If HTTPS **is not** configured on the server, disable HTTPS.

    >>> data_flow = MIDataflowIntegration(use_https=False)

    If HTTPS **is** configured on the server with an **internal certificate** and the private CA certificate
    **is not** available, either disable HTTPS or disable certificate verification.

    >>> data_flow = MIDataflowIntegration(use_https=False)
    >>> data_flow = MIDataflowIntegration(use_https=True, verify_ssl=False)

    If HTTPS **is** configured on the server with an **internal certificate** and the private CA certificate **is**
    available, provide the private CA certificate to use this certificate for verification. If the filename only is
    provided, then the certificate must be added to the workflow definition file in Data Flow Designer.

    >>> data_flow = MIDataflowIntegration(certificate_file="my_cert.crt")

    If the certificate is stored somewhere else on disk, it can be specified by using a pathlib.Path object. In this
    case, the certificate should not be added to the workflow definition file in Data Flow Designer.

    >>> cert = pathlib.Path(r"C:\dataflow_files\certificates\my_cert.crt")
    >>> data_flow = MIDataflowIntegration(certificate_file=cert)

    If HTTPS **is** configured on the server with a **public certificate**, use the default configuration to enable
    HTTPS and certificate verification against public CAs.

    >>> data_flow = MIDataflowIntegration()
    """

    def __init__(
        self,
        use_https: bool = True,
        verify_ssl: bool = True,
        certificate_file: str | Path | None = None,
    ) -> None:
        # Define properties
        self._supporting_files_dir = Path(sys.path[0])

        self._mi_session: mpy.Session | None = None

        # Logger
        logger.info("")
        logger.info("---------- Initializing new Data Flow Extensions instance ----------")

        # Get data from data flow. Getting the payload as a sanitized string performs a basic check that we have
        # an expected data structure.
        self._df_data = self._get_standard_input()
        sanitized_payload = self.get_payload_as_string(indent=False)
        logger.debug(f"Dataflow data received: {sanitized_payload}")

        # Parse url
        logger.debug("Parsing Data Flow URL")
        try:
            url = self._df_data["WorkflowUrl"]
        except KeyError as e:
            raise KeyError(
                'Key "WorkflowUrl" not found in provided payload. Ensure the payload is correct and try again.'
            ) from e
        parsed_url = urlparse(url)
        self._hostname = parsed_url.netloc
        self._dataflow_path = parsed_url.path
        logger.debug(f'Data Flow hostname: "{self._hostname}"')
        logger.debug(f'Data Flow path: "{self._dataflow_path}"')

        # Authentication method
        client_credential_type = self._df_data["ClientCredentialType"]
        try:
            self._authentication_mode = _AuthenticationMode(client_credential_type)
        except ValueError as e:
            raise NotImplementedError(f'Unknown ClientCredentialType "{client_credential_type}"') from e
        logger.debug(f'Authentication mode: "{self._authentication_mode.name}"')

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
        self._verify_ssl = self._https_enabled  # Verify if HTTPS is enabled unless explicitly disabled
        self._ca_path = None  # Use public certs by default

        if certificate_file is not None and not isinstance(certificate_file, (Path, str)):
            raise TypeError(
                f'Argument "certificate_file" must be of type pathlib.Path or str. '
                f"Value provided was of type {type(certificate_file)}."
            )

        # HTTP and OIDC is not supported
        if not self._https_enabled and self._authentication_mode == _AuthenticationMode.OIDC_AUTHENTICATION:
            raise ValueError("HTTPS cannot be disabled when using OIDC authentication.")

        # HTTPS is disabled. Nothing to configure.
        if not self._https_enabled:
            logger.debug("HTTPS is not enabled. Using plain HTTP.")

        # HTTPS is enabled, but verification is disabled.
        elif not verify_ssl:
            self._verify_ssl = False
            logger.debug("Certificate verification is disabled.")

        # HTTPS is enabled, verification is enabled, and a CA certificate has been provided as an absolute Path
        elif isinstance(certificate_file, Path) and certificate_file.is_absolute():
            logger.debug(f'CA certificate absolute file path "{certificate_file}" provided.')

            self._ca_path = certificate_file
            if self._ca_path.is_file():
                logger.debug(f'Successfully resolved file "{self._ca_path}"')
            else:
                raise FileNotFoundError(
                    f'CA certificate "{certificate_file}" not found. Ensure the path refers to a file on disk '
                    "and try again."
                )

        # A CA certificate has been provided as a string or a relative Path
        elif certificate_file is not None:
            if isinstance(certificate_file, str):
                value_type = "filename"
            else:
                value_type = "relative file path"

            logger.debug(f'CA certificate {value_type} "{certificate_file}" provided.')
            self._ca_path = self.supporting_files_dir / certificate_file
            if self._ca_path.is_file():
                logger.debug(f'Successfully resolved file "{self._ca_path}"')
            else:
                raise FileNotFoundError(
                    f'CA certificate "{certificate_file}" not found. Ensure the {value_type} is '
                    "correct, that the certificate was included in the Workflow definition, and that "
                    "the sys.path search path has not been modified."
                )

        # HTTPS is enabled, verification is enabled, and no CA certificate has been provided
        else:
            logger.debug("No CA certificate provided. Using public CAs to verify certificates.")

        logger.info("------------------- Initialization complete --------------------")

    @classmethod
    def from_dict_payload(
        cls,
        dataflow_payload: Dict[str, Any],
        **kwargs: Any,
    ) -> "MIDataflowIntegration":
        """
        Instantiate an :class:`~.MIDataflowIntegration` object with a static payload provided as a Python dictionary.

        Can be used for testing purposes to avoid needing to trigger the Python script from within Data Flow.
        See :meth:`~.MIDataflowIntegration.get_payload_as_dict` for information on generating a suitable payload.

        Parameters
        ----------
        dataflow_payload : Dict[str, Any]
            A Python dictionary containing a copy of a Data Flow data payload used for testing purposes.
        **kwargs
            Additional keyword arguments are passed to the :class:`~.MIDataflowIntegration` constructor.

        Returns
        -------
        MIDataflowIntegration
            The instantiated class.

        Examples
        --------
        >>> dataflow_payload = {"WorkflowId": "67eb55ff-363a-42c7-9793-df363f1ecc83", ...: ...}
        >>> df = MIDataflowIntegration.from_dict_payload(dataflow_payload)

        Additional parameters are passed through to the :class:`~MIDataflowIntegration` constructor

        >>> dataflow_payload = {"WorkflowId": "67eb55ff-363a-42c7-9793-df363f1ecc83", ...: ...}
        >>> df = MIDataflowIntegration.from_dict_payload(dataflow_payload, verify_ssl=False)
        """
        serialized_payload = json.dumps(dataflow_payload)
        sys.stdin = StringIO(serialized_payload)
        df = cls(**kwargs)
        return df

    @classmethod
    def from_string_payload(
        cls,
        dataflow_payload: str,
        **kwargs: Any,
    ) -> "MIDataflowIntegration":
        """
        Instantiate an :class:`~.MIDataflowIntegration` object with a static payload.

        provided as a JSON formatted string.

        Can be used for testing purposes to avoid needing to trigger the Python script from within Data Flow.
        See :meth:`~.MIDataflowIntegration.get_payload_as_string` for information on generating a suitable payload.

        Parameters
        ----------
        dataflow_payload : str
            A JSON-formatted static copy of a Data Flow
            data payload used for testing purposes.
        **kwargs
            Additional keyword arguments are passed to the :class:`~.MIDataflowIntegration` constructor.

        Returns
        -------
        MIDataflowIntegration
            The instantiated class.

        Raises
        ------
        ValueError
            If the ``dataflow_payload`` argument is not valid JSON.

        Examples
        --------
        >>> dataflow_payload = '{"WorkflowId": "67eb55ff-363a-42c7-9793-df363f1ecc83", ...: ...}'
        >>> df = MIDataflowIntegration.from_string_payload(dataflow_payload)

        Additional parameters are passed through to the :class:`~MIDataflowIntegration` constructor

        >>> dataflow_payload = '{"WorkflowId": "67eb55ff-363a-42c7-9793-df363f1ecc83", ...: ...}'
        >>> df = MIDataflowIntegration.from_string_payload(dataflow_payload, verify_ssl=False)
        """
        try:
            json.loads(dataflow_payload)
        except json.JSONDecodeError as e:
            raise ValueError(
                "'dataflow_payload' is not valid JSON. Ensure the dataflow_payload argument contains a valid JSON "
                "string and try again."
            ) from e
        sys.stdin = StringIO(dataflow_payload)
        df = cls(**kwargs)
        return df

    def get_payload_as_dict(self, include_credentials: bool = False) -> Dict[str, Any]:
        """
        Get the payload used to instantiate this class as a Python dictionary.

        This can be stored and provided to the :meth:`~.MIDataflowIntegration.from_dict_payload` method to test
        independently of MI Data Flow.

        Parameters
        ----------
        include_credentials : bool, default ``False``
            Whether to include the Basic or OIDC token header in the result.

        Returns
        -------
        str
            A static copy of a Data Flow data payload used for testing purposes.

        Notes
        -----
        By default the basic and OIDC authentication header ``AuthorizationHeader`` is replaced with the string
        ``"<HeaderRemoved>"`` to avoid leaking credentials. To construct the appropriate header manually:

        * For basic authentication, combine the username and password with a colon (``:``), Base64 encode the resulting
          string, and then prepend the result with `"Basic "`. For example, for the username ``Alice`` and password
          ``s3cr3t``, these are combined to give ``"Alice:s3cr3t"`` and Base64 encoded to ``"QWxpY2U6czNjcjN0"``, which
          gives the final ``AuthorizationHeader`` value of ``"Basic QWxpY2U6czNjcjN0"``.
        * For OIDC authentication, generate a valid access token and prepend with ``"Bearer "``. For example, for the
          token ``gaUDsgUrOiJSUzI``, the final ``AuthorizationHeader`` value would be ``"Bearer gaUDsgUrOiJSUzI"``.

        Alternatively, you can invoke this method with ``include_credentials=True``, however you **must** ensure that
        the result is stored securely to avoid leaking credentials.
        """
        data = copy.deepcopy(self._df_data)
        try:
            if not include_credentials and data["AuthorizationHeader"]:
                data["AuthorizationHeader"] = "<HeaderRemoved>"
        except KeyError as e:
            raise KeyError(
                'Key "AuthorizationHeader" not found in provided payload. Ensure the payload is correct and try again.'
            ) from e
        return data

    def get_payload_as_string(self, indent: bool = False, **kwargs: Any) -> str:
        """
        Get the payload used to instantiate this class and serialize to a JSON string.

        This can be stored and provided to the :meth:`~.MIDataflowIntegration.from_string_payload` method to test
        independently of MI Data Flow.

        This method uses the :meth:`.MIDataflowIntegration.get_payload_as_dict` method to prepare the dictionary. See
        the :meth:`.MIDataflowIntegration.get_payload_as_dict` documentation for more details and additional keyword
        arguments.

        Parameters
        ----------
        indent : bool, default ``False``
            Whether to indent the JSON representation of the payload. Useful if displaying the result.
        **kwargs
            Additional keyword arguments are passed to the :meth:`.MIDataflowIntegration.get_payload_as_dict` method.

        Returns
        -------
        str
            A static copy of a Data Flow data payload used for testing purposes.
        """
        data = self.get_payload_as_dict(**kwargs)
        if indent:
            return json.dumps(data, indent=4)
        else:
            return json.dumps(data)

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
            return f"https://{self._hostname}{self._dataflow_path}"
        else:
            return f"http://{self._hostname}{self._dataflow_path}"

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
                "Could not find Scripting Toolkit. Ensure Scripting Toolkit is installed " "and try again."
            ) from e
        return self._mi_session

    @property
    def supporting_files_dir(self) -> Path:
        """
        The directory containing the supporting files added to the workflow definition.

        Will always include the script executed by the workflow, but may contain additional scripts,
        CA certificates, and any other files as required by the business logic.

        Returns
        -------
        pathlib.Path
            The directory containing supporting files added to the workflow definition.
        """
        return self._supporting_files_dir

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
        logger.debug("Creating MI Scripting Toolkit session.")

        if self._authentication_mode == _AuthenticationMode.BASIC_AUTHENTICATION:
            logger.debug("Using Basic authentication.")
            username, password = self._get_basic_creds()
            session = mpy.connect(self.service_layer_url, user_name=username, password=password)

        elif self._authentication_mode == _AuthenticationMode.INTEGRATED_WINDOWS_AUTHENTICATION:
            logger.debug("Using Windows authentication.")
            session = mpy.connect(self.service_layer_url, autologon=True)

        elif self._authentication_mode == _AuthenticationMode.OIDC_AUTHENTICATION:
            logger.debug("Using OIDC authentication.")
            access_token = self._get_oidc_token()
            session = mpy.connect(self.service_layer_url, oidc=True, auth_token=access_token)

        else:
            raise NotImplementedError()

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
        NotImplementedError
            If the Granta MI server is configured with OIDC authentication.

        Warnings
        --------
        This method does not currently support OIDC. A workaround is to create the client manually and
        authenticate with a stored OIDC refresh token. See :class:`~ansys.openapi.common.OIDCSessionBuilder`
        for more details.

        Examples
        --------
        >>> from ansys.grantami.jobqueue import Connection
        >>> data_flow = MIDataflowIntegration()
        >>> connection = data_flow.configure_pygranta_connection(Connection)
        >>> client = connection.connect()
        >>> client
        <JobQueueApiClient: url: http://my_mi_server/mi_servicelayer>
        """
        logger.debug("Creating PyGranta client.")

        if not issubclass(pygranta_connection_class, ApiClientFactory):
            raise TypeError('"pygranta_connection_class" must be a subclass of ansys.openapi.common.ApiClientFactory')

        config = SessionConfiguration(
            cert_store_path=str(self._ca_path) if self._ca_path is not None else None,
            verify_ssl=self._verify_ssl,
        )
        # We rename the first argument from 'api_url' to 'servicelayer_url', so use a positional
        # argument to avoid type errors.
        builder = pygranta_connection_class(self.service_layer_url, session_configuration=config)

        if self._authentication_mode == _AuthenticationMode.BASIC_AUTHENTICATION:
            logger.debug("Using Basic authentication.")
            username, password = self._get_basic_creds()
            return builder.with_credentials(username=username, password=password)

        elif self._authentication_mode == _AuthenticationMode.INTEGRATED_WINDOWS_AUTHENTICATION:
            logger.debug("Using Windows authentication.")
            return builder.with_autologon()

        elif self._authentication_mode == _AuthenticationMode.OIDC_AUTHENTICATION:
            raise NotImplementedError("OIDC authentication is not supported with PyGranta packages.")

        else:
            raise NotImplementedError()

    def _get_basic_creds(self) -> Tuple[str, str]:
        """
        Extract the username and password from the basic authorization header.

        Returns
        -------
        Tuple[str, str]
            A 2-tuple of the username and password.
        """
        auth_header = self._df_data["AuthorizationHeader"]
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
        auth_header = cast(str, self._df_data["AuthorizationHeader"])
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
        logger.debug(f"Returning control to MI Data Flow with exit code {exit_code}")
        headers = {"Content-Type": "application/json"}
        response_data = json.dumps(
            {
                "Values": {"ExitCode": exit_code},
                "WorkflowDefinitionName": self._df_data["WorkflowDefinitionId"],
                "TransitionName": self._df_data["TransitionName"],
            }
        ).encode("utf-8")

        verify_argument = self._verify_ssl if self._ca_path is None else self._ca_path
        logger.debug(f"Resuming bookmark using URL {self._dataflow_url}")

        request_url = f"{self._dataflow_url}/api/workflows/{self._get_workflow_id(self._df_data)}"
        if self._authentication_mode in [
            _AuthenticationMode.OIDC_AUTHENTICATION,
            _AuthenticationMode.BASIC_AUTHENTICATION,
        ]:
            headers["Authorization"] = self._df_data["AuthorizationHeader"]
            response = requests.post(
                url=request_url,
                data=response_data,
                headers=headers,
                verify=verify_argument,
            )
        elif self._authentication_mode == _AuthenticationMode.INTEGRATED_WINDOWS_AUTHENTICATION:
            response = requests.post(
                url=request_url,
                data=response_data,
                auth=HttpNegotiateAuth(),
                headers=headers,
                verify=verify_argument,
            )
        else:
            raise NotImplementedError()
        response.raise_for_status()
        logger.info("---------------- Workflow successfully resumed -----------------")


class MissingClientModuleException(ImportError):  # noqa: N818
    """Raised when a client API module is expected but could not be imported."""

    pass
