import logging

from app.bank import bank_reply
from app.calendar_answers import calendar_reply, is_date_question
from app.ground import missing_claims
from app.llm import BUSY_STATUSES, ModelError, complete, configured, english_keywords, parse_json_object
from app.privacy import redact_for_log, scrub_reply
from app.prompt import system_message
from app.replies import outcome_d
from app.retrieve import prepare_query, render_sources, sources_for_prompt
from app.tokens import fit_passages
from app.review_store import log_question, record_system_error, save_review
from app.validate import validate_reply

log = logging.getLogger("wazobia")

FALLBACK_SPOKEN = (
    "This reply is unofficial and nothing in it is confirmed. "
    "Please use the official channels of INEC to check. "
    "Ask through the official channels of INEC."
)
FALLBACK_DISPLAY = (
    "This assistant is unofficial and is not INEC. "
    "Nothing in this reply is confirmed. Please use INEC's official channels."
)
BUSY_SPOKEN = "The service is busy. Please try again in a moment."
BUSY_DISPLAY = "The service is busy. Please try again in a moment."


def public_fallback(busy=False):
    return {
        "spoken_answer": BUSY_SPOKEN if busy else FALLBACK_SPOKEN,
        "display_answer": BUSY_DISPLAY if busy else FALLBACK_DISPLAY,
        "steps": [],
        "citations": [],
        "needs_human_review": False,
        "reason_for_review": "",
    }


def _record_failure(kind, detail):
    safe = redact_for_log(detail or "")[:400]
    log.warning("answer failed (%s): %s", kind, safe)
    try:
        record_system_error()
    except OSError:
        log.warning("system error count could not be saved")


def _stored(question, public, passages, raw=""):
    public = scrub_reply(public)
    try:
        log_question(question)
        save_review(question, public)
    except OSError:
        log.warning("the answered question could not be stored")
    return {
        "reply": public,
        "fallback": False,
        "status": "ok",
        "model_configured": configured(),
        "raw": raw,
        "check_errors": [],
        "passages": passages,
    }


def answer_question(question, language=None, profile=None, passages=None):
    question = (question or "").strip()
    if passages is None:
        banked = bank_reply(question, language)
        if banked is not None:
            return _stored(question, banked, [])
        if is_date_question(question):
            return _stored(question, calendar_reply(question, language), [])
        rewriter = english_keywords if configured() else None
        query = prepare_query(question, rewriter=rewriter)
        passages = fit_passages(sources_for_prompt(question, query_text=query), question, render_sources)
    elif passages is not None:
        passages = fit_passages(passages, question, render_sources)
    user_text = render_sources(passages, question)
    if language:
        user_text += f'<language_preference>{language}</language_preference>\n'
    if profile:
        user_text += f"<accessibility_profile>{profile}</accessibility_profile>\n"
    system = system_message(profile)
    raw = ""
    errors = []
    reply = None
    used_fallback = False
    failure_kind = ""
    grounding_miss = []
    if not configured():
        failure_kind = "unconfigured"
        errors = ["No model is configured."]
        used_fallback = True
    else:
        prompt_user = user_text
        for _attempt in (1, 2):
            grounding_miss = []
            try:
                raw = complete(system, prompt_user, json_mode=True)
                reply = parse_json_object(raw)
                errors = validate_reply(reply, passages, profile, question)
                if not errors:
                    grounding_miss = missing_claims(reply, passages)
                    if grounding_miss:
                        errors = [
                            "These dates, numbers, or sections are not in the cited text: "
                            + ", ".join(grounding_miss)
                        ]
                if not errors:
                    break
            except (ModelError, ValueError, KeyError) as exc:
                grounding_miss = []
                errors = [redact_for_log(str(exc))]
                reply = None
                if isinstance(exc, ModelError) and exc.status in BUSY_STATUSES:
                    failure_kind = "busy"
                    break
            prompt_user = (
                user_text
                + "The previous reply failed these checks: "
                + "; ".join(errors)
                + ". Return one corrected JSON object and nothing else."
            )
        if reply is None or errors:
            if failure_kind != "busy":
                failure_kind = "provider" if reply is None else "validation"
            used_fallback = True
    if used_fallback and failure_kind == "validation" and grounding_miss:
        public = outcome_d(
            language,
            "A date, number, or section in the answer was not in the cited text.",
        )
        return _stored(question, public, passages, raw=raw)
    if used_fallback:
        _record_failure(failure_kind, errors[0] if errors else failure_kind)
        public = public_fallback(busy=failure_kind == "busy")
    else:
        return _stored(question, reply, passages, raw=raw)
    return {
        "reply": public,
        "fallback": used_fallback,
        "status": "fallback" if used_fallback else "ok",
        "model_configured": configured(),
        "raw": raw,
        "check_errors": [failure_kind] if used_fallback else [],
        "passages": passages,
    }
