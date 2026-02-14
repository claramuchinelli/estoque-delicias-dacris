from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "deliciasdacris"

# Configuração do banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///estoque.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- MODELOS ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telefone = db.Column(db.String(20), unique=True, nullable=False)
    senha = db.Column(db.String(100))

class Estoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sabor = db.Column(db.String(100), unique=True, nullable=False)
    quantidade = db.Column(db.Integer, default=0)

# --- FUNÇÃO PARA INICIALIZAR O BANCO (SÓ RODA UMA VEZ) ---
def inicializar_banco():
    sabores_iniciais = [
        "Abacate", "Amendoim", "Chocolate", "Coco Cremoso", "Doce de Leite",
        "Leite Moça", "Limão Siciliano", "Manga", "Milho verde", "Morango com Nutella",
        "Ninho com Maracujá", "Ninho com Morango", "Ninho com Nutella", "Oreo",
        "Ouro Branco", "Ovomaltine", "Paçoca", "Prestígio", "Pudim", "Sonho de Valsa",
        "Tablito", "Trufado de Maracujá"
    ]
    
    db.create_all()
    
    # Verifica se já existem sabores para não duplicar toda vez que iniciar
    if not Estoque.query.first():
        for sabor in sorted(sabores_iniciais):
            novo_sabor = Estoque(sabor=sabor, quantidade=0)
            db.session.add(novo_sabor)
        db.session.commit()
        print("Banco de dados inicializado com sucesso!")

# --- ROTAS ---

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        telefone = request.form.get("telefone")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(telefone=telefone).first()

        if usuario:
            if usuario.senha == senha:
                session["user"] = telefone
                return redirect("/estoque")
            else:
                return "Senha incorreta", 401
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
        sabor_nome = request.form.get("sabor")
        quantidade = int(request.form.get("quantidade", 0))
        tipo = request.form.get("tipo")

        item = Estoque.query.filter_by(sabor=sabor_nome).first()

        if item:
            if tipo == "adicionar":
                item.quantidade += quantidade
            elif tipo == "remover":
                item.quantidade = max(0, item.quantidade - quantidade)
            
            db.session.commit()
        return redirect("/estoque") # Redireciona para evitar reenvio de formulário ao atualizar

    # Ordena por nome (A-Z) diretamente na busca do banco
    itens = Estoque.query.order_by(Estoque.sabor.asc()).all()
    return render_template("estoque.html", itens=itens)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    with app.app_context():
        inicializar_banco()
    app.run(debug=True)
