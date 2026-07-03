from database import (
    aggiungi_categoria,
    aggiungi_password,
    crea_database,
    leggi_impostazione,
    leggi_nome_categoria,
    leggi_password,
    salva_impostazione,
    vedi_tutti_login,
    leggi_password_per_id,
    elimina_password,
    modifica_password,
    vedi_categorie,
    rinomina_categoria,
    elimina_categoria,
)
from crypto_utils import genera_chiave, cripta_testo, decripta_testo, genera_password_personalizzata
import string
import os
import base64
from getpass import getpass
from cryptography.fernet import InvalidToken

TOKEN_VERIFICA = "main_pass_ok"

def primo_accesso():
    main_pass = getpass("Crea master password: ")

    while not valida_master_password(main_pass):
        print("Password debole")
        main_pass = getpass("Riprova: ")

    salt = os.urandom(16)
    chiave = genera_chiave(main_pass, salt)

    token_criptato = cripta_testo(TOKEN_VERIFICA, chiave)
    salt_testo = base64.b64encode(salt).decode()

    salva_impostazione("salt", salt_testo)
    salva_impostazione("verification_token", token_criptato)

    print("Master password configurata correttamente")

    return chiave

def valida_master_password(password):
    if len(password) < 10:
        return False

    ha_maiuscola = any(carattere.isupper() for carattere in password)
    ha_minuscola = any(carattere.islower() for carattere in password)
    ha_numero = any(carattere.isdigit() for carattere in password)
    ha_speciale = any(carattere in string.punctuation for carattere in password)

    return ha_maiuscola and ha_minuscola and ha_numero and ha_speciale

def chiedi_si_no(domanda):
    while True:
        risposta = input(f"{domanda} s/n: ").strip().lower()

        if risposta == "s":
            return True

        if risposta == "n":
            return False

        print("Risposta non valida, scrivi s oppure n")

def chiedi_numero_intero(domanda, minimo=0, valore_default=None):
    while True:
        risposta = input(domanda).strip()

        if not risposta and valore_default is not None:
            return valore_default

        if not risposta.isdigit():
            print("Devi inserire un numero")
            continue

        numero = int(risposta)

        if numero < minimo:
            print(f"Il numero deve essere almeno {minimo}")
            continue

        return numero

def genera_password_da_input():
    lunghezza = chiedi_numero_intero("Lunghezza password (Invio = 16): ", minimo=1, valore_default=16)
    usa_maiuscole = chiedi_si_no("Vuoi usare lettere maiuscole?")
    usa_minuscole = chiedi_si_no("Vuoi usare lettere minuscole?")
    usa_numeri = chiedi_si_no("Vuoi usare numeri?")
    usa_speciali = chiedi_si_no("Vuoi usare caratteri speciali?")

    minimo_numeri = 0
    minimo_speciali = 0

    if usa_numeri:
        minimo_numeri = chiedi_numero_intero("Numero minimo di numeri: ", minimo=0, valore_default=0)

    if usa_speciali:
        minimo_speciali = chiedi_numero_intero("Numero minimo di caratteri speciali: ", minimo=0, valore_default=0)

    try:
        return genera_password_personalizzata(
            lunghezza,
            usa_maiuscole,
            usa_minuscole,
            usa_numeri,
            usa_speciali,
            minimo_numeri,
            minimo_speciali
        )
    except ValueError as errore:
        print(f"Impostazioni non valide: {errore}")
        return None

def mostra_generatore_password():
    password = genera_password_da_input()

    if password is not None:
        print(f"Password generata: {password}")

def login():
    salt_testo = leggi_impostazione("salt")
    token_criptato = leggi_impostazione("verification_token")

    if salt_testo is None or token_criptato is None:
        print("Errore: configurazione master password mancante")
        return None

    salt = base64.b64decode(salt_testo)

    while True:
        main_pass = getpass("Inserisci master password: ")
        chiave = genera_chiave(main_pass, salt)

        try:
            token = decripta_testo(token_criptato, chiave)

            if token == TOKEN_VERIFICA:
                print("Accesso consentito")
                return chiave
            else:
                print("Password errata")

        except InvalidToken:
            print("Password errata")

def nuovo_save(chiave):
    titolo = input("Inserisci il nome del login che vuoi salvare: ").strip()
    username = input("Inserisci l'username del login che vuoi salvare: ").strip()

    if not titolo or not username:
        print("Titolo e username sono obbligatori")
        return

    if chiedi_si_no("Vuoi generare una password sicura?"):
        password = genera_password_da_input()

        if password is None:
            return

        print(f"Password generata: {password}")
    else:
        password = getpass("Inserisci la password del login che vuoi salvare: ")

    sito = input("Inserisci il link del sito del login che vuoi salvare: ").strip()

    categoria = input("Inserisci la categoria del login che vuoi salvare: ").strip()

    if not password:
        print("La password e obbligatoria")
        return

    categoria_id = None
    if categoria:
        categoria_id = aggiungi_categoria(categoria)

    username_criptato = cripta_testo(username, chiave)
    password_criptata = cripta_testo(password, chiave)

    aggiungi_password(titolo, username_criptato, password_criptata, sito, categoria_id)
    print("Login salvato correttamente")

def vedi_save(chiave):
    risultato = None

    while True:
        print("\n1. Cerca per id")
        print("2. Cerca per titolo")
        print("0. Torna al menu")

        scelta = input("Scegli un'opzione: ").strip()

        if scelta == "1":
            id_cercato = input("Inserisci l'id del login che vuoi cercare: ").strip()

            if not id_cercato.isdigit():
                print("L'id deve essere un numero")
                continue

            risultato = leggi_password_per_id(int(id_cercato))
            break

        elif scelta == "2":
            titolo_cercato = input("Inserisci il titolo del login che vuoi cercare: ").strip()
            risultato = leggi_password(titolo_cercato)
            break

        elif scelta == "0":
            return

        else:
            print("Scelta non valida")

    if risultato is None:
        print("Nessun login trovato")
        return

    titolo, username_criptato, password_criptata, sito, categoria_id = risultato
    username = decripta_testo(username_criptato, chiave)
    password = decripta_testo(password_criptata, chiave)
    categoria = leggi_nome_categoria(categoria_id)

    print("\n--- Login trovato ---")
    print(f"Titolo: {titolo}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Sito: {sito or 'Nessun sito'}")
    print(f"Categoria: {categoria or 'Nessuna categoria'}")

def tutti_login():
    risultati = vedi_tutti_login()

    if not risultati:
        print("Non ci sono login salvati")
        return

    print("\n--- Login salvati ---")

    for id_login, titolo, sito, categoria_id in risultati:
        categoria = leggi_nome_categoria(categoria_id)
        print(f"{id_login}. {titolo} | {sito or 'Nessun sito'} | {categoria or 'Nessuna categoria'}")

def elimina_login():
    tutti_login()
    while True:
        scelta = input("\nScegli l'id dell'elemento che vuoi cancellare: ").strip()
        
        if not scelta.isdigit():
            print("L'id deve essere un numero")
            continue

        risultato = leggi_password_per_id(int(scelta))

        if risultato is None:
            print("Nessun login trovato con questo id")
            continue

        titolo, _, _, sito, _ = risultato
        conferma = input(f"Sei sicuro di voler eliminare '{titolo}' ({sito or 'Nessun sito'})? s/n: ").strip().lower()

        if conferma == "s":
            righe_eliminate = elimina_password(int(scelta))

            if righe_eliminate:
                print("Login eliminato correttamente")
            else:
                print("Eliminazione non riuscita")

            return

        if conferma == "n":
            print("Eliminazione annullata")
            return

        print("Risposta non valida, scrivi s oppure n")
        
def modifica_login(chiave):
    tutti_login()
    while True:
        scelta = input("\nScegli l'id dell'elemento che vuoi modificare: ").strip()
        
        if not scelta.isdigit():
            print("L'id deve essere un numero")
            continue

        risultato = leggi_password_per_id(int(scelta))

        if risultato is None:
            print("Nessun login trovato con questo id")
            continue

        titolo, username_criptato, password_criptata, sito, categoria_id = risultato
        username = decripta_testo(username_criptato, chiave)
        password = decripta_testo(password_criptata, chiave)
        categoria = leggi_nome_categoria(categoria_id)

        print("\n--- Dati del Login ---")
        print(f"Titolo: {titolo}")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Sito: {sito or 'Nessun sito'}")
        print(f"Categoria: {categoria or 'Nessuna categoria'}")

        print("\nSe non vuoi cambiare un valore, premi Invio")
        cambio_titolo = input("Inserisci il nuovo titolo: ").strip()
        cambio_username = input("Inserisci il nuovo username: ").strip()

        if chiedi_si_no("Vuoi generare una nuova password sicura?"):
            cambio_password = genera_password_da_input()

            if cambio_password is None:
                return

            print(f"Password generata: {cambio_password}")
        else:
            cambio_password = getpass("Inserisci la nuova password: ")

        cambio_sito = input("Inserisci il nuovo sito: ").strip()
        cambio_categoria = input("Inserisci la nuova categoria: ").strip()

        nuovo_titolo = cambio_titolo or titolo
        nuovo_username = cambio_username or username
        nuova_password = cambio_password or password
        nuovo_sito = cambio_sito or sito
        nuovo_categoria_id = categoria_id

        if cambio_categoria:
            nuovo_categoria_id = aggiungi_categoria(cambio_categoria)

        nuovo_username_criptato = cripta_testo(nuovo_username, chiave)
        nuova_password_criptata = cripta_testo(nuova_password, chiave)

        righe_modificate = modifica_password(
            int(scelta),
            nuovo_titolo,
            nuovo_username_criptato,
            nuova_password_criptata,
            nuovo_sito,
            nuovo_categoria_id
        )

        if righe_modificate:
            print("Login modificato correttamente")
        else:
            print("Modifica non riuscita")

        return

def gestisci_categorie():
    while True:
        risultati = vedi_categorie()

        print("\n--- Categorie salvate ---")

        if not risultati:
            print("Non ci sono categorie salvate")
        else:
            for id_cat, nome_cat in risultati:
                print(f"{id_cat}. {nome_cat}")

        print("\n1. Aggiungi categoria")
        print("2. Rinomina categoria")
        print("3. Elimina categoria")
        print("0. Torna al menu")

        scelta = input("Scegli un'opzione: ").strip()

        if scelta == "1":
            nuova_categoria = input("Inserisci il nome della categoria che vuoi creare: ").strip()

            if not nuova_categoria:
                print("Non puoi inserire una categoria vuota")
            else:
                categoria_id = aggiungi_categoria(nuova_categoria)

                if categoria_id is None:
                    print("Categoria non salvata")
                else:
                    print("Categoria salvata correttamente")

        elif scelta == "2":
            id_categoria = input("Inserisci l'id della categoria che vuoi modificare: ").strip()

            if not id_categoria.isdigit():
                print("L'id deve essere un numero")
                continue

            risultato = leggi_nome_categoria(int(id_categoria))

            if risultato is None:
                print("Nessuna categoria trovata con questo id")
                continue
            else:
                nuovo_nome = input("Inserisci il nuovo nome della categoria: ").strip()

                if not nuovo_nome:
                    print("Non puoi inserire una categoria vuota")
                else:
                    verifica = rinomina_categoria(int(id_categoria), nuovo_nome)

                    if verifica is None:
                        print("Esiste gia una categoria con questo nome")
                    elif verifica:
                        print("Categoria rinominata correttamente")
                    else:
                        print("Cambiamento non riuscito")

        elif scelta == "3":
            id_categoria = input("Inserisci l'id della categoria che vuoi eliminare: ").strip()

            if not id_categoria.isdigit():
                print("L'id deve essere un numero")
                continue

            risultato = leggi_nome_categoria(int(id_categoria))

            if risultato is None:
                print("Nessuna categoria trovata con questo id")
                continue
            else:
                conferma = input(f"Sei sicuro di voler eliminare '{risultato}'? s/n: ").strip().lower()

                if conferma == "s":
                    righe_eliminate = elimina_categoria(int(id_categoria))

                    if righe_eliminate:
                        print("Categoria eliminata correttamente")
                    else:
                        print("Eliminazione non riuscita")

                    continue

                if conferma == "n":
                    print("Eliminazione annullata")
                    continue

                print("Risposta non valida, scrivi s oppure n")

        elif scelta == "0":
            return

        else:
            print("Scelta non valida")

def scelta_azione(chiave):
    while True:
        print("\n1. Crea nuovo login")
        print("2. Vedi login salvato")
        print("3. Vedi tutti i login salvati")
        print("4. Elimina un login in base al id")
        print("5. Modifica un login in base al id")
        print("6. Gestisci le categorie")
        print("7. Genera password sicura")
        print("0. Esci")

        scelta = input("Scegli un'opzione: ").strip()

        if scelta == "1":
            nuovo_save(chiave)
        elif scelta == "2":
            vedi_save(chiave)
        elif scelta == "3":
            tutti_login()
        elif scelta == "4":
            elimina_login()
        elif scelta == "5":
            modifica_login(chiave)
        elif scelta == "6":
            gestisci_categorie()
        elif scelta == "7":
            mostra_generatore_password()
        elif scelta == "0":
            print("Programma chiuso")
            break
        else:
            print("Scelta non valida")

def main():
    crea_database()
    print("Database creato correttamente")

    token = leggi_impostazione("verification_token")

    if token is None:
        chiave = primo_accesso()
    else:
        chiave = login()

    if chiave is not None:
        scelta_azione(chiave)

if __name__ == "__main__":
    main()
