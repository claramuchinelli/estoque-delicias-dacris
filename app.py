from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "deliciasdacris"

# Banco SQLite local
import os

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Modelos
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

# Sabores iniciais
sabores_iniciais = sorted([
    "Ninho com Nutella",
    "Morango com Nutella",
    "Ninho com Morango",
    "Ninho com Maracujá",
    "Leite Moça",
    "Trufado de Maracujá",
    "Chocolate",
    "Amendoim",
    "Paçoca",
    "Tablito",
    "Ovomaltine",
    "Oreo",
    "Doce de Leite",
    "Prestígio",
    "Pudim",
    "Milho verde",
    "Ouro Branco",
    "Abacate",
    "Coco Cremoso",
    "Limão Siciliano",
    "Sonho de Valsa",
    "Manga"
])

# Criar banco e sabores iniciais automaticamente
with app.app_context():
    db.create_all()
    for sabor in sabores_iniciais:
        if not Estoque.query.filter_by(sabor=sabor).first():
            db.session.add(Estoque(sabor=sabor, quantidade=0))
    db.session.commit()

# Rotas
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
                flash("Senha incorreta!", "error")
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
        if item:
            if tipo == "adicionar":
                item.quantidade += quantidade
            elif tipo == "remover":
                item.quantidade = max(item.quantidade - quantidade, 0)
            elif tipo == "zerar":
                item.quantidade = 0
            db.session.commit()

    itens = Estoque.query.order_by(Estoque.sabor).all()
    return render_template("estoque.html", itens=itens)

@app.route("/relatorio_estoque")
def relatorio_estoque():
    if "user" not in session:
        return redirect("/")
    itens = Estoque.query.order_by(Estoque.sabor).all()
    return render_template("relatorio_estoque.html", itens=itens)

@app.route("/relatorio_vendas")
def relatorio_vendas():
    if "user" not in session:
        return redirect("/")
    vendas = Venda.query.order_by(Venda.data.desc()).all()
    return render_template("relatorio_vendas.html", vendas=vendas)

@app.route("/vender", methods=["POST"])
def vender():
    if "user" not in session:
        return redirect("/")

    sabor = request.form["sabor"]
    quantidade = int(request.form["quantidade"])
    item = Estoque.query.filter_by(sabor=sabor).first()

    if item and item.quantidade >= quantidade:
        item.quantidade -= quantidade
        venda = Venda(sabor=sabor, quantidade=quantidade)
        db.session.add(venda)
        db.session.commit()
        flash(f"{quantidade} {sabor} vendido(s)!", "success")
    else:
        flash("Quantidade insuficiente!", "error")

    return redirect("/estoque")

@app.route("/limpar_estoque", methods=["POST"])
def limpar_estoque():
    if "user" not in session:
        return redirect("/")

    # Zerar todas as quantidades
    Estoque.query.update({Estoque.quantidade: 0})
    db.session.commit()
    flash("Estoque zerado com sucesso!", "success")
    return redirect("/estoque")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
