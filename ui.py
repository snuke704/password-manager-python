import base64
import os
import sys
import string


def sistema_percorso_tkinter():
    cartella_python = sys.base_prefix
    cartella_tcl = os.path.join(cartella_python, "tcl", "tcl8.6")
    cartella_tk = os.path.join(cartella_python, "tcl", "tk8.6")

    if os.path.exists(os.path.join(cartella_tcl, "init.tcl")):
        os.environ["TCL_LIBRARY"] = cartella_tcl

    if os.path.exists(os.path.join(cartella_tk, "tk.tcl")):
        os.environ["TK_LIBRARY"] = cartella_tk


sistema_percorso_tkinter()

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from cryptography.fernet import InvalidToken

from crypto_utils import (
    cripta_testo,
    decripta_testo,
    genera_chiave,
    genera_password_personalizzata,
)
from database import (
    aggiungi_categoria,
    aggiungi_password,
    crea_database,
    elimina_categoria,
    elimina_password,
    leggi_impostazione,
    leggi_nome_categoria,
    leggi_password_per_id,
    modifica_password,
    rinomina_categoria,
    salva_impostazione,
    vedi_categorie,
    vedi_tutti_login,
)


TOKEN_VERIFICA = "main_pass_ok"


def valida_master_password(password):
    if len(password) < 10:
        return False

    ha_maiuscola = any(carattere.isupper() for carattere in password)
    ha_minuscola = any(carattere.islower() for carattere in password)
    ha_numero = any(carattere.isdigit() for carattere in password)
    ha_speciale = any(carattere in string.punctuation for carattere in password)

    return ha_maiuscola and ha_minuscola and ha_numero and ha_speciale


class PasswordManagerApp:
    def __init__(self):
        crea_database()

        self.finestra = tk.Tk()
        self.finestra.title("Password Manager")
        self.finestra.geometry("950x600")

        self.chiave = None
        self.frame_attuale = None
        self.cerca_var = tk.StringVar()
        self.filtro_categoria_var = tk.StringVar(value="Tutte")

        self.configura_stile()
        self.mostra_schermata_accesso()

    def configura_stile(self):
        stile = ttk.Style()
        stile.theme_use("clam")
        stile.configure("TButton", padding=6)
        stile.configure("Treeview", rowheight=28)

    def avvia(self):
        self.finestra.mainloop()

    def pulisci_finestra(self):
        if self.frame_attuale is not None:
            self.frame_attuale.destroy()

    def master_password_esiste(self):
        salt = leggi_impostazione("salt")
        token = leggi_impostazione("verification_token")
        return salt is not None and token is not None

    def mostra_schermata_accesso(self):
        self.pulisci_finestra()
        self.chiave = None

        primo_accesso = not self.master_password_esiste()

        frame = ttk.Frame(self.finestra, padding=30)
        frame.pack(fill="both", expand=True)
        self.frame_attuale = frame

        titolo = "Crea cassaforte" if primo_accesso else "Accedi alla cassaforte"
        ttk.Label(frame, text=titolo, font=("Segoe UI", 18, "bold")).pack(pady=(40, 20))

        ttk.Label(frame, text="Master password").pack()

        password_var = tk.StringVar()
        password_entry = ttk.Entry(frame, textvariable=password_var, show="*", width=35)
        password_entry.pack(pady=5)

        mostra_password_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame,
            text="Mostra password",
            variable=mostra_password_var,
            command=lambda: self.mostra_o_nascondi_password(password_entry, mostra_password_var),
        ).pack()

        if primo_accesso:
            ttk.Label(frame, text="Conferma master password").pack(pady=(15, 0))

            conferma_var = tk.StringVar()
            conferma_entry = ttk.Entry(frame, textvariable=conferma_var, show="*", width=35)
            conferma_entry.pack(pady=5)

            mostra_conferma_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                frame,
                text="Mostra conferma",
                variable=mostra_conferma_var,
                command=lambda: self.mostra_o_nascondi_password(conferma_entry, mostra_conferma_var),
            ).pack()
        else:
            conferma_var = None

        def invia():
            password = password_var.get()

            if primo_accesso:
                self.crea_cassaforte(password, conferma_var.get())
            else:
                self.accedi_cassaforte(password)

        testo_bottone = "Crea e accedi" if primo_accesso else "Accedi"
        ttk.Button(frame, text=testo_bottone, command=invia).pack(pady=20)

        password_entry.focus()
        password_entry.bind("<Return>", lambda evento: invia())

    def mostra_o_nascondi_password(self, entry, variabile):
        if variabile.get():
            entry.config(show="")
        else:
            entry.config(show="*")

    def crea_cassaforte(self, password, conferma):
        if not valida_master_password(password):
            messagebox.showerror(
                "Errore",
                "La master password deve avere almeno 10 caratteri, maiuscole, minuscole, numeri e simboli.",
            )
            return

        if password != conferma:
            messagebox.showerror("Errore", "Le password non coincidono.")
            return

        salt = os.urandom(16)
        self.chiave = genera_chiave(password, salt)
        token_criptato = cripta_testo(TOKEN_VERIFICA, self.chiave)

        salva_impostazione("salt", base64.b64encode(salt).decode())
        salva_impostazione("verification_token", token_criptato)

        messagebox.showinfo("OK", "Cassaforte creata correttamente.")
        self.mostra_schermata_principale()

    def accedi_cassaforte(self, password):
        salt_testo = leggi_impostazione("salt")
        token_criptato = leggi_impostazione("verification_token")

        try:
            salt = base64.b64decode(salt_testo)
            chiave = genera_chiave(password, salt)
            token = decripta_testo(token_criptato, chiave)
        except (InvalidToken, ValueError, TypeError):
            messagebox.showerror("Errore", "Master password errata.")
            return

        if token != TOKEN_VERIFICA:
            messagebox.showerror("Errore", "Master password errata.")
            return

        self.chiave = chiave
        self.mostra_schermata_principale()

    def mostra_schermata_principale(self):
        self.pulisci_finestra()

        frame = ttk.Frame(self.finestra, padding=15)
        frame.pack(fill="both", expand=True)
        self.frame_attuale = frame

        barra_superiore = ttk.Frame(frame)
        barra_superiore.pack(fill="x", pady=(0, 10))

        ttk.Label(barra_superiore, text="Password Manager", font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Button(barra_superiore, text="Blocca", command=self.mostra_schermata_accesso).pack(side="right", padx=4)
        ttk.Button(barra_superiore, text="Categorie", command=self.apri_finestra_categorie).pack(side="right", padx=4)
        ttk.Button(barra_superiore, text="Genera password", command=self.apri_generatore_password).pack(side="right", padx=4)
        ttk.Button(barra_superiore, text="Aggiungi", command=self.apri_form_login).pack(side="right", padx=4)

        filtri = ttk.Frame(frame)
        filtri.pack(fill="x", pady=(0, 10))

        ttk.Label(filtri, text="Cerca").pack(side="left")
        cerca_entry = ttk.Entry(filtri, textvariable=self.cerca_var)
        cerca_entry.pack(side="left", fill="x", expand=True, padx=8)
        cerca_entry.bind("<KeyRelease>", lambda evento: self.aggiorna_tabella())

        ttk.Label(filtri, text="Categoria").pack(side="left")
        self.combo_filtro_categoria = ttk.Combobox(
            filtri,
            textvariable=self.filtro_categoria_var,
            values=self.lista_categorie_per_filtro(),
            state="readonly",
            width=20,
        )
        self.combo_filtro_categoria.pack(side="left", padx=8)
        self.combo_filtro_categoria.bind("<<ComboboxSelected>>", lambda evento: self.aggiorna_tabella())

        colonne = ("titolo", "sito", "categoria")
        self.tabella = ttk.Treeview(frame, columns=colonne, show="headings")
        self.tabella.heading("titolo", text="Titolo")
        self.tabella.heading("sito", text="Sito")
        self.tabella.heading("categoria", text="Categoria")
        self.tabella.pack(fill="both", expand=True)
        self.tabella.bind("<Double-1>", lambda evento: self.modifica_login_selezionato())

        bottoni = ttk.Frame(frame)
        bottoni.pack(fill="x", pady=10)

        ttk.Button(bottoni, text="Visualizza", command=self.visualizza_login_selezionato).pack(side="left", padx=4)
        ttk.Button(bottoni, text="Modifica", command=self.modifica_login_selezionato).pack(side="left", padx=4)
        ttk.Button(bottoni, text="Elimina", command=self.elimina_login_selezionato).pack(side="left", padx=4)

        self.aggiorna_tabella()

    def lista_categorie_per_filtro(self):
        categorie = ["Tutte", "Senza categoria"]

        for _id, nome in vedi_categorie():
            categorie.append(nome)

        return categorie

    def lista_categorie_per_form(self):
        categorie = [""]

        for _id, nome in vedi_categorie():
            categorie.append(nome)

        return categorie

    def aggiorna_tabella(self):
        for riga in self.tabella.get_children():
            self.tabella.delete(riga)

        testo_cercato = self.cerca_var.get().strip().lower()
        filtro_categoria = self.filtro_categoria_var.get()

        for id_login, titolo, sito, categoria_id in vedi_tutti_login():
            categoria = leggi_nome_categoria(categoria_id) or "Senza categoria"

            contiene_testo = (
                testo_cercato in titolo.lower()
                or testo_cercato in (sito or "").lower()
                or testo_cercato in categoria.lower()
            )
            categoria_corretta = filtro_categoria == "Tutte" or filtro_categoria == categoria

            if contiene_testo and categoria_corretta:
                self.tabella.insert("", "end", iid=id_login, values=(titolo, sito or "", categoria))

        categorie = self.lista_categorie_per_filtro()
        self.combo_filtro_categoria.config(values=categorie)

        if self.filtro_categoria_var.get() not in categorie:
            self.filtro_categoria_var.set("Tutte")

    def leggi_login_decriptato(self, id_login):
        risultato = leggi_password_per_id(id_login)

        if risultato is None:
            return None

        titolo, username_criptato, password_criptata, sito, categoria_id = risultato

        try:
            username = decripta_testo(username_criptato, self.chiave)
            password = decripta_testo(password_criptata, self.chiave)
        except InvalidToken:
            messagebox.showerror("Errore", "Impossibile decriptare il login.")
            return None

        return {
            "id": id_login,
            "titolo": titolo,
            "username": username,
            "password": password,
            "sito": sito or "",
            "categoria": leggi_nome_categoria(categoria_id) or "",
        }

    def id_login_selezionato(self):
        selezione = self.tabella.selection()

        if not selezione:
            messagebox.showwarning("Attenzione", "Seleziona prima un login.")
            return None

        return int(selezione[0])

    def apri_form_login(self, login=None):
        finestra = tk.Toplevel(self.finestra)
        finestra.title("Modifica login" if login else "Aggiungi login")
        finestra.geometry("450x430")

        frame = ttk.Frame(finestra, padding=15)
        frame.pack(fill="both", expand=True)

        titolo_var = tk.StringVar(value=login["titolo"] if login else "")
        username_var = tk.StringVar(value=login["username"] if login else "")
        password_var = tk.StringVar(value=login["password"] if login else "")
        sito_var = tk.StringVar(value=login["sito"] if login else "")
        categoria_var = tk.StringVar(value=login["categoria"] if login else "")

        self.crea_campo_testo(frame, "Titolo", titolo_var)
        self.crea_campo_testo(frame, "Username", username_var)

        ttk.Label(frame, text="Password").pack(anchor="w", pady=(10, 0))
        riga_password = ttk.Frame(frame)
        riga_password.pack(fill="x")

        password_entry = ttk.Entry(riga_password, textvariable=password_var, show="*")
        password_entry.pack(side="left", fill="x", expand=True)

        mostra_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            riga_password,
            text="Mostra",
            variable=mostra_var,
            command=lambda: self.mostra_o_nascondi_password(password_entry, mostra_var),
        ).pack(side="left", padx=5)

        ttk.Button(
            riga_password,
            text="Genera",
            command=lambda: self.apri_generatore_password(password_var),
        ).pack(side="left", padx=5)

        self.crea_campo_testo(frame, "Sito", sito_var)

        ttk.Label(frame, text="Categoria").pack(anchor="w", pady=(10, 0))
        categoria_combo = ttk.Combobox(frame, textvariable=categoria_var, values=self.lista_categorie_per_form())
        categoria_combo.pack(fill="x")

        def salva_login():
            titolo = titolo_var.get().strip()
            username = username_var.get().strip()
            password = password_var.get().strip()
            sito = sito_var.get().strip()
            categoria = categoria_var.get().strip()

            if not titolo or not username or not password:
                messagebox.showerror("Errore", "Titolo, username e password sono obbligatori.")
                return

            categoria_id = None
            if categoria:
                categoria_id = aggiungi_categoria(categoria)

            username_criptato = cripta_testo(username, self.chiave)
            password_criptata = cripta_testo(password, self.chiave)

            if login is None:
                aggiungi_password(titolo, username_criptato, password_criptata, sito, categoria_id)
            else:
                modifica_password(login["id"], titolo, username_criptato, password_criptata, sito, categoria_id)

            self.aggiorna_tabella()
            finestra.destroy()

        bottoni = ttk.Frame(frame)
        bottoni.pack(fill="x", pady=20)

        ttk.Button(bottoni, text="Annulla", command=finestra.destroy).pack(side="right", padx=5)
        ttk.Button(bottoni, text="Salva", command=salva_login).pack(side="right", padx=5)

    def crea_campo_testo(self, frame, testo, variabile):
        ttk.Label(frame, text=testo).pack(anchor="w", pady=(10, 0))
        entry = ttk.Entry(frame, textvariable=variabile)
        entry.pack(fill="x")
        return entry

    def visualizza_login_selezionato(self):
        id_login = self.id_login_selezionato()

        if id_login is None:
            return

        login = self.leggi_login_decriptato(id_login)

        if login is None:
            return

        categoria = login["categoria"] or "Senza categoria"
        testo = (
            f"Titolo: {login['titolo']}\n"
            f"Username: {login['username']}\n"
            f"Password: {login['password']}\n"
            f"Sito: {login['sito'] or 'Nessun sito'}\n"
            f"Categoria: {categoria}"
        )
        messagebox.showinfo("Login salvato", testo)

    def modifica_login_selezionato(self):
        id_login = self.id_login_selezionato()

        if id_login is None:
            return

        login = self.leggi_login_decriptato(id_login)

        if login is not None:
            self.apri_form_login(login)

    def elimina_login_selezionato(self):
        id_login = self.id_login_selezionato()

        if id_login is None:
            return

        login = self.leggi_login_decriptato(id_login)

        if login is None:
            return

        conferma = messagebox.askyesno("Conferma", f"Vuoi eliminare '{login['titolo']}'?")

        if conferma:
            elimina_password(id_login)
            self.aggiorna_tabella()

    def apri_finestra_categorie(self):
        finestra = tk.Toplevel(self.finestra)
        finestra.title("Categorie")
        finestra.geometry("400x380")

        frame = ttk.Frame(finestra, padding=15)
        frame.pack(fill="both", expand=True)

        lista = tk.Listbox(frame)
        lista.pack(fill="both", expand=True)

        def aggiorna_lista():
            lista.delete(0, tk.END)

            for id_categoria, nome in vedi_categorie():
                lista.insert(tk.END, f"{id_categoria} - {nome}")

            self.aggiorna_tabella()

        def categoria_selezionata():
            selezione = lista.curselection()

            if not selezione:
                messagebox.showwarning("Attenzione", "Seleziona prima una categoria.")
                return None

            testo = lista.get(selezione[0])
            id_categoria, nome = testo.split(" - ", 1)
            return int(id_categoria), nome

        def aggiungi_nuova_categoria():
            nome = simpledialog.askstring("Nuova categoria", "Nome categoria:", parent=finestra)

            if nome is None:
                return

            nome = nome.strip()

            if not nome:
                messagebox.showerror("Errore", "Il nome non puo essere vuoto.")
                return

            aggiungi_categoria(nome)
            aggiorna_lista()

        def rinomina_categoria_selezionata():
            categoria = categoria_selezionata()

            if categoria is None:
                return

            id_categoria, nome_vecchio = categoria
            nome_nuovo = simpledialog.askstring("Rinomina categoria", "Nuovo nome:", initialvalue=nome_vecchio)

            if nome_nuovo is None:
                return

            nome_nuovo = nome_nuovo.strip()

            if not nome_nuovo:
                messagebox.showerror("Errore", "Il nome non puo essere vuoto.")
                return

            risultato = rinomina_categoria(id_categoria, nome_nuovo)

            if risultato is None:
                messagebox.showerror("Errore", "Esiste gia una categoria con questo nome.")
                return

            aggiorna_lista()

        def elimina_categoria_selezionata():
            categoria = categoria_selezionata()

            if categoria is None:
                return

            id_categoria, nome = categoria
            conferma = messagebox.askyesno(
                "Conferma",
                f"Vuoi eliminare '{nome}'?\nLe password collegate resteranno senza categoria.",
            )

            if conferma:
                elimina_categoria(id_categoria)
                aggiorna_lista()

        bottoni = ttk.Frame(frame)
        bottoni.pack(fill="x", pady=10)

        ttk.Button(bottoni, text="Aggiungi", command=aggiungi_nuova_categoria).pack(side="left", padx=3)
        ttk.Button(bottoni, text="Rinomina", command=rinomina_categoria_selezionata).pack(side="left", padx=3)
        ttk.Button(bottoni, text="Elimina", command=elimina_categoria_selezionata).pack(side="left", padx=3)
        ttk.Button(bottoni, text="Chiudi", command=finestra.destroy).pack(side="right", padx=3)

        aggiorna_lista()

    def apri_generatore_password(self, variabile_destinazione=None):
        finestra = tk.Toplevel(self.finestra)
        finestra.title("Generatore password")
        finestra.geometry("420x380")

        frame = ttk.Frame(finestra, padding=15)
        frame.pack(fill="both", expand=True)

        lunghezza_var = tk.IntVar(value=16)
        maiuscole_var = tk.BooleanVar(value=True)
        minuscole_var = tk.BooleanVar(value=True)
        numeri_var = tk.BooleanVar(value=True)
        simboli_var = tk.BooleanVar(value=True)
        minimo_numeri_var = tk.IntVar(value=2)
        minimo_simboli_var = tk.IntVar(value=1)
        risultato_var = tk.StringVar()

        ttk.Label(frame, text="Lunghezza").pack(anchor="w")
        ttk.Spinbox(frame, from_=4, to=64, textvariable=lunghezza_var, width=8).pack(anchor="w")

        ttk.Checkbutton(frame, text="Maiuscole", variable=maiuscole_var).pack(anchor="w", pady=(10, 0))
        ttk.Checkbutton(frame, text="Minuscole", variable=minuscole_var).pack(anchor="w")
        ttk.Checkbutton(frame, text="Numeri", variable=numeri_var).pack(anchor="w")
        ttk.Checkbutton(frame, text="Simboli", variable=simboli_var).pack(anchor="w")

        ttk.Label(frame, text="Minimo numeri").pack(anchor="w", pady=(10, 0))
        ttk.Spinbox(frame, from_=0, to=20, textvariable=minimo_numeri_var, width=8).pack(anchor="w")

        ttk.Label(frame, text="Minimo simboli").pack(anchor="w", pady=(10, 0))
        ttk.Spinbox(frame, from_=0, to=20, textvariable=minimo_simboli_var, width=8).pack(anchor="w")

        ttk.Label(frame, text="Password generata").pack(anchor="w", pady=(10, 0))
        ttk.Entry(frame, textvariable=risultato_var).pack(fill="x")

        def genera():
            try:
                password = genera_password_personalizzata(
                    lunghezza_var.get(),
                    maiuscole_var.get(),
                    minuscole_var.get(),
                    numeri_var.get(),
                    simboli_var.get(),
                    minimo_numeri_var.get() if numeri_var.get() else 0,
                    minimo_simboli_var.get() if simboli_var.get() else 0,
                )
                risultato_var.set(password)
            except ValueError as errore:
                messagebox.showerror("Errore", str(errore))

        def usa_password():
            if not risultato_var.get():
                genera()

            if risultato_var.get() and variabile_destinazione is not None:
                variabile_destinazione.set(risultato_var.get())
                finestra.destroy()

        bottoni = ttk.Frame(frame)
        bottoni.pack(fill="x", pady=15)

        ttk.Button(bottoni, text="Genera", command=genera).pack(side="left", padx=3)

        if variabile_destinazione is not None:
            ttk.Button(bottoni, text="Usa password", command=usa_password).pack(side="left", padx=3)

        ttk.Button(bottoni, text="Chiudi", command=finestra.destroy).pack(side="right", padx=3)

        genera()


def avvia_app():
    app = PasswordManagerApp()
    app.avvia()
