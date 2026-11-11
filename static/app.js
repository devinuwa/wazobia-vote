const ICONS = {
  "id-card": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="9" cy="12" r="2" fill="currentColor"/></svg>',
  "location-pin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="10" r="2" fill="currentColor"/></svg>',
  calendar: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 10h18M8 3v4M16 3v4" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
  clock: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 8v5l3 2" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
  phone: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3h3l1 4-2 1a12 12 0 0 0 6 6l1-2 4 1v3c0 1-1 2-2 2C10 18 6 14 4 5c0-1 1-2 2-2z" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
  "person-assist": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="7" r="2" fill="currentColor"/><path d="M4 20c1-4 3-6 5-6s4 2 5 6M16 11h4M18 9v4" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
  "ballot-box": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="9" width="16" height="10" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8 9V6h8v3M12 13v3" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
  check: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12l5 5L20 7" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
  warning: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 10v4M12 17h.01" stroke="currentColor" stroke-width="2"/></svg>',
  question: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2c-1 .6-1.5 1-1.5 2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="17" r="0.8" fill="currentColor"/></svg>',
  info: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 11v5M12 8h.01" stroke="currentColor" stroke-width="2"/></svg>',
  scope: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2"/><path d="M7 12h10" stroke="currentColor" stroke-width="2"/></svg>'
};

const STATUSES = {
  A: {label: "Verified from sources", className: "badge-verified", icon: "check"},
  B: {label: "Partly confirmed", className: "badge-partial", icon: "info"},
  C: {label: "Out of scope", className: "badge-scope", icon: "scope"},
  D: {label: "Not yet verified", className: "badge-unverified", icon: "warning"}
};

const form = document.querySelector("#ask-form");
const status = document.querySelector("#status");
const result = document.querySelector("#result");
const askButton = document.querySelector("#ask");
const askLabel = askButton.querySelector(".ask-label");
const question = document.querySelector("#question");
let currentReply = null;

function shareText(reply) {
  const lines = [reply.display_answer || ""];
  const citations = Array.isArray(reply.citations) ? reply.citations : [];
  if (citations.length) {
    lines.push("");
    lines.push("Sources");
    for (const citation of citations) {
      lines.push(citation.title || "");
      lines.push(citation.last_verified ? "Last checked " + citation.last_verified : "Last checked: not dated");
    }
  }
  return lines.join("\n").trim();
}

function rememberReply(reply) {
  currentReply = reply || null;
  const actions = document.querySelector("#answer-actions");
  if (actions) {
    actions.hidden = !currentReply;
  }
}

function selected(name) {
  return form.querySelector(`input[name="${name}"]:checked`).value;
}

function applyProfile() {
  document.body.className = "profile-" + selected("profile");
}

form.addEventListener("change", applyProfile);

function iconHtml(id) {
  return ICONS[id] || "";
}

function insertAtCursor(letter) {
  const start = question.selectionStart ?? question.value.length;
  const end = question.selectionEnd ?? question.value.length;
  question.value = question.value.slice(0, start) + letter + question.value.slice(end);
  const next = start + letter.length;
  question.setSelectionRange(next, next);
  question.focus();
}

document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => {
    question.value = button.dataset.question;
    if (button.dataset.ask === "yes") {
      form.requestSubmit();
      return;
    }
    question.focus();
  });
});

document.querySelectorAll("[data-letter]").forEach((button) => {
  button.addEventListener("click", () => insertAtCursor(button.dataset.letter));
});

function setStatus(message, isError) {
  status.hidden = !message;
  status.textContent = message || "";
  status.classList.toggle("is-error", Boolean(isError));
}

function showEvidence(items) {
  const block = document.querySelector("#evidence-block");
  const list = document.querySelector("#evidence");
  if (!block || !list) {
    return;
  }
  list.replaceChildren();
  const rows = Array.isArray(items) ? items : [];
  block.hidden = rows.length === 0;
  for (const item of rows) {
    const card = document.createElement("article");
    card.className = "evidence";
    const title = document.createElement("h3");
    title.textContent = item.title || "";
    const quote = document.createElement("p");
    quote.textContent = item.excerpt || "";
    card.append(title, quote);
    list.append(card);
  }
}

function showCouldNotAnswer(reply) {
  showEvidence([]);
  rememberReply(reply || {display_answer: "", citations: []});
  result.hidden = false;
  result.classList.add("is-fallback");
  const badge = document.querySelector("#badge");
  badge.className = "badge badge-failed";
  badge.replaceChildren();
  const icon = document.createElement("span");
  icon.className = "badge-icon";
  icon.innerHTML = iconHtml("warning");
  const label = document.createElement("span");
  label.textContent = "Could not get an answer";
  badge.append(icon, label);
  document.querySelector("#display").textContent = (reply && reply.display_answer) || "";
  document.querySelector("#steps").replaceChildren();
  document.querySelector("#steps-block").hidden = true;
  document.querySelector("#citations").replaceChildren();
  document.querySelector("#sources-block").hidden = false;
  document.querySelector("#empty-sources").hidden = false;
  document.querySelector("#review-note").hidden = true;
  const spoken = (reply && reply.spoken_answer) || "";
  document.querySelector("#speak").onclick = () => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(spoken);
    const language = selected("language");
    utterance.lang = language === "ha" ? "ha" : language === "ig" ? "ig" : "en";
    window.speechSynthesis.speak(utterance);
  };
  setStatus("Could not get an answer.", true);
}

function showReply(payload) {
  if (payload.status === "fallback") {
    showCouldNotAnswer(payload.reply);
    return;
  }
  const reply = payload.reply;
  showEvidence(payload.evidence);
  rememberReply(reply);
  const state = STATUSES[reply.outcome];
  if (!state) {
    showCouldNotAnswer(reply);
    return;
  }
  result.hidden = false;
  result.classList.remove("is-fallback");
  const badge = document.querySelector("#badge");
  badge.className = "badge " + state.className;
  badge.replaceChildren();
  const icon = document.createElement("span");
  icon.className = "badge-icon";
  icon.innerHTML = iconHtml(state.icon);
  const label = document.createElement("span");
  label.textContent = state.label;
  badge.append(icon, label);

  document.querySelector("#display").textContent = reply.display_answer;
  const steps = document.querySelector("#steps");
  const stepsBlock = document.querySelector("#steps-block");
  steps.replaceChildren();
  stepsBlock.hidden = reply.steps.length === 0;
  for (const step of reply.steps) {
    const item = document.createElement("li");
    item.className = "step";
    const stepIcon = document.createElement("span");
    stepIcon.innerHTML = iconHtml(step.icon);
    const text = document.createElement("span");
    text.textContent = step.text;
    item.append(stepIcon, text);
    steps.append(item);
  }

  const citations = document.querySelector("#citations");
  const sourcesBlock = document.querySelector("#sources-block");
  const emptySources = document.querySelector("#empty-sources");
  citations.replaceChildren();
  const hasSources = reply.citations.length > 0;
  sourcesBlock.hidden = false;
  emptySources.hidden = hasSources;
  for (const citation of reply.citations) {
    const item = document.createElement("li");
    const title = document.createElement("div");
    title.textContent = citation.title;
    item.append(title);
    if (citation.url && /^https?:\/\//i.test(citation.url)) {
      const link = document.createElement("a");
      link.href = citation.url;
      link.textContent = citation.url;
      link.rel = "noopener noreferrer";
      item.append(link);
    }
    const verified = document.createElement("div");
    verified.textContent = citation.last_verified
      ? "Last checked " + citation.last_verified
      : "Last checked: not dated";
    item.append(verified);
    citations.append(item);
  }

  const reviewNote = document.querySelector("#review-note");
  reviewNote.replaceChildren();
  if (reply.needs_human_review) {
    reviewNote.hidden = false;
    const noteIcon = document.createElement("span");
    noteIcon.innerHTML = iconHtml("warning");
    const noteText = document.createElement("span");
    noteText.textContent = "Needs review.";
    reviewNote.append(noteIcon, noteText);
  } else {
    reviewNote.hidden = true;
  }

  document.querySelector("#speak").onclick = () => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(reply.spoken_answer);
    const language = selected("language");
    utterance.lang = language === "ha" ? "ha" : language === "ig" ? "ig" : "en";
    window.speechSynthesis.speak(utterance);
  };
  setStatus("", false);
}

document.querySelector("#copy-answer").addEventListener("click", async () => {
  if (!currentReply) {
    return;
  }
  const text = shareText(currentReply);
  try {
    await navigator.clipboard.writeText(text);
    setStatus("Answer copied.", false);
  } catch (error) {
    setStatus("Copy failed. Select the answer and copy it.", true);
  }
});

document.querySelector("#share-whatsapp").addEventListener("click", () => {
  if (!currentReply) {
    return;
  }
  const url = "https://wa.me/?text=" + encodeURIComponent(shareText(currentReply));
  window.open(url, "_blank", "noopener,noreferrer");
});

document.querySelector("#report-answer").addEventListener("click", async () => {
  if (!currentReply) {
    return;
  }
  setStatus("Sending the report.", false);
  try {
    const response = await fetch("/api/report", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: question.value, reply: currentReply})
    });
    if (!response.ok) {
      setStatus("The report could not be saved.", true);
      return;
    }
    setStatus("Reported for review.", false);
  } catch (error) {
    setStatus("The report could not be saved.", true);
  }
});

function questionProblem(value) {
  const text = value.trim();
  if (!text) return "Type a question before asking.";
  if (text.length < 3) return "Type at least 3 characters.";
  if (text.length > 500) return "Keep the question to 500 characters or fewer.";
  return "";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const problem = questionProblem(question.value);
  if (problem) {
    setStatus(problem, true);
    return;
  }
  setStatus("Asking…", false);
  result.hidden = true;
  askButton.disabled = true;
  askButton.setAttribute("aria-busy", "true");
  askLabel.textContent = "Asking…";
  const body = {
    question: question.value.trim(),
    language: selected("language"),
    accessibility_profile: selected("profile")
  };
  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body)
    });
    const payload = await response.json().catch(() => ({}));
    if (response.status === 503 && payload.status === "fallback") {
      showReply(payload);
      return;
    }
    if (response.status === 400) {
      setStatus(typeof payload.detail === "string" ? payload.detail : "The question could not be sent.", true);
      return;
    }
    if (!response.ok) {
      setStatus("The question could not be sent.", true);
      return;
    }
    showReply(payload);
  } catch (error) {
    setStatus("The page could not reach the assistant.", true);
  } finally {
    askButton.disabled = false;
    askButton.removeAttribute("aria-busy");
    askLabel.textContent = "Ask";
  }
});

applyProfile();
