from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, g, session, jsonify
import mysql.connector
import os # para receber as credenciais de acesso a base do container



app = Flask(__name__)
# app.secret_key = 'sua_chave_secreta'  # Necessário para flash messages
app.secret_key = '24e23c43d423c434343vfghfgd'

# Configurações do banco de dados a partir das variáveis de ambiente
app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'db')  # 'db' é o nome do serviço no compose
app.config['MYSQL_USER'] = os.getenv('DB_USER', 'veritas_user')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', '1234')
app.config['MYSQL_DATABASE'] = os.getenv('DB_NAME', 'veritas_db')

# Configuração da base de dados
db_config = {
    'host': 'db',
    'user': 'veritas_user',
    'password': '1234',
    'database': 'veritas_db'
}

@app.route("/")
def home():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Query Facto do Dia
    today = datetime.today()
    month = today.month
    day = today.day
    query = """
    SELECT * FROM fatos WHERE MONTH(data_fato) = %s AND DAY(data_fato) = %s LIMIT 1;
    """
    cursor.execute(query, (int(month), int(day)))
    facto_do_dia = cursor.fetchone()

    # Query Factos Aleatórios
    query_factos_random = """
        SELECT * FROM fatos
        ORDER BY RAND()
        LIMIT 2
    """
    cursor.execute(query_factos_random)
    factos_random = cursor.fetchall()
    if not factos_random:
        factos_random = []  # garante lista vazia, não None

    cursor.close()

    return render_template("index.html", facto_do_dia=facto_do_dia, factos_random=factos_random)




@app.route('/api/gerar_facto', methods=['POST'])
def api_gerar_facto():
    data = request.json
    data_input = data.get('dataInput')
    categoria = data.get('categoriaSelect')
    area = data.get('areaSelect')

    query = "SELECT * FROM fatos WHERE 1=1"
    params = []

    if data_input:
        try:
            year, month = map(int, data_input.split('/'))
            query += " AND YEAR(data_fato) = %s AND MONTH(data_fato) = %s"
            params.extend([year, month])
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use AAAA-MM."}), 400

    if categoria:
        categoria_map = {
            "historia": 1,
            "desporto": 2,
            "futebol": 3,
            "politica": 4,
            "musica": 5
        }
        cat_id = categoria_map.get(categoria.lower())
        if cat_id:
            query += " AND categoria_id = %s"
            params.append(cat_id)

    if area and area.lower() != 'mundo':
        if area.lower() == 'europa':
            query += " AND localizacao REGEXP 'Portugal|Espanha|França|Itália|Alemanha|Reino Unido|Holanda|Bélgica|Suíça|Suécia|Dinamarca|Noruega|Finlândia|Polónia|Grécia|Áustria|Irlanda'"
        elif area.lower() == 'america':
            query += " AND localizacao REGEXP 'Brasil|Estados Unidos|Canadá|México|Argentina|Chile|Colômbia|Peru|Uruguai'"

    query += " ORDER BY RAND() LIMIT 1"

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    facto_gerado = cursor.fetchone()
    cursor.close()

    if facto_gerado:
        return jsonify(facto_gerado)
    else:
        return jsonify({"message": "Nenhum facto encontrado."}), 404





# Gerir conexões com a base
def get_db():
    if 'db' not in g: # valida que nao existe conexão com o objeto especial g (namespace global durante o ciclo de vida de uma requisição)
        try:
        # criar a conexão
            g.db = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],  
                database=app.config['MYSQL_DATABASE']
            )
            app.logger.info("Nova conexão com a base de dados estabelecida")
        except mysql.connector.Error as err:
            app.logger.error(f"Falha na conexão com a base: {err}")
            return f"Erro: {e}"
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



@app.route('/conta',  methods=['GET', 'POST'])
def conta():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            # LOGIN
            if 'username' in request.form and 'password' in request.form:
                username = request.form['username']
                password = request.form['password']

                cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
                user = cursor.fetchone()

                if user:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    flash('Login feito com sucesso!')
                else:
                    flash('Credenciais inválidas.')

            # REGISTO
            elif 'new_username' in request.form and 'new_password' in request.form and 'new_email' in request.form:
                new_username = request.form['new_username']
                new_password = request.form['new_password']
                new_email = request.form['new_email']

                cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                               (new_username, new_password, new_email))
                conn.commit()
                flash('Conta criada com sucesso! Agora podes fazer login.')

        # Buscar info para mostrar
        user_info = None
        if session.get('user_id'):
            cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
            user_info = cursor.fetchone()

        conn.close()
        return render_template("conta.html", user_data=user_info)
    except Exception as e:
        return f"Erro: {e}"


@app.route('/logout', methods=['POST'])
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



@app.route("/factosen")
def factosen():
    return render_template("factosen.html")


@app.route("/factosg", methods=["GET", "POST"])
def factosg():
    if not session.get('user_id'):
        flash("Precisas de estar autenticado para ver os teus factos guardados.", "warning")
        return redirect(url_for("conta"))

    filtros = {
        "dataInput": request.form.get("dataInput", "").strip(),
        "categoria": request.form.get("categoriaSelect", "").strip(),
        "area": request.form.get("areaSelect", "").strip()
    }

    query = """
        SELECT f.*
        FROM factos_guardados fg
        JOIN fatos f ON fg.fato_id = f.id
        WHERE fg.user_id = %s
    """
    params = [session["user_id"]]

    if filtros["dataInput"]:
        try:
            data = datetime.strptime(filtros["dataInput"].replace('-', '/'), "%Y/%m")
            query += " AND YEAR(f.data_fato) = %s AND MONTH(f.data_fato) = %s"
            params.extend([data.year, data.month])
        except ValueError:
            flash("Formato de data inválido. Usa aaaa/mm.", "danger")

    if filtros["categoria"]:
        categoria_ids = {
            "historia": 1, "desporto": 2, "futebol": 3,
            "politica": 4, "musica": 5
        }
        cat_id = categoria_ids.get(filtros["categoria"].lower())
        if cat_id:
            query += " AND f.categoria_id = %s"
            params.append(cat_id)

    if filtros["area"]:
        if filtros["area"].lower() == "europa":
            query += " AND f.localizacao REGEXP 'Portugal|Espanha|França|Itália|Alemanha|Reino Unido|Holanda|Bélgica|Suíça|Suécia|Dinamarca|Noruega|Finlândia|Polónia|Grécia|Áustria|Irlanda'"
        elif filtros["area"].lower() == "america":
            query += " AND f.localizacao REGEXP 'Brasil|Estados Unidos|Canadá|México|Argentina|Chile|Colômbia|Peru|Uruguai'"

    query += " ORDER BY f.data_fato DESC"

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    factos = cursor.fetchall()
    cursor.close()

    return render_template("factosg.html", factos=factos, filtros=filtros)




@app.route("/guardar_facto", methods=["POST"])
def guardar_facto():
    if not session.get("user_id"):
        flash("Tens de estar autenticado para guardar factos.", "warning")
        return redirect(url_for("conta"))

    fato_id = request.form.get("fato_id")
    if not fato_id:
        flash("ID do facto não fornecido.", "danger")
        return redirect(url_for("home"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM factos_guardados WHERE user_id = %s AND fato_id = %s", (session["user_id"], fato_id))
    ja_existe = cursor.fetchone()

    if not ja_existe:
        cursor.execute("INSERT INTO factos_guardados (user_id, fato_id) VALUES (%s, %s)", (session["user_id"], fato_id))
        db.commit()
        flash("Facto guardado com sucesso!", "success")
    else:
        flash("Este facto já está guardado.", "info")

    return redirect(request.referrer or url_for("home"))



@app.route('/remover_facto_guardado', methods=['POST'])
def remover_facto_guardado():
    if not session.get('user_id'):
        flash('Precisas de estar autenticado para remover factos.', 'warning')
        return redirect(url_for('conta'))

    fato_id = request.form.get('fato_id')
    if not fato_id:
        flash('ID do facto não fornecido.', 'danger')
        return redirect(url_for('factosg'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        DELETE FROM factos_guardados
        WHERE user_id = %s AND fato_id = %s
    """, (session['user_id'], fato_id))
    db.commit()
    cursor.close()

    flash('Facto removido dos guardados com sucesso!', 'success')
    return redirect(url_for('factosg'))













if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
