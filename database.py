import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / "password_manager.db"

def crea_database() -> None:
    """Crea il database SQLite e le tabelle se non esistono gia."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # impostazioni conserva salt e token di verifica della master password.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS impostazioni (
        chiave TEXT PRIMARY KEY,
        valore TEXT NOT NULL
    )
    """)

    # categorie permette di raggruppare i login salvati.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)

    # password contiene username e password gia criptati prima del salvataggio.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titolo TEXT NOT NULL,
        username_criptato TEXT NOT NULL,
        password_criptata TEXT NOT NULL,
        sito TEXT,
        categoria_id INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES categorie(id)
    )
    """)

    conn.commit()
    conn.close()

def salva_impostazione(chiave: str, valore: str) -> None:
    """Salva o aggiorna un valore nella tabella impostazioni."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO impostazioni (chiave, valore)
        VALUES (?, ?)
        """,
        (chiave, valore)
    )

    conn.commit()
    conn.close()

def leggi_impostazione(chiave: str) -> str | None:
    """Legge un valore dalla tabella impostazioni."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT valore FROM impostazioni WHERE chiave = ?",
        (chiave,)
    )

    risultato = cursor.fetchone()
    conn.close()

    if risultato:
        return risultato[0]
    return None

def aggiungi_categoria(nome: str) -> int | None:
    """Aggiunge una categoria se non esiste e restituisce il suo id."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO categorie (nome) VALUES (?)",
        (nome,)
    )

    conn.commit()

    cursor.execute(
        "SELECT id FROM categorie WHERE nome = ?",
        (nome,)
    )
    risultato = cursor.fetchone()

    conn.close()

    if risultato:
        return risultato[0]
    return None

def leggi_nome_categoria(categoria_id: int | None) -> str | None:
    """Restituisce il nome della categoria partendo dal suo id."""
    if categoria_id is None:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT nome FROM categorie WHERE id = ?",
        (categoria_id,)
    )

    risultato = cursor.fetchone()
    conn.close()

    if risultato:
        return risultato[0]
    return None

def aggiungi_password(
    titolo: str,
    username_criptato: str,
    password_criptata: str,
    sito: str,
    categoria_id: int | None = None
) -> None:
    """Inserisce un nuovo login nel database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO password (titolo, username_criptato, password_criptata, sito, categoria_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (titolo, username_criptato, password_criptata, sito, categoria_id)
    )

    conn.commit()
    conn.close()

def leggi_password(titolo: str) -> tuple | None:
    """Cerca un login tramite titolo."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT titolo, username_criptato, password_criptata, sito, categoria_id
        FROM password
        WHERE titolo = ?
        """,
        (titolo,)
    )

    risultato = cursor.fetchone()
    conn.close()
    return risultato

def vedi_tutti_login() -> list[tuple]:
    """Restituisce l'elenco sintetico dei login da mostrare nella tabella."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, titolo, sito, categoria_id
        FROM password
        ORDER BY titolo
        """,
    )

    risultato = cursor.fetchall()
    conn.close()
    return risultato

def leggi_password_per_id(id_login: int) -> tuple | None:
    """Legge un login completo partendo dal suo id."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT titolo, username_criptato, password_criptata, sito, categoria_id
        FROM password
        WHERE id = ?
        """,
        (id_login,)
    )

    risultato = cursor.fetchone()
    conn.close()
    return risultato

def elimina_password(id_login: int) -> int:
    """Elimina un login e restituisce il numero di righe eliminate."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM password
        WHERE id = ?
        """,
        (id_login,)
    )

    righe_eliminate = cursor.rowcount
    conn.commit()
    conn.close()
    return righe_eliminate

def modifica_password(
    id_login: int,
    titolo: str,
    username_criptato: str,
    password_criptata: str,
    sito: str,
    categoria_id: int | None
) -> int:
    """Aggiorna i dati di un login esistente."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE password
        SET titolo = ?,
            username_criptato = ?,
            password_criptata = ?,
            sito = ?,
            categoria_id = ?
        WHERE id = ?
        """,
        (titolo, username_criptato, password_criptata, sito, categoria_id, id_login)
    )

    righe_modificate = cursor.rowcount
    conn.commit()
    conn.close()
    return righe_modificate

def vedi_categorie() -> list[tuple]:
    """Restituisce tutte le categorie ordinate per nome."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, nome
        FROM categorie
        ORDER BY nome
        """
    )

    risultato = cursor.fetchall()
    conn.close()
    return risultato

def rinomina_categoria(id_cat: int, nuovo_nome_cat: str) -> int | None:
    """Rinomina una categoria. Restituisce None se il nome esiste gia."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE categorie
            SET nome = ?
            WHERE id = ?
            """,
            (nuovo_nome_cat, id_cat)
        )
    except sqlite3.IntegrityError:
        conn.close()
        return None

    righe_modificate = cursor.rowcount
    conn.commit()
    conn.close()
    return righe_modificate

def elimina_categoria(id_categoria: int) -> int:
    """Elimina una categoria e lascia senza categoria i login collegati."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Prima scollego i login dalla categoria, poi elimino la categoria.
    cursor.execute(
        """
        UPDATE password
        SET categoria_id = NULL
        WHERE categoria_id = ?
        """,
        (id_categoria,)
    )

    cursor.execute(
        """
        DELETE FROM categorie
        WHERE id = ?
        """,
        (id_categoria,)
    )

    righe_eliminate = cursor.rowcount
    conn.commit()
    conn.close()
    return righe_eliminate
