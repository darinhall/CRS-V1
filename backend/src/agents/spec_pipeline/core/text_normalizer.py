import re
from typing import Optional


_BULLETS = ["\u2022", "•", "\u25cf", "\u25aa"]


def clean_text_for_spec_value(raw: Optional[str]) -> str:
    """
    Deterministic cleanup for display-facing values (spec_value).

    IMPORTANT: caller should preserve raw_value verbatim for provenance.
    """
    if not raw:
        return ""

    s = str(raw)

    # Normalize odd spaces
    s = s.replace("\u00a0", " ")  # NBSP
    s = s.replace("\u2009", " ")  # thin space
    s = s.replace("\u202f", " ")  # narrow no-break space

    # Turn bullets into newlines so UIs can render lists cleanly
    for b in _BULLETS:
        s = s.replace(b, "\n- ")

    # Common separator cleanup
    s = s.replace("•  ", "\n- ")
    s = s.replace("• ", "\n- ")

    # Collapse whitespace on each line, preserve newlines
    s = "\n".join([re.sub(r"[ \t]+", " ", line).strip() for line in s.splitlines()]).strip()

    # Collapse excessive blank lines
    s = re.sub(r"\n{3,}", "\n\n", s).strip()

    return s

