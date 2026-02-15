import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "deliciasdacris"

# ==============================
# CONFIGURAÇÃO DO BANCO (RENDER)
# ==============================
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///estoque.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==============================
# MODELOS
# ==============================
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telefone = db.Column(db.String(20), unique=True, nullable=False)
    senha = db.Column(db.String(100))

class Estoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sabor = db.Column(db.String(100), unique=True, nullable=False)
    quantidade = db.Column(db.Integer, default=0)

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sabor = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data = db.Column(db.DateTime, default=db.func.current_timestamp())

# ==============================
# SABORES INICIAIS
# ==============================
sabores_iniciais = [
    "Abacate",
    "Amendoim",
    "Chocolate",
    "Coco Cremoso",
    "Doce de Leite",
    "Leite Moça",
    "Limão Siciliano",
    "Manga",
    "Milho verde",
    "Morango com Nutella",
    "Ninho com Maracujá",
    "Ninho com Morango",
    "Ninho com Nutella",
    "Oreo",
    "Ovomaltine",
    "Ouro Branco",
    "Paçoca",
    "Prestígio",
    "Pudim",
    "Sonho de Valsa",
    "Tablito",
    "Trufado de Maracujá"
]

# ==============================
# CRIAR TABELAS + SABORES
# ==============================
with app.app_context():
    db.create_all()

    for sabor in sabores_iniciais:
        existe = Estoque.query.filter_by(sabor=sabor).first()
        if not existe:
            db.session.add(Estoque(sabor=sabor, quantidade=0))

    db.session.commit()

# ==============================
# LOGIN
# ==============================
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

# ==============================
# ESTOQUE
# ==============================
@app.route("/estoque", methods=["GET", "POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        sabor = request.form["sabor"]
        quantidade = int(request.form.get("quantidade", 0))
        tipo = request.form["tipo"]

        item = Estoque.query.filter_by(sabor=sabor).first()

        if not item:
            return "Item não encontrado"

        if tipo == "adicionar":
            item.quantidade += quantidade

        elif tipo == "venda":
            if item.quantidade >= quantidade:
                item.quantidade -= quantidade
                nova_venda = Venda(sabor=sabor, quantidade=quantidade)
                db.session.add(nova_venda)
            else:
                return "Estoque insuficiente"

        elif tipo == "zerar":
            item.quantidade = 0

        db.session.commit()
        return redirect("/estoque")

    itens = Estoque.query.order_by(Estoque.sabor.asc()).all()
    return render_template("estoque.html", itens=itens)

# ==============================
# RELATÓRIO ESTOQUE
# ==============================
@app.route("/relatorio/estoque")
def relatorio_estoque():
    if "user" not in session:
        return redirect("/")

    itens = Estoque.query.order_by(Estoque.sabor.asc()).all()
    return render_template("relatorio_estoque.html", itens=itens)

# ==============================
# RELATÓRIO VENDAS
# ==============================
@app.route("/relatorio/vendas")
def relatorio_vendas():
    if "user" not in session:
        return redirect("/")

    vendas = Venda.query.order_by(Venda.data.desc()).all()
    return render_template("relatorio_vendas.html", vendas=vendas)

# ==============================
# LOGOUT
# ==============================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ==============================
# RODAR LOCAL
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
