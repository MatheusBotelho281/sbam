# database.py
import sqlite3
import uuid
from datetime import date

def inicializar_banco():
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()

    # Apaga a tabela antiga para garantir que a nova seja criada com a coluna certa
    cursor.execute('DROP TABLE IF EXISTS livros')

    # Cria a tabela de livros com a nova coluna 'data_emprestimo'
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

    print("Banco de dados inicializado com a estrutura de tabela vazia.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    # timedelta não é mais necessário aqui
    from datetime import date
    inicializar_banco()

