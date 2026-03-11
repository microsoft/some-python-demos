from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastapi_demo import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Helpdesk Tickets", lifespan=lifespan)


class TicketCreate(BaseModel):
    subject: str
    description: str
    priority: str = "medium"


class Ticket(TicketCreate):
    id: int
    status: str = "open"


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


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int):
    if not db.delete_ticket(ticket_id):
        raise HTTPException(status_code=404, detail="Ticket not found")
