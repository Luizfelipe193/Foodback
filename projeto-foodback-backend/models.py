from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ---------------------------
# 🧍 Tabela principal: USUÁRIOS
# ---------------------------
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # pessoa / empresa
    papel = db.Column(db.String(20), nullable=False, default="doador")  # doador / receptor / voluntario / admin
    cpf_cnpj = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(50))
    endereco = db.Column(db.String(255))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(50))
    cep = db.Column(db.String(20))
    foto = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    # Relacionamentos
    empresa = db.relationship("Empresa", backref="usuario", uselist=False)
    pessoa = db.relationship("Pessoa", backref="usuario", uselist=False)

    def __repr__(self):
        return f"<Usuario {self.nome} - {self.tipo}>"


# ---------------------------
# 🏢 Tabela EMPRESAS (apenas para tipo = empresa)
# ---------------------------
class Empresa(db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    nome_fantasia = db.Column(db.String(255))
    tipo_estabelecimento = db.Column(db.String(100))
    horario_funcionamento = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    qtd_media_doacoes = db.Column(db.String(50))
    responsavel_contato = db.Column(db.String(255))

    def __repr__(self):
        return f"<Empresa {self.nome_fantasia}>"


# ---------------------------
# 👤 Tabela PESSOAS (apenas para tipo = pessoa)
# ---------------------------
class Pessoa(db.Model):
    __tablename__ = "pessoas"

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    idade = db.Column(db.Integer)
    motivo_cadastro = db.Column(db.Text)
    disponibilidade = db.Column(db.String(100))
    preferencia_contato = db.Column(db.String(100))

    def __repr__(self):
        return f"<Pessoa {self.usuario.nome}>"
