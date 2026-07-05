import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import string


def genera_chiave(master_password: str, salt: bytes) -> bytes:
    """
    Genera una chiave Fernet partendo dalla master password.

    La password non viene usata direttamente come chiave: PBKDF2HMAC la
    trasforma in una chiave sicura usando un salt e molte iterazioni.
    """
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

def cripta_testo(testo: str, chiave: bytes) -> str:
    """Cripta una stringa e restituisce il risultato in formato testo."""
    fernet = Fernet(chiave)
    testo_criptato = fernet.encrypt(testo.encode())
    return testo_criptato.decode()

def decripta_testo(testo_criptato: str, chiave: bytes) -> str:
    """Decripta una stringa cifrata con la stessa chiave Fernet."""
    fernet = Fernet(chiave)
    testo = fernet.decrypt(testo_criptato.encode())
    return testo.decode()

def genera_password_personalizzata(
    lunghezza: int = 16,
    usa_maiuscole: bool = True,
    usa_minuscole: bool = True,
    usa_numeri: bool = True,
    usa_speciali: bool = True,
    minimo_numeri: int = 0,
    minimo_speciali: int = 0
) -> str:
    """
    Genera una password casuale rispettando i criteri scelti dall'utente.

    secrets viene usato al posto di random perche e piu adatto a valori
    collegati alla sicurezza, come password e token.
    """
    if lunghezza <= 0:
        raise ValueError("La lunghezza deve essere maggiore di zero")

    if minimo_numeri < 0 or minimo_speciali < 0:
        raise ValueError("I valori minimi non possono essere negativi")

    if minimo_numeri > 0 and not usa_numeri:
        raise ValueError("Non puoi richiedere numeri se hai escluso i numeri")

    if minimo_speciali > 0 and not usa_speciali:
        raise ValueError("Non puoi richiedere caratteri speciali se li hai esclusi")

    minimo_maiuscole = 1 if usa_maiuscole else 0
    minimo_minuscole = 1 if usa_minuscole else 0
    totale_minimi = minimo_maiuscole + minimo_minuscole + minimo_numeri + minimo_speciali

    if totale_minimi > lunghezza:
        raise ValueError("I caratteri minimi richiesti superano la lunghezza della password")

    gruppi_caratteri = []

    if usa_maiuscole:
        gruppi_caratteri.append(string.ascii_uppercase)

    if usa_minuscole:
        gruppi_caratteri.append(string.ascii_lowercase)

    if usa_numeri:
        gruppi_caratteri.append(string.digits)

    if usa_speciali:
        gruppi_caratteri.append(string.punctuation)

    if not gruppi_caratteri:
        raise ValueError("Devi scegliere almeno un tipo di carattere")

    # Unisco tutti i gruppi abilitati per riempire la parte restante.
    caratteri_disponibili = "".join(gruppi_caratteri)

    password = []

    # Inserisco prima i caratteri minimi obbligatori.
    for _ in range(minimo_maiuscole):
        password.append(secrets.choice(string.ascii_uppercase))

    for _ in range(minimo_minuscole):
        password.append(secrets.choice(string.ascii_lowercase))

    for _ in range(minimo_numeri):
        password.append(secrets.choice(string.digits))

    for _ in range(minimo_speciali):
        password.append(secrets.choice(string.punctuation))

    while len(password) < lunghezza:
        password.append(secrets.choice(caratteri_disponibili))

    # Mescolo la password per non lasciare i caratteri obbligatori sempre all'inizio.
    secrets.SystemRandom().shuffle(password)

    return "".join(password)
