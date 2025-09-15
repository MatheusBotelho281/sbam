# database.py
import sqlite3
import os
from datetime import date

def inicializar_banco():
    # Verifica se o banco de dados já existe para dar uma mensagem clara ao usuário
    db_ja_existe = os.path.exists('biblioteca.db')
    
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()

    # REMOVIDO: A linha "DROP TABLE" foi removida para não apagar seus dados.

    # A instrução 'IF NOT EXISTS' é a chave aqui. Ela garante que a tabela
    # só seja criada se ela realmente não existir no banco de dados.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS livros (
        codigo TEXT PRIMARY KEY,
        estante TEXT,
        nome TEXT,
        autor TEXT,
        data_publicacao TEXT,
        status TEXT,
        usuario TEXT,
        prazo TEXT,
        data_emprestimo TEXT
    )
    ''')

    if not db_ja_existe:
        print("Banco de dados 'biblioteca.db' não encontrado. Um novo arquivo foi criado.")
    else:
        print("Banco de dados 'biblioteca.db' já existe. Estrutura verificada.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    inicializar_banco()

