# from flask import Flask
# from flask import Flask, render_template
from flask import Flask, request, render_template, redirect, url_for, flash, g
import mysql.connector
import os # para receber as credenciais de acesso a base do container


app = Flask(__name__)


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
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT texto FROM factos ORDER BY criado_em DESC")
    factos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("factosen.html", factos=factos)

@app.route("/submeter_facto", methods=["POST"])
def submeter_facto():
    texto = request.form.get("texto")
    data = request.form.get("data")
    local = request.form.get("local")
    estilo = request.form.get("estilo")

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "INSERT INTO factos (texto, data, local, estilo) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (texto, data, local, estilo))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/factosen")


if __name__ == "__main__":
    app.run(debug=True)

