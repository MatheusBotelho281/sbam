# database.py
import sqlite3
import uuid
from datetime import date

def inicializar_banco():
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()

    # Cria a tabela de livros se ela não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS livros (
        codigo TEXT PRIMARY KEY,
        estante TEXT,
        nome TEXT,
        autor TEXT,
        data_publicacao TEXT,
        status TEXT,
        usuario TEXT,
        prazo TEXT
    )
    ''')

    # Adiciona alguns dados de exemplo se a tabela estiver vazia
    conn.commit()
    conn.close()

if __name__ == '__main__':
    inicializar_banco()