# app.py
import sqlite3
import uuid
import os
import sys
from flask import Flask, jsonify, render_template, request
import requests
from datetime import date, timedelta

# --- CÓDIGO ESSENCIAL PARA O PYINSTALLER ---
# Determina o caminho base, seja rodando como script ou como executável
def get_base_path():
    if getattr(sys, 'frozen', False):
        # Se estiver rodando como um executável do PyInstaller
        return sys._MEIPASS
    else:
        # Se estiver rodando como um script .py normal
        return os.path.abspath(".")

BASE_PATH = get_base_path()
# -----------------------------------------

# Modifique a linha de inicialização do Flask para usar o caminho base
app = Flask(__name__,
            template_folder=os.path.join(BASE_PATH, 'templates'),
            static_folder=os.path.join(BASE_PATH, 'static'))

# Chave da API do Google Books (opcional, para a funcionalidade de ISBN)
GOOGLE_API_KEY = "AIzaSyA9gO2r2Vxtx4n0j4WrfgMjDVaPwgKsUWs" # Chave da aplicação original

def get_db_connection():
    # Garante que o banco de dados seja encontrado no mesmo diretório do executável
    db_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'biblioteca.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# --- ROTAS DO FRONTEND ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_html(filename):
    # Evita que a rota capture caminhos de API ou estáticos
    if filename.startswith('api/') or filename.startswith('static/'):
        return "Not Found", 404
    return render_template(filename)

# --- ROTAS DA API ---

@app.route('/api/livros', methods=['GET'])
def get_livros():
    conn = get_db_connection()
    # Adiciona a coluna data_emprestimo na consulta para consistência
    livros_db = conn.execute('SELECT codigo, estante, nome, autor, data_publicacao, status, usuario, prazo, data_emprestimo FROM livros ORDER BY nome').fetchall()
    conn.close()
    
    header = ["codigo", "estante", "nome", "autor", "data_publicacao", "status", "usuario", "prazo", "data_emprestimo"]
    livros_list = [header] + [list(livro) for livro in livros_db]
    
    return jsonify(livros_list)

@app.route('/api/livros/emprestados')
def get_livros_emprestados():
    conn = get_db_connection()
    livros_db = conn.execute("SELECT * FROM livros WHERE status = 'Emprestado' ORDER BY prazo ASC").fetchall()
    conn.close()

    livros_list = [dict(livro) for livro in livros_db]
    
    response_data = {
        "livros": livros_list,
        "server_date": date.today().isoformat()
    }
    return jsonify(response_data)

@app.route('/api/livros/adicionar', methods=['POST'])
def add_livro():
    data = request.get_json()
    codigo = f"LIV{str(uuid.uuid4().int)[:6]}"
    
    conn = get_db_connection()
    # Adiciona a coluna data_emprestimo (vazia) na inserção
    conn.execute('INSERT INTO livros (codigo, estante, nome, autor, data_publicacao, status, usuario, prazo, data_emprestimo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 (codigo, data['estante'], data['nome'], data['autor'], data['data'], 'Disponível', '', '', ''))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "codigo": codigo})

@app.route('/api/livros/atualizar-status', methods=['POST'])
def update_status():
    data = request.get_json()
    conn = get_db_connection()
    
    codigos = data.get('codigos', [])
    if not codigos:
        codigos = [data.get('codigo')]

    status = data.get('status')
    usuario = data.get('usuario', '')
    prazo = data.get('prazo', '')
    
    data_emprestimo = ''
    if status == 'Emprestado':
        data_emprestimo = date.today().isoformat()

    for codigo in codigos:
        if not codigo: continue
        
        conn.execute('UPDATE livros SET status = ?, usuario = ?, prazo = ?, data_emprestimo = ? WHERE codigo = ?',
                     (status, usuario, prazo, data_emprestimo, codigo))

    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/buscar-isbn')
def buscar_isbn():
    isbn = request.args.get('isbn')
    if not isbn:
        return jsonify({"error": "ISBN não fornecido"}), 400
    
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={GOOGLE_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Erro ao contatar a API do Google Books: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=9991)

