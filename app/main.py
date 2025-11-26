from fastapi import FastAPI
from app.routers import Customers, LogOff, Login, ServiceOperation, ShortCardNr, Hit_Integration, Plates, Ticket_Details, Tickets, Manual_Tickets, Ops
from dotenv import load_dotenv
import os
from app.routers.Login import router as login_router
from app.routers.LogOff import router as logoff_router
from app.Soap import login
app = FastAPI(title="Designa Gateway API")
load_dotenv()

app.include_router(login_router)
app.include_router(logoff_router)
app.include_router(Tickets.router)
app.include_router(Plates.router)
app.include_router(Manual_Tickets.router)
app.include_router(Ops.router)
# app.include_router(Login.app.router)
app.include_router(Customers.router)
app.include_router(ServiceOperation.router)
app.include_router(ShortCardNr.router)
app.include_router(Hit_Integration.router)
app.include_router(Ticket_Details.router)
# app.include_router(LogOff.app.router)
