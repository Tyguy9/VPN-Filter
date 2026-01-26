import base64
import gzip
import hashlib
import re
from urllib.parse import urlparse

import requests

SOURCE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt"
KEEP_N = 100  # <- set this to 100, 150, 200, etc.

B64_CHARS_RE = re.compile(rb"[^A-Za-z0-9+/=_-]+")

def decode_subscription(raw: bytes) -> str:
    # If already plain text and contains links, return it
    plain = raw.decode("utf-8", errors="ignore")
    if "vless://" in plain:
        return plain

    # Otherwise, assume base64/base64url (possibly gzipped after decode)
    cleaned = re.sub(B64_CHARS_RE, b"", raw).strip()
    cleaned = cleaned.replace(b"-", b"+").replace(b"_", b"/")
    pad = (-len(cleaned)) % 4
    if pad:
        cleaned += b"=" * pad

    decoded = base64.b64decode(cleaned, validate=False)

    # gzip magic bytes
    if decoded[:2] == b"\x1f\x8b":
        decoded = gzip.decompress(decoded)

    return decoded.decode("utf-8", errors="ignore")

def hostport_key(vless_line: str) -> str | None:
    try:
        u = urlparse(vless_line.strip())
        if not u.hostname or not u.port:
            return None
        return f"{u.hostname}:{u.port}"
    except Exception:
        return None

def stable_score(line: str) -> str:
    # stable ordering via hash (no location text needed)
    return hashlib.sha1(line.encode("utf-8", errors="ignore")).hexdigest()

def main():
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()

    decoded_text = decode_subscription(r.content)
    lines = [ln.strip() for ln in decoded_text.splitlines() if ln.strip()]

    # keep only VLESS
    vless = [ln for ln in lines if ln.lower().startswith("vless://")]

    # dedupe by host:port
    seen = set()
    uniq = []
    for ln in vless:
        k = hostport_key(ln)
        if not k:
            continue
        if k in seen:
            continue
        seen.add(k)
        uniq.append(ln)

    # choose a stable subset
    uniq.sort(key=stable_score)
    chosen = uniq[:KEEP_N]

    print(f"Total lines decoded: {len(lines)}")
    print(f"VLESS lines: {len(vless)}")
    print(f"Unique host:port: {len(uniq)}")
    print(f"Chosen: {len(chosen)}")

    # output as base64 subscription (what NekoBox wants)
    out = "\n".join(chosen).encode("utf-8")
    encoded = base64.b64encode(out).decode("ascii")

    with open("filtered.txt", "w", encoding="utf-8") as f:
        f.write(encoded)

if __name__ == "__main__":
    main()
