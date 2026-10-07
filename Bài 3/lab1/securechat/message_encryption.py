import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class MessageEncryption:
    """Encrypt and authenticate chat text with a shared, pre-distributed key."""

    def __init__(self, key: bytes | None = None):
        self.key = key or os.urandom(32)
        if len(self.key) not in (16, 24, 32):
            raise ValueError("AES key must be 16, 24, or 32 bytes")
        self.cipher = AESGCM(self.key)

    def encrypt(self, plaintext: str, associated_data: bytes = b"") -> bytes:
        nonce = os.urandom(12)
        return nonce + self.cipher.encrypt(nonce, plaintext.encode("utf-8"), associated_data)

    def decrypt(self, ciphertext: bytes, associated_data: bytes = b"") -> str:
        if len(ciphertext) < 28:
            raise ValueError("Ciphertext is too short")
        nonce, encrypted = ciphertext[:12], ciphertext[12:]
        return self.cipher.decrypt(nonce, encrypted, associated_data).decode("utf-8")
