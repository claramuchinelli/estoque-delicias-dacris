from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "deliciasdacris"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///estoque.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telefone = db.Column(db.String(20), unique=True, nullable=False)
    senha = db.Column(db.String(100))

class Estoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sabor = db.Column(db.String(100), unique=True, nullable=False)
    quantidade = db.Column(db.Integer, default=0)

sabores_iniciais = [
    "Ninho com Nutella": 0,

    "Morango com Nutella": 0,

    "Ninho com Morango": 0,

    "Ninho com Maracujá": 0,

    "Leite Moça": 0,

    "Trufado de Maracujá": 0,

    "Chocolate": 0,

    "Amendoim": 0,

    "Paçoca": 0,

    "Tablito": 0,

    "Ovomaltine": 0,

    "Oreo": 0,

    "Doce de Leite": 0,

    "Prestígio": 0,

    "Pudim": 0,

    "Milho verde": 0,

    "Ouro Branco": 0,

    "Abacate": 0,

    "Coco Cremoso": 0,

    "Limão Siciliano": 0,

    "Sonho de Valsa": 0,

    "Manga": 0,
]

@app.before_first_request
def criar_tabelas():
    db.create_all()
    for sabor in sabores_iniciais:
        if not Estoque.query.filter_by(sabor=sabor).first():
            db.session.add(Estoque(sabor=sabor, quantidade=0))
    db.session.commit()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        telefone = request.form["telefone"]
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(telefone=telefone).first()

        if usuario:
            if usuario.senha == senha:
                session["user"] = telefone
                return redirect("/estoque")
            else:
                return "Senha incorreta"
        else:
            novo = Usuario(telefone=telefone, senha=senha)
            db.session.add(novo)
            db.session.commit()
            session["user"] = telefone
            return redirect("/estoque")

    return render_template("login.html")

@app.route("/estoque", methods=["GET", "POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        sabor = request.form["sabor"]
        quantidade = int(request.form["quantidade"])
        tipo = request.form["tipo"]

        item = Estoque.query.filter_by(sabor=sabor).first()

        if tipo == "adicionar":
            item.quantidade += quantidade
        else:
            item.quantidade -= quantidade

        db.session.commit()

    itens = Estoque.query.all()
    return render_template("estoque.html", itens=itens)

if __name__ == "__main__":
    app.run()
