from app import app, db, bcrypt
from models import Admin

with app.app_context():
    if not Admin.query.filter_by(email='admin@foodback.com').first():
        hashed = bcrypt.generate_password_hash('admin1234').decode('utf-8')
        adm = Admin(email='admin@foodback.com', senha=hashed, nome='Super Admin')
        db.session.add(adm); db.session.commit()
        print('Admin criado')
    else:
        print('Admin já existe')
