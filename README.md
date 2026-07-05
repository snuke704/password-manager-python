# Password Manager

Progetto Python per un esame: un password manager con database SQLite e crittografia delle credenziali tramite master password.

## Funzionalita presenti

- Creazione della master password al primo avvio
- Login tramite master password
- Crittografia di username e password salvati
- Database SQLite locale
- Inserimento, visualizzazione, modifica ed eliminazione dei login
- Inserimento, modifica ed eliminazione delle categorie
- Generatore di password personalizzabile
- Interfaccia grafica con Tkinter

## Avvio su Linux

Installa Tkinter, se non e gia presente:

```bash
sudo apt install python3-tk
```

Crea e attiva un ambiente virtuale:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Installa le dipendenze:

```bash
python -m pip install -r requirements.txt
```

Avvia il programma:

```bash
python main.py
```

## Avvio su Windows

Da PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Note

Il file `password_manager.db` non viene caricato su GitHub perche contiene dati locali. Il database viene creato automaticamente all'avvio.
