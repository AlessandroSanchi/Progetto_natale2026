import sqlite3
from flask import current_app, g

def get_db():
    """Restituisce la connessione al database per la richiesta corrente."""

    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE']
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """Chiude la connessione alla fine della richiesta."""
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    """Registra la funzione di chiusura automatica."""
    app.teardown_appcontext(close_db)