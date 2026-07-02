import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def genera_chiave(master_password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )

    chiave = base64.urlsafe_b64encode(
        kdf.derive(master_password.encode())
    )

    return chiave

def cripta_testo(testo, chiave):
    fernet = Fernet(chiave)
    testo_criptato = fernet.encrypt(testo.encode())
    return testo_criptato.decode()

def decripta_testo(testo_criptato, chiave):
    fernet = Fernet(chiave)
    testo = fernet.decrypt(testo_criptato.encode())
    return testo.decode()