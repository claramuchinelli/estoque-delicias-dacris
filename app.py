from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "deliciasdacris"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///estoque.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Modelos do banco
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telefone = db.Column(db.String(20), unique=True, nullable=False)
    senha = db.Column(db.String(100))

class Estoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sabor = db.Column(db.String(100), unique=True, nullable=False)
    quantidade = db.Column(db.Integer, default=0)

# Sabores iniciais
sabores_iniciais = [
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
]

# Criar banco e adicionar sabores iniciais
with app.app_context():
    db.create_all()
    for sabor in sabores_iniciais:
        if not Estoque.query.filter_by(sabor=sabor).first():
            db.session.add(Estoque(sabor=sabor, quantidade=0))
    db.session.commit()

# Rota de login
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

# Rota de estoque
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

    # Itens ordenados alfabeticamente
    itens = Estoque.query.order_by(Estoque.sabor.asc()).all()
    return render_template("estoque.html", itens=itens)

# Rodar app
if __name__ == "__main__":
    app.run()
    
