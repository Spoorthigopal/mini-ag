from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
import logging
import hashlib

logger = logging.getLogger(__name__)


def generate_salt() -> bytes:
    """
    Generate 16 random bytes using os.urandom().
    Used for key derivation.
    """
    return os.urandom(16)


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Derives consistent 256-bit encryption key using PBKDF2 with SHA-256.
    100,000 iterations for security.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def encrypt_file(file_bytes: bytes, user_id: str) -> dict:
    """
    Encrypt file content using AES-256-GCM authenticated encryption.
    
    AES-256-GCM provides:
    - Confidentiality (AES-256)
    - Integrity & Authenticity (GCM mode tag)
    - Replay/Tampering detection
    """
    try:
        salt = generate_salt()
        key = derive_key_from_password(user_id, salt)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(file_bytes) + encryptor.finalize()
        tag = encryptor.tag
        
        # Calculate SHA-256 checksum of original file for integrity checks
        checksum = compute_file_checksum(file_bytes)
        
        return {
            "ciphertext": ciphertext,
            "salt": salt,
            "nonce": nonce,
            "tag": tag,
            "checksum": checksum
        }
    except Exception as e:
        logger.error(f"Error during AES-GCM encryption: {e}")
        raise ValueError(f"Encryption failed: {e}")


def decrypt_file(ciphertext: bytes, salt: bytes, nonce: bytes, tag: bytes, user_id: str) -> bytes:
    """
    Decrypts ciphertext and verifies integrity using the authentication tag.
    Raises ValueError/DecryptionFailed if the tag verification fails.
    """
    try:
        key = derive_key_from_password(user_id, salt)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext
    except Exception as e:
        logger.error(f"Decryption or tag verification failed: {e}")
        raise ValueError(f"Decryption failed: authentication tag mismatch or corrupted key. {e}")


def compute_file_checksum(file_bytes: bytes) -> str:
    """
    Calculate SHA-256 hash of original unencrypted content for integrity verification.
    """
    hasher = hashlib.sha256()
    hasher.update(file_bytes)
    return hasher.hexdigest()


def verify_file_integrity(file_bytes: bytes, stored_checksum: str) -> bool:
    """
    Verify downloaded file integrity by comparing original checksum against current file bytes.
    """
    current_checksum = compute_file_checksum(file_bytes)
    return current_checksum == stored_checksum

# SECURITY NOTES:
# - AES-256-GCM provides authenticated encryption (confidentiality + integrity)
# - Salt prevents rainbow table attacks by generating a unique key derivation target
# - 100,000 PBKDF2 iterations slow down brute-force attacks on key derivation
# - Nonce should be completely random for each encryption (never reuse a nonce/IV)
# - Tag verification detects tampering and fails decryption immediately if corrupted
# - User-specific key derivation prevents cross-user document access even with duplicate salts
