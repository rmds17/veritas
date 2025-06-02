from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Configuração da base de dados
db_config = {
    'host': 'db',
    'user': 'veritas_user',
    'password': '1234',
    'database': 'veritas_db'
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/conta")
def conta():
    return render_template("conta.html")

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
    app.run(debug=True, host="0.0.0.0")

# Configuração da base de dados