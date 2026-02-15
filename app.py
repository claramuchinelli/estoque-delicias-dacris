from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "deliciasdacris"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///estoque.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telefone = db.Column(db.String(20), unique=True)
    senha = db.Column(db.String(50))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sabor = db.Column(db.String(100))
    quantidade = db.Column(db.Integer)

with app.app_context():
    db.create_all()

    if Item.query.count() == 0:
        sabores = [
            "Abacate",
            "Amendoim",
            "Chocolate",
            "Coco Cremoso",
            "Doce de Leite",
            "Leite Moça",
            "Limão Siciliano",
            "Manga",
            "Milho Verde",
            "Morango com Nutella",
            "Ninho com Maracujá",
            "Ninho com Morango",
            "Ninho com Nutella",
            "Oreo",
            "Ouro Branco",
            "Ovomaltine",
            "Paçoca",
            "Prestígio",
            "Pudim",
            "Sonho de Valsa",
            "Tablito",
            "Trufado de Maracujá"
        ]

        sabores.sort()  # ORDEM ALFABÉTICA

        for s in sabores:
            db.session.add(Item(sabor=s, quantidade=0))
        db.session.commit()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        telefone = request.form["telefone"]
        senha = request.form["senha"]

        user = Usuario.query.filter_by(telefone=telefone).first()

        if user:
            if user.senha == senha:
                session["user"] = telefone
                return redirect("/estoque")
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

        item = Item.query.filter_by(sabor=sabor).first()

        if tipo == "adicionar":
            item.quantidade += quantidade
        else:
            item.quantidade -= quantidade
            if item.quantidade < 0:
                item.quantidade = 0

        db.session.commit()

    itens = Item.query.order_by(Item.sabor.asc()).all()
    return render_template("estoque.html", itens=itens)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
