import os
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "deliciasdacris"

# Configuração do banco: PostgreSQL no Render ou SQLite local
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///estoque.db"

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
    "Ninho com Nutella", "Morango com Nutella", "Ninho com Morango",
    "Ninho com Maracujá", "Leite Moça", "Trufado de Maracujá",
    "Chocolate", "Amendoim", "Paçoca", "Tablito", "Ovomaltine",
    "Oreo", "Doce de Leite", "Prestígio", "Pudim", "Milho verde",
    "Ouro Branco", "Abacate", "Coco Cremoso", "Limão Siciliano",
    "Sonho de Valsa", "Manga"
])

# Criar tabelas e
