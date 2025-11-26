
# app/utils.py
import os
import requests
from zeep import Client, Settings
from zeep.transports import Transport
from dotenv import load_dotenv

# ---------------------------------------------------------------------
# Load environment early to ensure WSDL URLs are available
# ---------------------------------------------------------------------
load_dotenv()


def get_soap_client(wsdl_env_key: str):
    """
    Returns a Zeep SOAP client for the given WSDL environment variable key.

    Args:
        wsdl_env_key (str): The name of the environment variable containing the WSDL URL.
                            Example: "DESIGNA_WSDL_CASHPOINT_URL"

    Returns:
        zeep.Client: Configured SOAP client ready for service calls.
    """
    wsdl_url = os.getenv(wsdl_env_key)
    if not wsdl_url:
        raise ValueError(f"Missing WSDL URL for environment key: {wsdl_env_key}")

    # Configure session
    session = requests.Session()

    # SSL verification toggle
    verify_ssl = os.getenv("DESIGNA_SSL_VERIFY", "True").lower() == "true"
    session.verify = verify_ssl

    # Optional: Log insecure warning suppression
    if not verify_ssl:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Configure Zeep transport and settings
    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)

    # Create SOAP client
    client = Client(wsdl=wsdl_url, transport=transport, settings=settings)
    return client
