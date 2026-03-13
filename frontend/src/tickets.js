const listEl = document.getElementById("tickets-list");
const formEl = document.getElementById("new-ticket-form");
const btnNew = document.getElementById("btn-new-ticket");
const btnSubmit = document.getElementById("btn-submit-ticket");
const btnCancel = document.getElementById("btn-cancel-ticket");
const inputSubject = document.getElementById("new-subject");
const inputDesc = document.getElementById("new-description");
const inputPriority = document.getElementById("new-priority");
const filterSelect = document.getElementById("filter-status");

const STATUSES = ["open", "in_progress", "closed"];

let allTickets = [];

export function initTickets() {
  btnNew.addEventListener("click", () => formEl.classList.remove("hidden"));
  btnCancel.addEventListener("click", () => {
    formEl.classList.add("hidden");
    clearForm();
  });
  btnSubmit.addEventListener("click", createTicket);
  filterSelect.addEventListener("change", () => renderTickets());
  loadTickets();
  setInterval(loadTickets, 2000);
}

function clearForm() {
  inputSubject.value = "";
  inputDesc.value = "";
  inputPriority.value = "medium";
}

async function loadTickets() {
  const res = await fetch("/tickets");
  allTickets = await res.json();
  renderTickets();
}

function filteredTickets() {
  const filter = filterSelect.value;
  if (filter === "all") return allTickets;
  if (filter === "not_closed") return allTickets.filter((t) => t.status !== "closed");
  return allTickets.filter((t) => t.status === filter);
}

function renderTickets() {
  const tickets = filteredTickets();
  const existingById = new Map();
  for (const card of listEl.querySelectorAll(".ticket-card[data-id]")) {
    existingById.set(card.dataset.id, card);
  }

  // Remove the "no tickets" placeholder if present
  const placeholder = listEl.querySelector(".ticket-card:not([data-id])");
  if (placeholder) placeholder.remove();

  if (tickets.length === 0) {
    // Clear any leftover cards then show placeholder
    listEl.innerHTML = '<li class="ticket-card" style="color:var(--text-muted)">No tickets match filter.</li>';
    return;
  }

  const desiredIds = new Set(tickets.map((t) => String(t.id)));

  // Remove cards no longer in the list
  for (const [id, card] of existingById) {
    if (!desiredIds.has(id)) card.remove();
  }

  // Update existing or insert new cards in order
  let prev = null;
  for (const t of tickets) {
    const key = String(t.id);
    let card = existingById.get(key);
    if (card) {
      updateCard(card, t);
    } else {
      card = buildCard(t);
    }
    // Ensure correct order
    const currentNext = prev ? prev.nextElementSibling : listEl.firstElementChild;
    if (currentNext !== card) {
      if (prev) {
        prev.after(card);
      } else {
        listEl.prepend(card);
      }
    }
    prev = card;
  }
}

function updateCard(card, ticket) {
  const priorityClass = `badge-${ticket.priority}`;

  card.querySelector(".ticket-subject").textContent = ticket.subject;
  card.querySelector(".ticket-desc").textContent = ticket.description;

  const badge = card.querySelector(".badge");
  badge.className = `badge ${priorityClass}`;
  badge.textContent = ticket.priority;

  const sel = card.querySelector('[data-action="status"]');
  if (sel.value !== ticket.status && document.activeElement !== sel) {
    sel.value = ticket.status;
  }
}

function buildCard(ticket) {
  const li = document.createElement("li");
  li.className = "ticket-card";
  li.dataset.id = ticket.id;

  const priorityClass = `badge-${ticket.priority}`;

  li.innerHTML = `
    <div class="ticket-header">
      <span class="ticket-subject">${esc(ticket.subject)}</span>
      <span class="ticket-id">#${ticket.id}</span>
    </div>
    <div class="ticket-desc">${esc(ticket.description)}</div>
    <div class="ticket-actions">
      <span class="badge ${priorityClass}">${esc(ticket.priority)}</span>
      <select data-action="status">
        ${STATUSES.map(
          (s) => `<option value="${s}"${s === ticket.status ? " selected" : ""}>${statusLabel(s)}</option>`
        ).join("")}
      </select>
      <button class="danger" data-action="delete">Delete</button>
    </div>
  `;

  li.querySelector('[data-action="status"]').addEventListener("change", (e) =>
    changeStatus(ticket.id, e.target.value)
  );
  li.querySelector('[data-action="delete"]').addEventListener("click", () =>
    deleteTicket(ticket.id)
  );

  return li;
}

function statusLabel(s) {
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function esc(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

async function createTicket() {
  const subject = inputSubject.value.trim();
  const description = inputDesc.value.trim();
  if (!subject || !description) return;

  btnSubmit.disabled = true;
  await fetch("/tickets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      subject,
      description,
      priority: inputPriority.value,
    }),
  });
  btnSubmit.disabled = false;
  formEl.classList.add("hidden");
  clearForm();
  loadTickets();
}

async function changeStatus(id, status) {
  await fetch(`/tickets/${encodeURIComponent(id)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  loadTickets();
}

async function deleteTicket(id) {
  await fetch(`/tickets/${encodeURIComponent(id)}`, { method: "DELETE" });
  loadTickets();
}
