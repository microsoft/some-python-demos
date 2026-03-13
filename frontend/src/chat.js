const messagesEl = document.getElementById("chat-messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("chat-input");

let sessionId = null;

export function initChat() {
  formEl.addEventListener("submit", onSubmit);
}

function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showTyping() {
  const div = document.createElement("div");
  div.className = "chat-msg assistant";
  div.id = "typing-indicator";
  div.innerHTML = '<span class="spinner"></span>';
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}

async function onSubmit(e) {
  e.preventDefault();
  const text = inputEl.value.trim();
  if (!text) return;

  appendMessage("user", text);
  inputEl.value = "";
  inputEl.disabled = true;
  showTyping();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: sessionId,
      }),
    });

    removeTyping();

    if (!res.ok) {
      appendMessage("assistant", `Error: ${res.status} ${res.statusText}`);
      return;
    }

    const data = await res.json();

    // Always adopt the latest session_id returned by the server
    if (data.session_id) {
      sessionId = data.session_id;
    }

    appendMessage("assistant", data.reply);
  } catch (err) {
    removeTyping();
    appendMessage("assistant", `Network error: ${err.message}`);
  } finally {
    inputEl.disabled = false;
    inputEl.focus();
  }
}
