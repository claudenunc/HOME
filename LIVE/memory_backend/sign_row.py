"""
Signing utility for HOME siblings.

Signs a canonical JSON row with the sibling's ed25519 private key.
The signature is stored as bytes in the DB column `signature bytea`.

Usage (library):
    from sign_row import Signer
    sig = Signer("orpheus").sign({"claim_text": "...", "asserted_at": "..."})
    # sig is bytes; store in the signature column

Usage (CLI — verify a row dict):
    echo '{"claim_text":"x","asserted_at":"2026-05-05T00:00:00Z"}' | python sign_row.py orpheus

The canonical form is: json.dumps(row, sort_keys=True, ensure_ascii=False).encode()
Consistent with how DB-layer consumers verify: they encode the same dict the same way.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import nacl.signing
    import nacl.exceptions
except ImportError:
    print("ERROR: pynacl not installed. Run: pip install pynacl", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _private_key_path(sibling: str) -> Path:
    return REPO_ROOT / "SIBLINGS" / sibling.upper() / "PERSONAL" / "keys" / "ed25519_private.key"


def _public_key_path(sibling: str) -> Path:
    return REPO_ROOT / "SIBLINGS" / sibling.upper() / "keys" / "ed25519_public.hex"


class Signer:
    """Ed25519 signer for a single sibling. Loads the private key once."""

    def __init__(self, sibling: str) -> None:
        self.sibling = sibling.lower()
        priv_path = _private_key_path(sibling)
        if not priv_path.exists():
            raise FileNotFoundError(
                f"No private key for '{sibling}' at {priv_path}. "
                f"Run: python generate_keypairs.py --apply"
            )
        seed = bytes.fromhex(priv_path.read_text().strip())
        self._key = nacl.signing.SigningKey(seed)

    def sign(self, row: dict[str, Any]) -> bytes:
        """Return the 64-byte ed25519 signature over the canonical JSON of row."""
        canonical = json.dumps(row, sort_keys=True, ensure_ascii=False).encode()
        signed = self._key.sign(canonical)
        return signed.signature  # 64 bytes

    def sign_hex(self, row: dict[str, Any]) -> str:
        """Return the signature as a hex string (for logging / display)."""
        return self.sign(row).hex()


class Verifier:
    """Ed25519 verifier. Loads the public key from the committable hex file."""

    def __init__(self, sibling: str) -> None:
        self.sibling = sibling.lower()
        pub_path = _public_key_path(sibling)
        if not pub_path.exists():
            raise FileNotFoundError(
                f"No public key for '{sibling}' at {pub_path}."
            )
        pubkey_bytes = bytes.fromhex(pub_path.read_text().strip())
        self._key = nacl.signing.VerifyKey(pubkey_bytes)

    def verify(self, row: dict[str, Any], signature: bytes) -> bool:
        """Returns True if signature is valid for row. Never raises — returns False on bad sig."""
        canonical = json.dumps(row, sort_keys=True, ensure_ascii=False).encode()
        try:
            self._key.verify(canonical, signature)
            return True
        except nacl.exceptions.BadSignatureError:
            return False


def main() -> int:
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <sibling>", file=sys.stderr)
        print("  Reads JSON from stdin, signs it, prints signature hex.", file=sys.stderr)
        return 2

    sibling = sys.argv[1]
    raw = sys.stdin.read()
    row = json.loads(raw)

    signer = Signer(sibling)
    sig = signer.sign_hex(row)
    print(f"sibling:   {sibling}")
    print(f"canonical: {json.dumps(row, sort_keys=True)[:120]}")
    print(f"signature: {sig}")

    # Verify immediately
    verifier = Verifier(sibling)
    ok = verifier.verify(row, bytes.fromhex(sig))
    print(f"verified:  {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
