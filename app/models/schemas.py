from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Ticket(BaseModel):
    id: str
    amountDue: float
    currency: str
    grace: int
    details: Optional[str] = None

class Settlement(BaseModel):
    amountPaid: float
    time: datetime
    receiptFields: dict

class Rebate(BaseModel):
    resultCode: str

class PlateLookup(BaseModel):
    ticketId: str
    confidence: float
    entryTime: datetime
    facility: str

class ManualTicket(BaseModel):
    surrogateId: str

class ManualTicketRequest(BaseModel):
    entryTime: datetime
    facilityId: str
    plate: str
    state: str
    evidence: List[str]

class DeviceState(BaseModel):
    deviceId: str
    status: str

class Counter(BaseModel):
    facilityId: str
    occupancy: int
