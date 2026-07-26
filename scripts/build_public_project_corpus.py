from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

STRONG_TITLE = re.compile(
    r"(?ix)(?:\bASIN(?:-HHC)?\b|\bHHC\b|\bCP8\b|\bCP9\b|\bHarmonyOS\b|\bHOS\b|"
    r"\bCodex\b|\bANU-?28\b|\bNCEA\b|\bACE\s+GEM\b|\b(?:harmonic|glyph|lattice|"
    r"resonance|phyllotaxis|sacred\s+geometry|crop\s+circle|flower\s+of\s+life)\b|"
    r"\b(?:sovereign\s+(?:agent|AI)|house\s+of\s+rooms|proof[- ]of[- ]process|PoWP|"
    r"provenance|receipt|replay|promotion\s+gate)\b|\b(?:AISquad|AISN|AI\s+network|"
    r"human[- ]AI|agent\s+accountability)\b|\b(?:HHC\s+crypto|mineable\s+cryptocurrency|"
    r"crypto\s+wallet|tokenomics|token\s+ecosystem|GPU\s+(?:rig|server|mining))\b|"
    r"\b(?:Weaver|Cathedral|DeepSpec|Unified\s+Bridge|Handshake|Cycle\s+0?10|Supreme\s+OS)\b)"
)

EXCLUDE_TITLE = re.compile(
    r"(?ix)(?:custody|parenting|child\s+support|co[- ]?parent|divorce|family\s+law|"
    r"ssi|ssdi|disability|medical|health|rheumatoid|tuberculosis|dating|relationship|"
    r"housing|rent|homeless|doordash|garnish|cdl|taxi|well\s+drilling|septic|personal\s+growth)"
)

SENSITIVE_MESSAGE = re.compile(
    r"(?ix)(?:custody|parenting\s+time|child\s+support|co[- ]?parent|ex[- ]?wife|divorce|"
    r"(?:my|our|the|got\s+the)\s+(?:kids?|children|son|daughter)\b|my\s+recovery|"
    r"in\s+recovery|recovery\s+program|12[- ]step|the\s+rooms|sobriety|sober|"
    r"rheumatoid|arthritis|tuberculosis|latent\s+tb|medication|doctor|hospital|"
    r"ssi|ssdi|social\s+security|disability\s+claim|garnish|homeless|bank\s+balance|"
    r"dating|girlfriend|boyfriend|romantic|first\s+date)"
)

EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)")
ADDRESS = re.compile(
    r"(?i)\b\d{1,6}\s+[A-Z][A-Za-z0-9.\-]*(?:\s+[A-Z][A-Za-z0-9.\-]*){0,4}\s+"
    r"(?:St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Ln|Lane|Blvd|Boulevard|Ct|Court|Way)\b"
)
PRIVATE_URL = re.compile(r"https?://(?:drive\.google\.com|docs\.google\.com|mail\.google\.com)/\S+", re.I)
SECRET = re.compile(
    r"(?i)(api[_ -]?key|secret|password|private[_ -]?key|access[_ -]?token|bearer)\s*[:=]\s*[^\s,;]+"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_private_terms(path: Path | None) -> list[re.Pattern[str]]:
    if not path:
        return []
    return [re.compile(rf"(?i)\b{re.escape(x.strip())}\b") for x in path.read_text().splitlines() if x.strip()]


def redact(text: str, private_terms: list[re.Pattern[str]]) -> str:
    text = html.unescape(text)
    text = EMAIL.sub("[REDACTED_EMAIL]", text)
    text = PHONE.sub("[REDACTED_PHONE]", text)
    text = ADDRESS.sub("[REDACTED_ADDRESS]", text)
    text = PRIVATE_URL.sub("[REDACTED_PRIVATE_URL]", text)
    text = SECRET.sub("[REDACTED_SECRET]", text)
    for pattern in private_terms:
        text = pattern.sub("[REDACTED_PERSON]", text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--private-terms", type=Path)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    private_terms = load_private_terms(args.private_terms)
    source = args.source.read_text(encoding="utf-8", errors="replace")
    source = source.split("### KIMI AGENT - ASIN_HHC METADATA CORPUS", 1)[0]
    starts = list(re.finditer(r"(?m)^CONVERSATION\s+(\d+)/1014\s*$", source))

    conversations = []
    messages = []
    replaced = 0
    for index, match in enumerate(starts):
        block = source[match.start() : starts[index + 1].start() if index + 1 < len(starts) else len(source)]
        title_match = re.search(r"(?m)^Title:\s*(.*?)\s*$", block)
        date_match = re.search(r"(?m)^Date:\s*(.*?)\s*$", block)
        title = html.unescape(title_match.group(1).strip()) if title_match else f"Conversation {match.group(1)}"
        if EXCLUDE_TITLE.search(title) or not STRONG_TITLE.search(title):
            continue

        parts = re.split(r"(?m)^\[(YOU|ChatGPT)\]\s*$", block)
        current = []
        for part_index in range(1, len(parts), 2):
            role = parts[part_index].lower()
            body = parts[part_index + 1].strip() if part_index + 1 < len(parts) else ""
            if not body:
                continue
            if SENSITIVE_MESSAGE.search(body):
                body = "[REDACTED_PERSONAL_TANGENT]"
                is_redacted = True
                replaced += 1
            else:
                body = redact(body, private_terms)
                is_redacted = False
            current.append({"role": role, "content": body, "redacted": is_redacted})

        usable = [m for m in current if not m["redacted"] and len(m["content"]) > 20]
        density = sum("\n".join(x["content"] for x in usable).lower().count(term) for term in (
            "asin", "hhc", "cp8", "harmonyos", "codex", "glyph", "harmonic", "lattice", "token", "wallet", "agent", "receipt"
        ))
        if len(usable) < 2 or density < 3:
            continue

        record = {
            "source": "openai_chat_export",
            "conversation_index": int(match.group(1)),
            "title": redact(title, private_terms),
            "date": date_match.group(1).strip() if date_match else None,
            "evidence_class": "HISTORICAL_PROJECT_DIALOGUE_UNVERIFIED",
            "publication_status": "PUBLIC_PROJECT_ONLY_REDACTED",
            "messages": current,
        }
        conversations.append(record)
        for sequence, message in enumerate(current, 1):
            messages.append({k: record[k] for k in record if k != "messages"} | {"message_seq": sequence} | message)

    conversation_path = args.out / "project_conversations.jsonl"
    message_path = args.out / "project_messages.jsonl"
    conversation_path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in conversations), encoding="utf-8")
    message_path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in messages), encoding="utf-8")
    manifest = {
        "conversations": len(conversations),
        "messages": len(messages),
        "personal_messages_replaced": replaced,
        "conversation_sha256": sha256(conversation_path),
        "message_sha256": sha256(message_path),
        "evidence_class": "HISTORICAL_PROJECT_DIALOGUE_UNVERIFIED",
    }
    (args.out / "PUBLIC_CORPUS_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
