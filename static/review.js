function reviewApi(path) {
  return new URL(path, window.location.origin).toString();
}

const rows = document.querySelector("#rows");
const empty = document.querySelector("#empty");
const note = document.querySelector("#expiry-note");
const systemErrors = document.querySelector("#system-errors");

function visibleReason(text) {
  if (!text) return "";
  if (/model request failed|no model is configured|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i.test(text)) {
    return "";
  }
  return text;
}

function dateLabel(value) {
  if (!value) return "";
  const date = new Date(value);
  return date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function expiryLabel(row, days) {
  if (row.status === "pending" || !row.status_set_at) {
    return "Pending rows stay until a status is set.";
  }
  const end = new Date(row.status_set_at);
  end.setDate(end.getDate() + days);
  return "Removed after " + dateLabel(end.toISOString());
}

function render(payload) {
  note.textContent = "A row is removed " + payload.expire_days + " days after its status is set. Pending rows are kept.";
  systemErrors.textContent = "System errors: " + payload.system_errors + ". No question text is stored with these.";
  rows.replaceChildren();
  const items = payload.reviews;
  empty.hidden = items.length > 0;
  for (const row of items) {
    const card = document.createElement("article");
    card.className = "review-row";
    const meta = document.createElement("p");
    meta.className = "meta";
    meta.textContent = dateLabel(row.created_at) + " · " + expiryLabel(row, payload.expire_days);
    const question = document.createElement("p");
    question.className = "reading";
    question.textContent = row.question || "Question omitted.";
    const reasonText = visibleReason(row.reason);
    const answer = document.createElement("p");
    answer.className = "reading";
    answer.textContent = (row.reply && row.reply.display_answer) || "";
    const form = document.createElement("form");
    const label = document.createElement("label");
    label.textContent = "Status ";
    const select = document.createElement("select");
    select.name = "status";
    for (const status of ["pending", "accepted", "rejected"]) {
      const option = document.createElement("option");
      option.value = status;
      option.textContent = status;
      option.selected = row.status === status;
      select.append(option);
    }
    label.append(select);
    const button = document.createElement("button");
    button.type = "submit";
    button.textContent = "Save";
    form.append(label, button);
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      button.disabled = true;
      const response = await fetch(reviewApi("/api/reviews/" + row.id), {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({status: select.value})
      });
      button.disabled = false;
      if (response.ok) load();
    });
    card.append(meta, question);
    if (reasonText) {
      const reason = document.createElement("p");
      reason.textContent = reasonText;
      card.append(reason);
    }
    card.append(answer, form);
    rows.append(card);
  }
}

async function load() {
  try {
    const response = await fetch(reviewApi("/api/reviews"));
    if (!response.ok) {
      empty.hidden = false;
      empty.textContent = "The review list could not be loaded.";
      return;
    }
    render(await response.json());
  } catch (error) {
    empty.hidden = false;
    empty.textContent = "The review list could not be loaded.";
  }
}

load();
