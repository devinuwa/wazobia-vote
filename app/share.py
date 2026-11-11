def share_text(reply):
    """Text for Copy and WhatsApp: display answer, source title, and last checked date."""
    lines = [(reply or {}).get("display_answer") or ""]
    citations = (reply or {}).get("citations") or []
    if citations:
        lines.append("")
        lines.append("Sources")
        for citation in citations:
            lines.append(citation.get("title") or "")
            verified = (citation.get("last_verified") or "").strip()
            lines.append("Last checked " + verified if verified else "Last checked: not dated")
    return "\n".join(lines).strip()
