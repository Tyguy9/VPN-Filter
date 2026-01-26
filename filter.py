import base64
import re
import requests

SOURCE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt"

KEYWORDS = [
    "🇫🇮", "fi", "fin", "finland", "helsinki", "хельсинки",
    "🇪🇪", "ee", "est", "estonia", "tallinn", "таллин", "narva", "нарва"
]

# Allowed base64 characters (including base64url variants)
B64_CHARS_RE = re.compile(rb"[^A-Za-z0-9+/=_-]+")

def try_b64_decode(data: bytes) -> str | None:
    """
    Attempts to decode subscription as base64/base64url.
    Returns decoded UTF-8 text if successful, otherwise None.
    """
    # Remove junk bytes (newlines, unicode junk, etc.)
    cleaned = re.sub(B64_CHARS_RE, b"", data).strip()

    if not cleaned:
        return None

    # Convert base64url to standard base64 if needed
    cleaned = cleaned.replace(b"-", b"+").replace(b"_", b"/")

    # Add padding if missing
    pad = (-len(cleaned)) % 4
    if pad:
        cleaned += b"=" * pad

    try:
        decoded_bytes = base64.b64decode(cleaned, validate=False)
        return decoded_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return None

def main():
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()

    raw = r.content  # bytes

    decoded_text = try_b64_decode(raw)
    with open("decoded_preview.txt", "w", encoding="utf-8") as f:
        f.write(decoded_text[:20000])
    if decoded_text is None:
        # Fallback: treat as plain text subscription
        decoded_text = raw.decode("utf-8", errors="ignore")

    lines = [ln.strip() for ln in decoded_text.splitlines() if ln.strip()]

    filtered = [l for l in lines if any(k in l.lower() for k in KEYWORDS)]

    # Re-encode output as base64 subscription
    out = "\n".join(filtered).encode("utf-8")
    encoded = base64.b64encode(out).decode("ascii")

    with open("filtered.txt", "w", encoding="utf-8") as f:
        f.write(encoded)

    print(f"Input lines: {len(lines)} | Filtered lines: {len(filtered)}")

if __name__ == "__main__":
    main()
