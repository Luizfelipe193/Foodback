import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from urllib.parse import quote_plus

# -------------------------------
# 🌎 Carregar variáveis de ambiente
# -------------------------------
load_dotenv()

app = Flask(__name__)
CORS(app)

# -------------------------------
# 🔧 CONFIGURAÇÃO DO BANCO
# -------------------------------
senha_segura = quote_plus(os.getenv("DB_PASSWORD"))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{senha_segura}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# -------------------------------
# 📧 CONFIGURAÇÃO DE E-MAIL
# -------------------------------
app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "True").lower() == "true",
    MAIL_USE_SSL=False,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_USERNAME")
)

mail = Mail(app)
serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY", "chave_segura_flask"))

# -------------------------------
# 👤 MODEL USUÁRIO
# -------------------------------
class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(255))
    cpf = db.Column(db.String(14))
    cnpj = db.Column(db.String(18))
    tipo = db.Column(db.String(20), default="pessoa", nullable=False)  # "pessoa" ou "empresa"

# -------------------------------
# ✅ TESTE DE API
# -------------------------------
@app.route("/api", methods=["GET"])
def api_status():
    return jsonify({"message": "✅ API FoodBack está rodando corretamente!"}), 200

# -------------------------------
# 📝 CADASTRAR NOVO USUÁRIO
# -------------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    nome = data.get("nome")
    email = data.get("email")
    senha = data.get("senha")
    telefone = data.get("telefone")
    endereco = data.get("endereco")
    cpf = data.get("cpf")
    cnpj = data.get("cnpj")
    tipo = data.get("tipo", "pessoa")

    # Validações básicas
    if not nome or not email or not senha:
        return jsonify({"error": "Preencha todos os campos obrigatórios (nome, email, senha)."}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "E-mail já cadastrado."}), 400

    if tipo not in ["pessoa", "empresa", "admin"]:
        return jsonify({"error": "Tipo de usuário inválido."}), 400

    try:
        senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha_hash,
            telefone=telefone,
            endereco=endereco,
            cpf=cpf,
            cnpj=cnpj,
            tipo=tipo
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({"message": "Usuário cadastrado com sucesso!"}), 201

    except Exception as e:
        print("Erro ao cadastrar usuário:", e)
        return jsonify({"error": "Erro interno ao cadastrar o usuário."}), 500

# -------------------------------
# 🔐 LOGIN DE USUÁRIO
# -------------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    senha = data.get("senha")

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not bcrypt.check_password_hash(usuario.senha, senha):
        return jsonify({"error": "E-mail ou senha inválidos."}), 401

    usuario_data = {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "tipo": usuario.tipo
    }

    return jsonify({"message": "Login bem-sucedido!", "usuario": usuario_data}), 200

# -------------------------------
# 🔑 ESQUECEU A SENHA
# -------------------------------
@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"error": "E-mail não encontrado."}), 404

    token = serializer.dumps(email, salt="reset-password")
    reset_link = f"http://localhost:3000/reset-password?token={token}"


    try:
        msg = Message("🔒 Redefinição de Senha - FoodBack", recipients=[email])
        msg.body = (
            f"Olá {usuario.nome},\n\n"
            f"Clique no link abaixo para redefinir sua senha:\n{reset_link}\n\n"
            "Se você não solicitou isso, ignore este e-mail."
        )
        mail.send(msg)
        return jsonify({"message": "E-mail de redefinição enviado com sucesso!"}), 200
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        return jsonify({"error": "Erro ao enviar o e-mail."}), 500

# -------------------------------
# 🔒 REDEFINIR SENHA (NOVA VERSÃO)
# -------------------------------
@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    token = data.get("token")
    nova_senha = data.get("nova_senha")

    if not token:
        return jsonify({"error": "Token não fornecido."}), 400
    if not nova_senha:
        return jsonify({"error": "Nova senha não fornecida."}), 400

    try:
        email = serializer.loads(token, salt="reset-password", max_age=3600)
    except Exception:
        return jsonify({"error": "Token inválido ou expirado."}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"error": "Usuário não encontrado."}), 404

    usuario.senha = bcrypt.generate_password_hash(nova_senha).decode("utf-8")
    db.session.commit()

    return jsonify({"message": "Senha redefinida com sucesso!"}), 200

# -------------------------------
# 🚀 MAIN
# -------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
