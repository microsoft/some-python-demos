from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastapi_demo import db


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Helpdesk Tickets", lifespan=lifespan)


class TicketCreate(BaseModel):
    subject: str
    description: str
    priority: str = "medium"


class TicketUpdate(BaseModel):
    subject: str | None = None
    description: str | None = None
    priority: str | None = None
    status: TicketStatus | None = None


class Ticket(TicketCreate):
    id: int
    status: TicketStatus = TicketStatus.open


@app.post("/tickets", response_model=Ticket, status_code=201)
def create_ticket(body: TicketCreate):
    return db.create_ticket(**body.model_dump())


@app.get("/tickets", response_model=list[Ticket])
def list_tickets():
    return db.list_tickets()


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: int):
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.patch("/tickets/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: int, body: TicketUpdate):
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=422, detail="No fields to update")
    ticket = db.update_ticket(ticket_id, **updates)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int):
    if not db.delete_ticket(ticket_id):
        raise HTTPException(status_code=404, detail="Ticket not found")
