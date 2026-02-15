from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# 🔹 Banco de dados (Render ou SQLite local)
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estoque.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🔹 Modelo do banco
class Sorvete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)

# 🔹 Sabores iniciais
sabores_iniciais = sorted([
    "Ninho com Nutella", "Morango com Nutella", "Ninho com Morango",
    "Ninho com Maracujá", "Leite Moça", "Trufado de Maracujá",
    "Chocolate", "Amendoim", "Paçoca", "Tablito", "Ovomaltine",
    "Oreo", "Doce de Leite", "Prestígio", "Pudim", "Milho Verde",
    "Ouro Branco", "Abacate", "Coco Cremoso", "Limão Siciliano",
    "Sonho de Valsa", "Manga"
])

# 🔹 Criar banco e inserir sabores automáticos
with app.app_context():
    db.create_all()

    for sabor in sabores_iniciais:
        existe = Sorvete.query.filter_by(nome=sabor).first()
        if not existe:
            novo = Sorvete(nome=sabor, quantidade=0)
            db.session.add(novo)

    db.session.commit()

# 🔹 Página principal
@app.route('/')
def estoque():
    sabores = Sorvete.query.order_by(Sorvete.nome.asc()).all()
    return render_template('estoque.html', sabores=sabores)

# 🔹 Adicionar quantidade a um sabor existente
@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form['nome']
    quantidade = int(request.form['quantidade'])

    sorvete = Sorvete.query.filter_by(nome=nome).first()

    if sorvete:
        sorvete.quantidade += quantidade
    else:
        novo = Sorvete(nome=nome, quantidade=quantidade)
        db.session.add(novo)

    db.session.commit()
    return redirect(url_for('estoque'))

# 🔹 Remover sabor
@app.route('/remover/<int:id>')
def remover(id):
    sorvete = Sorvete.query.get_or_404(id)
    db.session.delete(sorvete)
    db.session.commit()
    return redirect(url_for('estoque'))

if __name__ == '__main__':
    app.run(debug=True)
