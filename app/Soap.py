
# app/soap.py
from gettext import install
import os
import logging
import importlib
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import HTTPException
import pip
import pydantic
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from app.utils import get_soap_client
from datetime import UTC
from pydantic_settings import BaseSettings
from app.config import settings

from zeep import Client, Settings, Transport
from zeep.exceptions import Fault



# soap.py
from requests import Session
from zeep import Client, Settings as ZeepSettings
from zeep.transports import Transport


logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------
# Logger setup
# ---------------------------------------------------------------------
logger = logging.getLogger("app.soap")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s"))
    logger.addHandler(handler)



# ---------------------------------------------------------------------
# login
# ---------------------------------------------------------------------
def login(tcc_num: int, user_id: str = None, password: str = None) -> int:
    """
    Calls the DESIGNA SOAP operation 'login'.

    Args:
        tcc_num (int): The TCC (Terminal Control Center) number.
        user_id (str, optional): DESIGNA user ID. Defaults to DESIGNA_USER from env/settings.
        password (str, optional): DESIGNA password. Defaults to DESIGNA_PASSWORD from env/settings.

    Returns:
        int: Result code from DESIGNA (0 = success, negative = failure).
    """
    try:
        # Use credentials from .env or app.config if not explicitly provided
        user = user_id or settings.DESIGNA_USER
        pwd = password or settings.DESIGNA_PASSWORD

        if not user or not pwd:
            raise ValueError("Missing DESIGNA_USER or DESIGNA_PASSWORD.")

        # Prepare SOAP client
        client = get_soap_client("DESIGNA_WSDL_CASHPOINT_URL")

        logger.info(f"Calling login for TccNum={tcc_num}, UserId={user}")
        response = client.service.login(TccNum=tcc_num, UserId=user, pwd=pwd)

        # Convert response to Python type (usually an int)
        result = serialize_object(response)
        logger.info(f"login response: {result}")

        return result

    except Fault as f:
        logger.error(f"SOAP Fault in login: {f}")
        raise RuntimeError("Failed to log in to DESIGNA SOAP service") from f
    except Exception as e:
        logger.exception(f"Unexpected error in login: {e}")
        raise



# ---------------------------------------------------------------------
# deprecated
# ---------------------------------------------------------------------
def logoff(tcc_num: int) -> bool:
    """
    Calls the DESIGNA SOAP operation 'logoff'.

    Args:
        tcc_num (int): The TCC (Terminal Control Center) number.

    Returns:
        bool: True/False depending on the result from DESIGNA SOAP service.
    """
    try:
        client = get_soap_client("DESIGNA_WSDL_CASHPOINT_URL")

        logger.info(f"Calling deprecated for TccNum={tcc_num}")
        # response = client.service.deprecated(TccNum=tcc_num)
        response = client.service.logoff(TccNum=tcc_num)


        # Convert response to Python type
        result = serialize_object(response)
        logger.info(f"deprecated response: {result}")
        # Ensure result is boolean
        if isinstance(result, bool):
            return result
        elif isinstance(result, str):
            # SOAP may sometimes return 'true'/'false' as string
            return result.lower() == "true"
        else:
            raise RuntimeError(f"Unexpected SOAP response type: {type(result)}")

    except Fault as f:
        logger.error(f"SOAP Fault in deprecated: {f}")
        raise RuntimeError("Failed to call DESIGNA deprecated SOAP operation") from f
    except Exception as e:
        logger.exception(f"Unexpected error in deprecated: {e}")
        raise RuntimeError("Error occurred during deprecated SOAP call") from e


def get_amount_due(tcc_num: int, card_number: str) -> str:
    """Calls DESIGNA SOAP operation getAmountDue."""
    try:
        client = get_soap_client("DESIGNA_WSDL_CASHPOINT_URL")
        logger.info(f"Calling getAmountDue for CardNumber={card_number}, TccNum={tcc_num}")
        
        response = client.service.getAmountDue(TccNum=tcc_num, CardNumber=card_number)
        result = serialize_object(response)
        
        logger.info(f"getAmountDue raw response: {result}")

        # Check for null or error-like results
        if not result or (isinstance(result, dict)):
            raise RuntimeError(f"Invalid SOAP result: {result}")

        return result
    
        if isinstance(result, str) and "Error occured" in result:
            raise ValueError(f"Ticket not found or cannot calculate fee: {result}")

        return result

    except Fault as f:
        logger.error(f"SOAP Fault in get_amount_due: {f}")
        raise RuntimeError(f"SOAP Fault: {f}") from f
    except Exception as e:
        logger.exception(f"Unexpected error in get_amount_due: {e}")
        raise RuntimeError(f"Error occurred during getAmountDue: {e}") from e


# ---------------------------------------------------------------------
# set_rebate
# ---------------------------------------------------------------------
def set_rebate(card_number: str, discount_type: int, discount_value: int, discount_account: int) -> int:
    """Calls DESIGNA SOAP operation setRebate."""
    try:
        client = get_soap_client("DESIGNA_WSDL_CASHPOINT_URL")
        user = settings.DESIGNA_USER
        pwd = settings.DESIGNA_PASSWORD

        logger.info(
            f"Calling setRebate for CardNumber={card_number}, "
            f"DiscountType={discount_type}, Value={discount_value}, Account={discount_account}"
        )

        response = client.service.setRebate(
            UserID=user,
            UserPWD=pwd,
            CardNumber=card_number,
            DiscountType=discount_type,
            DiscountValue=discount_value,
            DiscountAccount=discount_account,
        )

        result = serialize_object(response)
        logger.info(f"setRebate response: {result}")
        return result
    except Fault as f:
        logger.error(f"SOAP Fault in set_rebate: {f}")
        raise RuntimeError("Failed to apply rebate") from f
    except Exception as e:
        logger.exception(f"Unexpected error in set_rebate: {e}")
        raise

# ---------------------------------------------------------------------
# set_card_settlement
# ---------------------------------------------------------------------
# def set_card_settlement(tcc_num: int, card_number: str, amount_paid: float) -> dict:
#     """Calls DESIGNA SOAP operation setCardSettlement."""
#     try:
#         user = settings.DESIGNA_USER
#         pwd = settings.DESIGNA_PASSWORD
#         client = get_soap_client("DESIGNA_WSDL_CASHPOINT_URL")
#         settlement_time = datetime.now(UTC).isoformat()

#         logger.info(
#             f"Calling setCardSettlement for CardNumber={card_number}, "
#             f"TccNum={tcc_num}, AmountPaid={amount_paid}, Time={settlement_time}"
#         )

#         response = client.service.setCardSettlement(
#             UserID=user,
#             UserPWD=pwd,
#             TccNum=tcc_num,
#             CardNumber=card_number,
#             SettlementTime=settlement_time,
#             AmountPaid=amount_paid,
#         )

#         result = serialize_object(response)
#         logger.info(f"setCardSettlement response: {result}")
#         return result
#     except Fault as f:
#         logger.error(f"SOAP Fault in set_card_settlement: {f}")
#         raise RuntimeError("Failed to perform card settlement") from f
#     except Exception as e:
#         logger.exception(f"Unexpected error in set_card_settlement: {e}")
#         raise



def set_card_settlement(tcc_num: int, card_number: str, amount_paid: float) -> dict:
    """Performs card settlement only if outstanding dues exist."""
    try:
        user = settings.DESIGNA_USER
        pwd = settings.DESIGNA_PASSWORD
        client = get_soap_client("DESIGNA_WSDL_CASHPOINT_URL")

        # Step 1: Fetch outstanding due
        amount_due_raw = get_amount_due(tcc_num, card_number)
        logger.info(f"[Payment Check] getAmountDue -> Card={card_number}, RawDue={amount_due_raw}")

        try:
            amount_due = float(amount_due_raw)
        except (ValueError, TypeError):
            # Invalid or non-numeric response from SOAP
            raise HTTPException(
                status_code=400,
                detail="Unable to determine outstanding due for this ticket. Please verify the ticket number or TCC."
            )

        # except (ValueError, TypeError):
        #     raise ValueError(f"Invalid amount due value returned: {amount_due_raw}")

        # Step 2: Validate payment logic
        if amount_due <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"No outstanding due for card {card_number}. Payment not required."
            )

        if amount_paid > amount_due:
            raise HTTPException(
                status_code=400,
                detail=f"Amount paid ({amount_paid}) exceeds outstanding due ({amount_due})."
            )

        # Step 3: Proceed with settlement
        settlement_time = datetime.now(UTC).isoformat()
        logger.info(
            f"[Settlement] Calling setCardSettlement for Card={card_number}, "
            f"TCC={tcc_num}, AmountPaid={amount_paid}, Time={settlement_time}"
        )

        response = client.service.setCardSettlement(
            UserID=user,
            UserPWD=pwd,
            TccNum=tcc_num,
            CardNumber=card_number,
            SettlementTime=settlement_time,
            AmountPaid=amount_paid,
        )

        result = serialize_object(response)
        logger.info(f"[Settlement] setCardSettlement response: {result}")

        return {
            "message": "Payment processed successfully.",
            "amount_due_before_payment": amount_due,
            "soap_response": result,
        }

    except Fault as f:
        logger.error(f"[SOAP Fault] set_card_settlement: {f}")
        raise HTTPException(status_code=502, detail="SOAP Fault during setCardSettlement")
    except HTTPException:
        # Already a clean client error, just re-raise it
        raise

    except Exception as e:
        logger.exception(f"[Error] Unexpected issue in set_card_settlement: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
# ---------------------------------------------------------------------
# set_cleared
# ---------------------------------------------------------------------
def set_cleared(tcc_num: int, card_number: str, user_id: str = None, password: str = None) -> str:
    """Calls DESIGNA SOAP operation setCleared."""
    try:
        user = user_id or settings.DESIGNA_USER
        pwd = password or settings.DESIGNA_PASSWORD
        client = get_soap_client("DESIGNA_WSDL_CASHPOINT_URL")

        logger.info(f"Calling setCleared for CardNumber={card_number}, TccNum={tcc_num}")
        response = client.service.setCleared(
            UserID=user,
            UserPWD=pwd,
            TccNum=tcc_num,
            CardNumber=card_number,
        )
        result = serialize_object(response)
        if not result or ("Error" in str(result)):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid or failed setCleared response: {result}"
            )
        logger.info(f"setCleared response: {result}")
        return result
    except Fault as f:
        logger.error(f"[SOAP Fault] setCleared: {f}")
        raise HTTPException(status_code=502, detail=f"SOAP Fault during setCleared: {f}")
    except HTTPException:
        raise  # pass through clean errors
    except Exception as e:
        logger.exception(f"[Unexpected Error] setCleared: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error during setCleared: {e}")


# ---------------------------------------------------------------------
# Function: calc_tariff
# ---------------------------------------------------------------------
def calc_tariff(
    carpark_nr: int,
    card_type: int,
    tariff_id: int,
    time_entry: datetime,
    time_exit: datetime,
) -> dict:
    """
    Calls the DESIGNA SOAP operation calcTariff to calculate parking fee.

    Args:
        carpark_nr (int): Carpark number.
        card_type (int): Type of card (e.g., 1 = ticket, 2 = season card, etc.)
        tariff_id (int): Tariff identifier for pricing rules.
        time_entry (datetime): Entry time of the vehicle.
        time_exit (datetime): Exit time of the vehicle.

    Returns:
        dict: Tariff calculation details (AmountDue, GracePeriod, etc.)
    """
    try:
        # Load credentials
        user_id = os.getenv("DESIGNA_USER")
        user_pwd = os.getenv("DESIGNA_PASSWORD")

        if not user_id or not user_pwd:
            raise ValueError("Missing DESIGNA_USER or DESIGNA_PASSWORD in environment.")

        # Prepare SOAP client
        client = get_soap_client("DESIGNA_WSDL_CASHPOINT_URL")

        # Ensure ISO format for datetime
        time_entry_iso = time_entry.isoformat()
        time_exit_iso = time_exit.isoformat()

        logger.info(
            f"Calling calcTariff for CarparkNr={carpark_nr}, CardType={card_type}, "
            f"TariffId={tariff_id}, TimeEntry={time_entry_iso}, TimeExit={time_exit_iso}"
        )

        # Call SOAP operation
        response = client.service.calcTariff(
            UserID=user_id,
            UserPWD=user_pwd,
            CarparkNr=carpark_nr,
            CardType=card_type,
            TariffId=tariff_id,
            TimeEntry=time_entry_iso,
            TimeExit=time_exit_iso,
        )

        result = serialize_object(response)
        logger.info(f"calcTariff response: {result}")
        return result

    except Fault as f:
        logger.error(f"SOAP Fault in calc_tariff: {f}")
        raise RuntimeError("Failed to calculate tariff") from f
    except Exception as e:
        logger.exception(f"Unexpected error in calc_tariff: {e}")
        raise




def get_card_by_carrier(user: str, pwd: str, card_carrier_nr: str):
    """
    Calls DESIGNA SOAP API: getCardByCarrier
    """
    try:
        client = get_soap_client("DESIGNA_WSDL_SERVICE_OPERATION_URL")
        response = client.service.getCardByCarrier(
            user=user,
            pwd=pwd,
            cardCarrierNr=card_carrier_nr
        )
        return response
    except Fault as fault:
        raise RuntimeError(f"SOAP Fault: {fault}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error calling SOAP: {e}")
    

def get_customer(user: str, pwd: str, person_id: int):
    """
    Calls DESIGNA SOAP API: getCustomer

    Args:
        user (str): DESIGNA username
        pwd (str): DESIGNA password
        person_id (int): Person ID to fetch customer data for

    Returns:
        dict: Customer details including name, address, and details list
    """
    try:
        client = get_soap_client("DESIGNA_WSDL_SERVICE_OPERATION_URL")

        logger.info(f"Calling getCustomer for PersonID={person_id}")

        # Call the SOAP method
        response = client.service.GetCustomer(
            user=user,
            pwd=pwd,
            personId=person_id
        )

        # Convert SOAP response to a serializable Python object
        result = serialize_object(response)
        logger.info(f"getCustomer raw SOAP response: {result}")

        if not result:
            raise RuntimeError("Empty SOAP response received from getCustomer.")

        # Handle expected structure (dict with nested Address + Details)
        customer_data = {
            "FirstName": result.get("FirstName"),
            "LastName": result.get("LastName"),
            "Address": result.get("Address", {}),
            "Details": result.get("Details", [])
        }

        return customer_data

    except Fault as fault:
        logger.error(f"SOAP Fault in get_customer: {fault}")
        raise RuntimeError(f"SOAP Fault calling getCustomer: {fault}") from fault
    except Exception as e:
        logger.exception(f"Unexpected error in get_customer: {e}")
        raise RuntimeError(f"Unexpected error calling getCustomer: {e}")

# ---------------------------------------------------------------------
# get_pm_string
# ---------------------------------------------------------------------
def get_pm_string(user: str, pwd: str, short_card_nr: str) -> str:
    """
    Calls DESIGNA SOAP API: getPMString
    Args:
        user (str): DESIGNA username
        pwd (str): DESIGNA password
        short_card_nr (str): Short card number (ticket or card ref)
    Returns:
        str: PM string result from DESIGNA SOAP
    """
    try:
        client = get_soap_client("DESIGNA_WSDL_SERVICE_OPERATION_URL")

        logger.info(f"Calling getPMString for ShortCardNr={short_card_nr}")

        # NOTE: SOAP operation name is case-sensitive
        response = client.service.getPMString(
            user=user,
            pwd=pwd,
            shortCardNr=short_card_nr
        )

        result = serialize_object(response)
        logger.info(f"getPMString SOAP response: {result}")

        if not result:
            raise RuntimeError("Empty response from getPMString")

        return result

    except Fault as fault:
        logger.error(f"SOAP Fault in get_pm_string: {fault}")
        raise RuntimeError(f"SOAP Fault calling getPMString: {fault}") from fault
    except Exception as e:
        logger.exception(f"Unexpected error in get_pm_string: {e}")
        raise RuntimeError(f"Unexpected error calling getPMString: {e}")
    

def get_Short_Card_Nr(short_card_nr: str) -> str:
    """
    Calls DESIGNA SOAP API: getPMString
    Args:
        user (str): DESIGNA username
        pwd (str): DESIGNA password
        short_card_nr (str): Short card number (ticket or card ref)
    Returns:
        str: PM string result from DESIGNA SOAP
    """
    try:
        client = get_soap_client("DESIGNA_WSDL_SERVICE_OPERATION_URL")

        logger.info(f"Calling getPMString for ShortCardNr={short_card_nr}")

        # NOTE: SOAP operation name is case-sensitive
        response = client.service.getPMString(
            shortCardNr=short_card_nr
        )

        result = serialize_object(response)
        logger.info(f"getPMString SOAP response: {result}")

        if not result:
            raise RuntimeError("Empty response from getPMString")

        return result

    except Fault as fault:
        logger.error(f"SOAP Fault in get_pm_string: {fault}")
        raise RuntimeError(f"SOAP Fault calling getPMString: {fault}") from fault
    except Exception as e:
        logger.exception(f"Unexpected error in get_pm_string: {e}")
        raise RuntimeError(f"Unexpected error calling getPMString: {e}")


def get_card_info(tcc_num: int, card_number: str):
    wsdl_url = os.getenv("DESIGNA_WSDL_CASHPOINT_URL")
    if not wsdl_url:
        raise RuntimeError("WSDL URL not configured in environment")

    # Prepare a requests Session to control SSL verification
    session = Session()
    verify_ssl = os.getenv("DESIGNA_SSL_VERIFY", "True").lower() in ("true", "1", "yes")
    session.verify = verify_ssl   # True or False based on .env

    transport = Transport(session=session, timeout=30)

    client = Client(
        wsdl=wsdl_url,
        transport=transport,
        settings=ZeepSettings(strict=False)
    )

    logger.info(f"Calling getCardInfo for TccNum={tcc_num}, CardNumber={card_number}")

    try:
        response = client.service.GetCardInfo(
            UserID=os.getenv("DESIGNA_USER"),
            UserPWD=os.getenv("DESIGNA_PASSWORD"),
            TccNum=tcc_num,
            CardNumber=card_number
        )
    except Fault as fault:
        logger.error(f"SOAP Fault in get_card_info: {fault}")
        raise RuntimeError(f"SOAP Fault calling getCardInfo: {fault}") from fault
    except Exception as e:
        logger.exception(f"Unexpected error in get_card_info: {e}")
        raise RuntimeError(f"Unexpected error calling getCardInfo: {e}")

    result = serialize_object(response)
    logger.info(f"getCardInfo SOAP response: {result}")

    if result is None:
        raise RuntimeError("Empty response from getCardInfo")

    return result


# ---------------------------------------------------------------------
# Local test entrypoint
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print(">> Running DESIGNA SOAP test sequence")
    TCC = int(settings.DESIGNA_TCC_ENTRY)
    CARD = "PM010100150101087927"

    try:
        # 🆕 Test deprecated
        # deprecated_result = deprecated(TCC)
        # print("Deprecated result:", deprecated_result)
        # 1️⃣ Test login
        login_result = login(TCC)
        print("Login result:", login_result)

        amount_due = get_amount_due(TCC, CARD)
        print("Amount due:", amount_due)

        rebate_result = set_rebate(CARD, 1, 10, 100)
        print("Rebate result:", rebate_result)

        settlement_result = set_card_settlement(TCC, CARD, 10.0)
        print("Settlement result:", settlement_result)

        cleared_result = set_cleared(TCC, CARD)
        print("Cleared result:", cleared_result)
    except Exception as e:
        print(f"Error: {e}")

    entry_time = datetime.now(timezone.utc) - timedelta(hours=2)
    exit_time = datetime.now(timezone.utc)

    tariff_result = calc_tariff(
        carpark_nr=1,
        card_type=1,
        tariff_id=1,
        time_entry=entry_time,
        time_exit=exit_time,
    )
    print("Tariff calculation result:", tariff_result)

