import sqlite3
import traceback 
import uuid
from werkzeug.utils import secure_filename
import os
import sys
from flask import Flask, jsonify, render_template, request
from flask import render_template, redirect, url_for, send_from_directory, flash
import requests
from datetime import date, timedelta
import subprocess


# --- CÓDIGO ESSENCIAL PARA O PYINSTALLER ---
def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.abspath(".")

BASE_PATH = get_base_path()
# -----------------------------------------

app = Flask(__name__,
            template_folder=os.path.join(BASE_PATH, 'templates'),
            static_folder=os.path.join(BASE_PATH, 'static'))
app.secret_key = 'uma_chave_secreta_muito_unica_e_segura' 

GOOGLE_API_KEY = "AIzaSyA9gO2r2Vxtx4n0j4WrfgMjDVaPwgKsUWs"

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'biblioteca.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/livros', methods=['GET'])
def get_livros():
    conn = get_db_connection()
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

def get_db_usuarios_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'usuarios_biblioteca.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/usuarios/inicializar', methods=['POST'])
def inicializar_usuarios():
    try:
        result = subprocess.run([sys.executable, 'database_usuarios.py'], 
                              capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(sys.argv[0])))
        
        if result.returncode == 0:
            return jsonify({"success": True, "message": "Banco de usuários inicializado com sucesso"})
        else:
            return jsonify({"success": False, "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/usuarios/listar', methods=['GET'])
def listar_usuarios():
    try:
        conn = get_db_usuarios_connection()
        usuarios = conn.execute('''
            SELECT id, nome, etapa_formativa, numero_contato, ativo, data_cadastro 
            FROM usuarios 
            ORDER BY nome
        ''').fetchall()
        conn.close()
        
        usuarios_list = [dict(usuario) for usuario in usuarios]
        return jsonify(usuarios_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/usuarios/adicionar', methods=['POST'])
def adicionar_usuario():
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        etapa_formativa = data.get('etapa_formativa', '').strip()
        numero_contato = data.get('numero_contato', '').strip()
        
        if not all([nome, etapa_formativa, numero_contato]):
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400
        
        conn = get_db_usuarios_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nome, etapa_formativa, numero_contato) 
            VALUES (?, ?, ?)
        ''', (nome, etapa_formativa, numero_contato))
        conn.commit()
        usuario_id = cursor.lastrowid
        conn.close()
        
        return jsonify({"success": True, "id": usuario_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/usuarios/editar/<int:usuario_id>', methods=['PUT'])
def editar_usuario(usuario_id):
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        etapa_formativa = data.get('etapa_formativa', '').strip()
        numero_contato = data.get('numero_contato', '').strip()
        ativo = data.get('ativo', True)
        
        if not all([nome, etapa_formativa, numero_contato]):
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400
        
        conn = get_db_usuarios_connection()
        conn.execute('''
            UPDATE usuarios 
            SET nome = ?, etapa_formativa = ?, numero_contato = ?, ativo = ?
            WHERE id = ?
        ''', (nome, etapa_formativa, numero_contato, ativo, usuario_id))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/usuarios/excluir/<int:usuario_id>', methods=['DELETE'])
def excluir_usuario(usuario_id):
    try:
        conn = get_db_usuarios_connection()
        conn.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/usuarios/notificacao', methods=['POST'])
def registrar_notificacao():
    try:
        data = request.get_json()
        usuario_id = data.get('usuario_id')
        codigo_livro = data.get('codigo_livro', '')
        tipo_notificacao = data.get('tipo_notificacao')
        
        nome_livro = ''
        if codigo_livro:
            conn_livros = get_db_connection()
            livro = conn_livros.execute('SELECT nome FROM livros WHERE codigo = ?', (codigo_livro,)).fetchone()
            if livro:
                nome_livro = livro['nome']
            conn_livros.close()
        
        conn = get_db_usuarios_connection()
        conn.execute('''
            INSERT INTO historico_notificacoes 
            (usuario_id, codigo_livro, nome_livro, tipo_notificacao, status_envio) 
            VALUES (?, ?, ?, ?, ?)
        ''', (usuario_id, codigo_livro, nome_livro, tipo_notificacao, 'enviado'))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/usuarios/historico/<int:usuario_id>', methods=['GET'])
def historico_notificacoes_usuario(usuario_id):
    try:
        conn = get_db_usuarios_connection()
        historico = conn.execute('''
            SELECT h.*, u.nome as nome_usuario
            FROM historico_notificacoes h
            JOIN usuarios u ON h.usuario_id = u.id
            WHERE h.usuario_id = ?
            ORDER BY h.data_envio DESC
        ''', (usuario_id,)).fetchall()
        conn.close()
        
        historico_list = [dict(item) for item in historico]
        return jsonify(historico_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/usuarios/buscar-por-nome', methods=['GET'])
def buscar_usuario_por_nome():
    termo = request.args.get('termo', '').strip()
    if not termo:
        return jsonify([])
    
    try:
        conn = get_db_usuarios_connection()
        usuarios = conn.execute('''
            SELECT id, nome, etapa_formativa, numero_contato 
            FROM usuarios 
            WHERE ativo = 1 AND nome LIKE ? 
            ORDER BY nome
            LIMIT 10
        ''', (f'%{termo}%',)).fetchall()
        conn.close()
        
        usuarios_list = [dict(usuario) for usuario in usuarios]
        return jsonify(usuarios_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/usuarios/emprestimos/<int:usuario_id>')
def emprestimos_usuario(usuario_id):
    try:
        conn_usuarios = get_db_usuarios_connection()
        usuario = conn_usuarios.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        conn_usuarios.close()

        if not usuario:
            return jsonify([]) # Retorna lista vazia se o usuário não for encontrado

        conn_livros = get_db_connection()
        livros = conn_livros.execute(
            # AQUI: Adicionamos 'estante' e 'autor' na consulta
            "SELECT codigo, nome, autor, estante, prazo FROM livros WHERE usuario = ?",
            (usuario['nome'],)
        ).fetchall()
        conn_livros.close()
        
        return jsonify([dict(l) for l in livros])
    except Exception as e:
        print(f"Erro ao buscar empréstimos do usuário {usuario_id}: {e}")
        return jsonify({"error": "Erro ao buscar empréstimos"}), 500


# Configuração para salvar os arquivos
UPLOAD_FOLDER = 'acervo_digital'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para conectar ao banco de dados do acervo
def get_db_acervo():
    conn = sqlite3.connect('acervo_digital.db')
    conn.row_factory = sqlite3.Row
    return conn

# Rota para a página de upload (Admin)
# Rota para a página de upload (Admin)
@app.route('/upload-digital')
def upload_digital_page():
    conn = get_db_acervo()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM arquivos_digitais ORDER BY nome")
    livros = cursor.fetchall()
    conn.close()
    
    # Adicione esta linha para verificar o conteúdo da lista
    print("Livros encontrados no banco de dados:", livros) 
    
    return render_template('upload.html', livros=livros)
# Rota para processar o upload do arquivo
# Rota para processar o upload do arquivo
@app.route('/upload-livro-digital', methods=['POST'])
def upload_livro_digital():
    if 'arquivo' not in request.files:
        flash('Nenhum arquivo enviado.', 'error')
        return redirect(url_for('upload_digital_page'))

    file = request.files['arquivo']
    nome = request.form['nome']
    autor = request.form['autor']

    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('upload_digital_page'))
    
    if file and (file.filename.endswith('.pdf') or file.filename.endswith('.epub')):
        conn = None 
        try:
            # Salva o arquivo no servidor
            original_filename = secure_filename(file.filename)
            # Use um UUID para um código verdadeiramente único
            codigo_livro = uuid.uuid4().hex
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
            file.save(filepath)

            # Insere os dados no banco de dados
            conn = get_db_acervo()
            cursor = conn.cursor()
            
            tamanho = os.path.getsize(filepath)
            formato = os.path.splitext(original_filename)[1].replace('.', '')

            cursor.execute("INSERT INTO arquivos_digitais (codigo, nome, autor, caminho_arquivo, tamanho, formato) VALUES (?, ?, ?, ?, ?, ?)",
                           (codigo_livro, nome, autor, filepath, tamanho, formato))
            conn.commit()
            
            flash('Livro digital enviado com sucesso!', 'success')
            return redirect(url_for('upload_digital_page'))

        except Exception as e:
            traceback.print_exc()
            flash(f'Erro no upload: {e}', 'error')
            
            # Se o upload do arquivo falhou, remove o arquivo salvo
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
            
            return redirect(url_for('upload_digital_page'))
        
        finally:
            if conn:
                conn.close()

    flash('Formato de arquivo inválido. Apenas PDF e EPUB são permitidos.', 'error')
    return redirect(url_for('upload_digital_page'))
# Rota para a página do catálogo digital
@app.route('/catalogo-digital')
def catalogo_digital():
    # seu código para buscar os livros aqui
    conn = get_db_acervo()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM arquivos_digitais")
    livros = cursor.fetchall()
    conn.close()
    return render_template('catalogo_digital.html', livros=livros)

@app.template_filter('filesizeformat')
def filesizeformat_filter(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"
    
# Rota para download do arquivo
@app.route('/download/<codigo>')
def download_file(codigo):
    conn = get_db_acervo()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM arquivos_digitais WHERE codigo = ?", (codigo,))
    livro = cursor.fetchone()
    conn.close()

    if livro:
        # Pega o caminho do arquivo e envia para o usuário
        return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=os.path.basename(livro['caminho_arquivo']), as_attachment=True)
    else:
        flash('Arquivo não encontrado.', 'error')
        return redirect(url_for('catalogo_digital'))


if __name__ == '__main__':
    app.run(debug=True, port=9991)