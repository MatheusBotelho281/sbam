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
    cursor.execute("SELECT COUNT(*) FROM livros")
    if cursor.fetchone()[0] == 0:
        livros_exemplo = [
            (f"LIV{str(uuid.uuid4().int)[:6]}", 'A1', 'Introdução à Filosofia', 'Marilena Chaui', '2000-01-01', 'Disponível', '', ''),
            (f"LIV{str(uuid.uuid4().int)[:6]}", 'B2', 'Suma Teológica - Vol. 1', 'Santo Tomás de Aquino', '1265-01-01', 'Disponível', '', ''),
            (f"LIV{str(uuid.uuid4().int)[:6]}", 'C3', 'O Senhor dos Anéis', 'J.R.R. Tolkien', '1954-07-29', 'Emprestado', 'João da Silva', '2025-09-15')
        ]
        cursor.executemany("INSERT INTO livros VALUES (?, ?, ?, ?, ?, ?, ?, ?)", livros_exemplo)
        print("Banco de dados inicializado com dados de exemplo.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    inicializar_banco()