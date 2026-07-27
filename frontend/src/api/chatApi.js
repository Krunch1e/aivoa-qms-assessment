const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

/**
 * Sends a chat message (and optional file) to the backend.
 * Always uses multipart/form-data so the file-upload and plain-text
 * paths share one request shape — matches routers/chat.py.
 *
 * @param {string} message
 * @param {object|null} currentComplaint - current Redux complaint state
 * @param {File|null} file
 */
export async function sendChatMessage(message, currentComplaint, file) {
  const form = new FormData();
  form.append("message", message);
  if (currentComplaint) {
    form.append("current_complaint", JSON.stringify(currentComplaint));
  }
  if (file) {
    form.append("file", file);
  }

  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    throw new Error(`Chat request failed: ${res.status}`);
  }

  return res.json(); // { reply, complaint, tool_used }
}

export async function commitComplaint(complaint) {
  const res = await fetch(`${API_BASE}/commit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(complaint),
  });

  if (!res.ok) {
    throw new Error(`Commit failed: ${res.status}`);
  }

  return res.json();
}
