
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.jwt_bearer import JWTBearer
from app.services.Hit_Services import send_hit_purchase_request, send_hit_refund_request, send_hit_unmatched_refund_request, send_hit_reversal_request, send_hit_status_request, send_hit_receipt_request, send_hit_enterdata_request, send_hit_generic_request, send_hit_ui_button_request

router = APIRouter(
    prefix="/hit",
    tags=["Windcave HIT"],
    dependencies=[Depends(JWTBearer())]
)

class PurchaseRequest(BaseModel):
    amount: float
    currency: str
    station: str
    txnRef: str
    deviceId: str
   
    user: str
    key: str
    posName: str | None = None
    posVersion: str | None = None
    vendorId: str | None = None
    mref: str | None = None


class RefundRequest(BaseModel):
    amount: float
    currency: str
    station: str
    txnRef: str
    dpsTxnRef: str        # REQUIRED for matched refund
    deviceId: str
    posName: str = ""
    vendorId: str = ""
    mref: str = ""
    user: str
    key: str



class UnmatchedRefundRequest(BaseModel):
    amount: float
    currency: str
    station: str
    txnRef: str
    deviceId: str
    posName: str
    vendorId: str
    mref: str
    user: str
    key: str


class ReversalRequest(BaseModel):
    txnRef: str
    station: str
    user: str
    key: str


class StatusRequest(BaseModel):
    txnRef: str
    station: str
    user: str
    key: str

class ReceiptRequest(BaseModel):
    txnRef: str
    station: str
    user: str
    key: str
    duplicateFlag: Optional[int] = 0  # default 0
    receiptType: int  # required, 1, 2, or 3



class ReceiptPrintRequest(BaseModel):
    station: str
    txnRef: str
    receiptType: int  # 1=Merchant, 2=Customer
    duplicateFlag: int = 0
    printer: str = None
    user: str
    key: str


class EnterDataRequest(BaseModel):
    station: str
    cmdSeq: int
    promptId: int
    timeout: int
    user: str
    key: str

class PinpadDisplayRequest(BaseModel):
    station: str
    cmdSeq: int
    promptId: int
    param1: str
    param2: str
    timeout: int
    user: str
    key: str


class ReadCardRequest(BaseModel):
    station: str
    txnRef: str
    user: str
    key: str


class SettlementSummaryRequest(BaseModel):
    station: str
    user: str
    key: str


class PingRequest(BaseModel):
    user: str
    key: str


class UIButtonRequest(BaseModel):
    station: str
    name: str          # "B1" or "B2"
    val: str           # "YES" | "NO" | "CANCEL"
    txnRef: str
    user: str
    key: str

 # Validation
    @classmethod
    def validate_name(cls, value):
        if value not in ["B1", "B2"]:
            raise ValueError("name must be B1 or B2")
        return value

    @classmethod
    def validate_val(cls, value):
        if value not in ["YES", "NO", "CANCEL"]:
            raise ValueError("val must be YES, NO, or CANCEL")
        return value

    # Override validation steps
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_all

    @classmethod
    def validate_all(cls, values):
        if values.get("name") not in ["B1", "B2"]:
            raise ValueError("Invalid name — allowed values: B1, B2")
        if values.get("val") not in ["YES", "NO", "CANCEL"]:
            raise ValueError("Invalid val — allowed: YES, NO, CANCEL")
        return values

@router.post("/purchase")
async def do_purchase(request: PurchaseRequest):
    try:
        result = await send_hit_purchase_request(request.dict())
        return {
            "status": "success",
            "windcave": result   # JSON parsed from XML
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/refund")
async def do_refund(request: RefundRequest):
    try:
        result = await send_hit_refund_request(request.dict())
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/refund/unmatched")
async def do_unmatched_refund(request: UnmatchedRefundRequest):
    try:
        result = await send_hit_unmatched_refund_request(request.dict())
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/reversal")
async def do_reversal(request: ReversalRequest):
    try:
        result = await send_hit_reversal_request(request.dict())
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/status")
async def check_status(request: StatusRequest):
    try:
        result = await send_hit_status_request(request.dict())
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/receipt")
async def get_receipt(request: ReceiptRequest):
    try:
        result = await send_hit_receipt_request(request.dict())
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/receipt-print")
async def receipt_print(req: ReceiptPrintRequest):
    try:
        result = await send_hit_receipt_request(req.dict(), action="Print")
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post("/enter-data")
async def enter_data(req: EnterDataRequest):
    try:
        result = await send_hit_enterdata_request(req.dict())
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/pinpad_display")
async def pinpad_display(request: PinpadDisplayRequest):
    try:
        result = await send_hit_generic_request(
            txn_type="PinpadDisplay",
            data=request.dict()
        )
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def read_card(request: ReadCardRequest):
    try:
        result = await send_hit_generic_request(
            txn_type="ReadCard",
            data=request.dict()
        )
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/settlement_summary")
async def settlement_summary(request: SettlementSummaryRequest):
    try:
        result = await send_hit_generic_request(
            txn_type="SettlementSummary",
            data=request.dict()
        )
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/ping")
async def ping(request: PingRequest):
    try:
        result = await send_hit_generic_request(
            txn_type="Ping",
            data=request.dict()
        )
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/ui/button")
async def ui_button_press(request: UIButtonRequest):
    try:
        result = await send_hit_ui_button_request(request.dict())
        return {
            "status": "success",
            "windcave": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/ui/button")
# async def send_ui_button(req: UIButtonRequest):
#     result = await send_hit_ui_button_request(req.dict())
#     return {"status": "success", "windcave": result}
