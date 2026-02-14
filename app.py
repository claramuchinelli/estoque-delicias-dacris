from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "deliciasdacris"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///estoque.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- MODELOS DO BANCO DE DADOS ---

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telefone = db.Column(db.String(20), unique=True, nullable=False)
    senha = db.Column(db.String(100))

class Estoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sabor = db.Column(db.String(100), unique=True, nullable=False)
    quantidade = db.Column(db.Integer, default=0)

# --- CONFIGURAÇÃO INICIAL (ORDEM ALFABÉTICA) ---

sabores_iniciais = [
    "Abacate", "Amendoim", "Chocolate", "Coco Cremoso", "Doce de Leite",
    "Leite Moça", "Limão Siciliano", "Manga", "Milho verde", "Morango com Nutella",
    "Ninho com Maracujá", "Ninho com Morango", "Ninho com Nutella", "Oreo",
    "Ouro Branco", "Ovomaltine", "Paçoca", "Prestígio", "Pudim", "Sonho de Valsa",
    "Tablito", "Trufado de Maracujá"
]

with app.app_context():
    db.create_all()
    # Usamos sorted() para garantir a ordem na primeira carga do banco
    for sabor in sorted(sabores_iniciais):
        if not Estoque.query.filter_by(sabor=sabor).first():
            db.session.add(Estoque(sabor=sabor, quantidade=0))
    db.session.commit()

# --- ROTAS ---

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
            # Cria novo usuário se não existir
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
        sabor_nome = request.form["sabor"]
        quantidade = int(request.form["quantidade"])
        tipo = request.form["tipo"]

        item = Estoque.query.filter_by(sabor=sabor_nome).first()

        if item:
            if tipo == "adicionar":
                item.quantidade += quantidade
            else:
                # Evita que o estoque fique negativo (opcional, mas recomendado)
                item.quantidade = max(0, item.quantidade - quantidade)
            
            db.session.commit()

    # BUSCA ORDENADA: Aqui garantimos a ordem alfabética na tela
    itens = Estoque.query.order_by(Estoque.sabor.asc()).all()
    return render_template("estoque.html", itens=itens)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
