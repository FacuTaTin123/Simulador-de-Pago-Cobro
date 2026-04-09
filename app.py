from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/contacto")
def contacto():
    return render_template("contacto.html")

@app.route("/curiosidades")
def curiosidades():
    return render_template("curiosidades.html")

@app.route("/info")
def informacion_flask():
    return render_template("informacion_flask.html")

if __name__ == "__main__":
    app.run(debug=True)