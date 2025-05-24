from flask import Flask, render_template


app = Flask(__name__)


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
    return render_template("factosen.html")

if __name__ == "__main__":
    app.run(debug=True)

