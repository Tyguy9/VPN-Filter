import base64
import requests

SOURCE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt"
KEYWORDS = ["helsinki", "finland", "narva", "estonia"]

def main():
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()

    decoded = base64.b64decode(r.text).decode("utf-8", errors="ignore")
    lines = decoded.splitlines()

    filtered = [
        l for l in lines
        if any(k in l.lower() for k in KEYWORDS)
    ]

    encoded = base64.b64encode(
        "\n".join(filtered).encode("utf-8")
    ).decode("utf-8")

    with open("filtered.txt", "w") as f:
        f.write(encoded)

    print(f"Saved {len(filtered)} servers")

if __name__ == "__main__":
    main()
