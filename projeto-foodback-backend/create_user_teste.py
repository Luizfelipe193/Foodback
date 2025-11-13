from app import db, bcrypt, Usuario, app

with app.app_context():
    senha_hash = bcrypt.generate_password_hash("123456").decode("utf-8")
    novo = Usuario(nome="Samuel", email="samuel@teste.com", senha=senha_hash, tipo="admin")
    db.session.add(novo)
    db.session.commit()
    print("✅ Usuário 'Samuel' criado com sucesso!")
