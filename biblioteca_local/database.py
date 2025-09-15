# database_usuarios.py
import sqlite3
import os

def inicializar_banco_usuarios():
    # Verifica se o banco já existe
    db_ja_existe = os.path.exists('usuarios_biblioteca.db')
    
    conn = sqlite3.connect('usuarios_biblioteca.db')
    cursor = conn.cursor()

    # Cria tabela de usuários se não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        etapa_formativa TEXT NOT NULL,
        numero_contato TEXT NOT NULL,
        ativo BOOLEAN DEFAULT 1,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Cria tabela de histórico de notificações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historico_notificacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        codigo_livro TEXT,
        nome_livro TEXT,
        tipo_notificacao TEXT,
        status_envio TEXT,
        data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')

    # Insere alguns usuários de exemplo se é a primeira vez
    if not db_ja_existe:
        usuarios_exemplo = [
            ('Teste Exemplo', '1º Ano Filosofia', '5511999999999'),
        ]
        
        cursor.executemany('''
        INSERT INTO usuarios (nome, etapa_formativa, numero_contato) VALUES (?, ?, ?)
        ''', usuarios_exemplo)
        
        print("Banco de dados de usuários criado com exemplos.")
    else:
        print("Banco de dados de usuários já existe. Estrutura verificada.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    inicializar_banco_usuarios()