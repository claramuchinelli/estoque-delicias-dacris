from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "deliciasdacris"

# 🔹 Configurar PostgreSQL do Render
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://estoque_delicias_user:OpL3sEkxXBexhEYPqN8qbH5fu0sDPRl3@dpg-d68qd7l6ubrc73a7a9rg-a/estoque_delicias"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# 🔹 Tabelas do banco
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

# 🔹 Sabores iniciais
sabores_iniciais = [
    "Abacate", "Amendoim", "Chocolate", "Coco Cremoso", "Doce de Leite", "Leite Moça",
    "Limão Siciliano", "Manga", "Milho verde", "Morango com Nutella", "Ninho com Maracujá",
    "Ninho com Morango", "Ninho com Nutella", "Oreo", "Ovomaltine", "Ouro Branco",
    "Paçoca", "Prestígio", "Pudim", "Sonho de Valsa", "Tablito", "Trufado de Maracujá"
]

# 🔹 Criar tabelas e inserir sabores iniciais se estiver vazio
with app.app_context():
    db.create_all()
    if Estoque.query.count() == 0:
        for sabor in sabores_iniciais:
            db.session.add(Estoque(sabor=sabor, quantidade=0))
        db.session.commit()

# 🔹 Rota de login / cadastro
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

# 🔹 Rota de logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# 🔹 Rota de estoque
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
        elif tipo == "remover":
            item.quantidade -= quantidade
            if item.quantidade < 0:
                item.quantidade = 0
        else:  # venda
            item.quantidade -= quantidade
            if item.quantidade < 0:
                item.quantidade = 0
            venda = Venda(sabor=sabor, quantidade=quantidade)
            db.session.add(venda)

        db.session.commit()

    itens = Estoque.query.order_by(Estoque.sabor).all()
    return render_template("estoque.html", itens=itens)

# 🔹 Rota para zerar quantidade de um produto
@app.route("/zerar_estoque", methods=["POST"])
def zerar_estoque():
    if "user" not in session:
        return redirect("/")

    sabor = request.form["sabor"]
    item = Estoque.query.filter_by(sabor=sabor).first()
    if item:
        item.quantidade = 0
        db.session.commit()
    return redirect("/estoque")

# 🔹 Rota para limpar todo o estoque
@app.route("/limpar_estoque")
def limpar_estoque():
    if "user" not in session:
        return redirect("/")

    for item in Estoque.query.all():
        item.quantidade = 0
    db.session.commit()
    return redirect("/estoque")

# 🔹 Relatório de estoque
@app.route("/relatorio/estoque")
def relatorio_estoque():
    if "user" not in session:
        return redirect("/")
    itens = Estoque.query.order_by(Estoque.sabor).all()
    return render_template("relatorio_estoque.html", itens=itens)

# 🔹 Relatório de vendas
@app.route("/relatorio/vendas")
def relatorio_vendas():
    if "user" not in session:
        return redirect("/")
    vendas = Venda.query.order_by(Venda.data.desc()).all()
    return render_template("relatorio_vendas.html", vendas=vendas)

# 🔹 Rodar o app
if __name__ == "__main__":
    app.run(debug=True)
