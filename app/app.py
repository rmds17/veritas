import os
from flask import Flask, request, render_template, redirect, url_for, flash, g, session
import mysql.connector
from werkzeug.utils import secure_filename


app = Flask(__name__)


app.secret_key = '24e23c43d423c434343vfghfgd'


# Configurações do banco de dados a partir das variáveis de ambiente
app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'db')
app.config['MYSQL_USER'] = os.getenv('DB_USER', 'veritas_user')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', '1234')
app.config['MYSQL_DATABASE'] = os.getenv('DB_NAME', 'veritas_db')


# Configurações do upload
UPLOAD_FOLDER = 'static/images/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Gerir coneções com a base
def get_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DATABASE']
            )
            app.logger.info("Nova conexão com a base de dados estabelecida")
        except mysql.connector.Error as err:
            app.logger.error(f"Falha na conexão com a base: {err}")
            raise
    return g.db


# encerra a conexão com uso do decorador
@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
            app.logger.info("Conexão com a base de dados fechada")
        except mysql.connector.Error as err:
            app.logger.error(f"Erro ao fechar conexão: {err}")


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/conta',  methods=['GET', 'POST'])
def conta():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Preencha todos os campos!', 'primary')
            return render_template('conta.html')

        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            cursor.close()

            if user:
                # Salvar informações do usuário na sessão
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Login bem-sucedido!', 'success')
                return redirect(url_for('conta'))
            else:
                flash('Credenciais inválidas!', 'warning')

        except mysql.connector.Error as err:
            app.logger.error(f"Erro na verificação de login: {err}")
            flash('Erro ao acessar a base de dados.', 'danger')
        
    # Se já estiver logado, buscar dados
    user_data = None
    if session.get('user_id'):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user_data = cursor.fetchone()
        cursor.close()

    return render_template('conta.html', user_data=user_data or {})


@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu com sucesso!', 'info')
    return redirect(url_for('home'))


@app.route('/registar', methods=['POST'])
def registar():
    username = request.form.get('new_username')
    password = request.form.get('new_password')

    if not username or not password:
        flash('Preencha todos os campos para registo!')
        return redirect(url_for('conta'))

    db = get_db()
    cursor = db.cursor()

    # Verifica se já existe
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        flash('Este username já está registado!', 'warning')
        return redirect(url_for('conta'))

    # Insere novo utilizador
    cursor.execute(
        "INSERT INTO users (username, password, created_at) VALUES (%s, %s, NOW())",
        (username, password)
    )
    db.commit()

    # Login automático após registo
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    session['user_id'] = user[0]
    session['username'] = user[1]
    cursor.close()

    flash('Registo feito com sucesso!', 'success')
    return redirect(url_for('conta'))



@app.route('/alterar_username', methods=['POST'])
def alterar_username():
    novo_username = request.form.get('novo_username')
    if not session.get('user_id') or not novo_username:
        return redirect(url_for('conta'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET username = %s WHERE id = %s", (novo_username, session['user_id']))
    db.commit()
    session['username'] = novo_username
    flash('Username alterado com sucesso!', 'success')
    return redirect(url_for('conta'))

@app.route('/alterar_password', methods=['POST'])
def alterar_password():
    nova_password = request.form.get('nova_password')
    if not session.get('user_id') or not nova_password:
        return redirect(url_for('conta'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (nova_password, session['user_id']))
    db.commit()
    flash('Password alterada com sucesso!', 'success')
    return redirect(url_for('conta'))

@app.route('/eliminar_conta', methods=['POST'])
def eliminar_conta():
    if not session.get('user_id'):
        return redirect(url_for('conta'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (session['user_id'],))
    db.commit()
    session.clear()
    flash('Conta eliminada com sucesso!', 'info')
    return redirect(url_for('conta'))



@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/factosg")
def factosg():
    return render_template("factosg.html")


@app.route("/factosen")
def factosen():
    return render_template("factosen.html")


if __name__ == "__main__":
    # Cria a pasta de uploads se não existir
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)