from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Helpdesk Tickets")

# In-memory store
tickets: dict[int, dict] = {}
_next_id = 1


class TicketCreate(BaseModel):
    subject: str
    description: str
    priority: str = "medium"


class Ticket(TicketCreate):
    id: int
    status: str = "open"


@app.post("/tickets", response_model=Ticket, status_code=201)
def create_ticket(body: TicketCreate):
    global _next_id
    ticket = Ticket(id=_next_id, **body.model_dump())
    tickets[_next_id] = ticket.model_dump()
    _next_id += 1
    return ticket


@app.get("/tickets", response_model=list[Ticket])
def list_tickets():
    return list(tickets.values())


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: int):
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return tickets[ticket_id]


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int):
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")
    del tickets[ticket_id]
