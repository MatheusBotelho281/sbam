import sqlite3
import os

def inicializar_banco():
    # Verifica se o banco de dados já existe para dar uma mensagem clara ao usuário
    db_ja_existe = os.path.exists('biblioteca.db')
    
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()

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

def inicializar_banco_acervo():
    conn = sqlite3.connect('acervo_digital.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS arquivos_digitais (
        codigo TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        autor TEXT NOT NULL,
        caminho_arquivo TEXT NOT NULL,
        tamanho REAL,
        formato TEXT
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    inicializar_banco_acervo()
    inicializar_banco()
    inicializar_banco_usuarios()