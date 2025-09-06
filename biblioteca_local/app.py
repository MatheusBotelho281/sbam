# app.py
import sqlite3
import uuid
from flask import Flask, jsonify, render_template, request
import requests
from datetime import date, timedelta

app = Flask(__name__, template_folder='templates', static_folder='static')

# Chave da API do Google Books (opcional, para a funcionalidade de ISBN)
GOOGLE_API_KEY = "AIzaSyA9gO2r2Vxtx4n0j4WrfgMjDVaPwgKsUWs" # Chave da aplicação original

def get_db_connection():
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_html(filename):
    return render_template(filename)

@app.route('/api/livros', methods=['GET'])
def get_livros():
    conn = get_db_connection()
    livros_db = conn.execute('SELECT * FROM livros ORDER BY nome').fetchall()
    conn.close()
    
    # Simula a estrutura de retorno da API do Google Sheets (cabeçalho + dados)
    header = ["código", "estante", "nome", "autor", "data_publicacao", "status", "usuario", "prazo"]
    livros_list = [header] + [list(livro) for livro in livros_db]
    
    return jsonify(livros_list)

@app.route('/api/livros/adicionar', methods=['POST'])
def add_livro():
    data = request.get_json()
    codigo = f"LIV{str(uuid.uuid4().int)[:6]}"
    
    conn = get_db_connection()
    conn.execute('INSERT INTO livros (codigo, estante, nome, autor, data_publicacao, status, usuario, prazo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                 (codigo, data['estante'], data['nome'], data['autor'], data['data'], 'Disponível', '', ''))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "codigo": codigo})

@app.route('/api/livros/atualizar-status', methods=['POST'])
def update_status():
    data = request.get_json()
    conn = get_db_connection()
    
    # Lida com múltiplos livros (para empréstimo/devolução em lote)
    codigos = data.get('codigos', [])
    if not codigos: # Fallback para código único
        codigos = [data.get('codigo')]

    for codigo in codigos:
        if not codigo: continue
        
        status = data.get('status')
        usuario = data.get('usuario', '')
        prazo = data.get('prazo', '')
        
        conn.execute('UPDATE livros SET status = ?, usuario = ?, prazo = ? WHERE codigo = ?',
                     (status, usuario, prazo, codigo))

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
        response.raise_for_status() # Lança um erro para status HTTP ruins
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Erro ao contatar a API do Google Books: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)