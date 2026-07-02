# Password Manager

Progetto Python per un esame: un password manager con database SQLite e crittografia delle credenziali tramite master password.

## Funzionalita presenti

- Creazione della master password al primo avvio
- Login tramite master password
- Crittografia di username e password salvati
- Database SQLite locale
- Inserimento, visualizzazione, modifica ed eliminazione dei login
- Gestione base delle categorie durante il salvataggio dei login

## Avvio

Installa le dipendenze:

```bash
pip install -r requirements.txt
```

Esegui il programma:

```bash
python main.py
```

## Note

Il file `password_manager.db` non viene caricato su GitHub perche contiene dati locali. Il database viene creato automaticamente all'avvio.
