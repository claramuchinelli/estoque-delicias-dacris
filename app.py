from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estoque.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo do banco
class Sorvete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)

# Criar banco ao iniciar
with app.app_context():
    db.create_all()

# Página principal
@app.route('/')
def estoque():
    sabores = Sorvete.query.order_by(Sorvete.nome.asc()).all()
    return render_template('estoque.html', sabores=sabores)

# Adicionar sabor
@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form['nome']
    quantidade = request.form['quantidade']

    novo = Sorvete(nome=nome, quantidade=int(quantidade))
    db.session.add(novo)
    db.session.commit()

    return redirect(url_for('estoque'))

# Remover sabor
@app.route('/remover/<int:id>')
def remover(id):
    sorvete = Sorvete.query.get(id)
    db.session.delete(sorvete)
    db.session.commit()
    return redirect(url_for('estoque'))

if __name__ == '__main__':
    app.run(debug=True)
