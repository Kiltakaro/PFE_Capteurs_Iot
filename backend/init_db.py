# from main import app
# from models import db
# # from main import app, db

# from models import User

# with app.app_context():
#     db.create_all()

#     # Vérifier si la base de données est vide
#     if User.query.count() == 0:
#         # Ajouter des utilisateurs pré-établis
#         admin_user = User(username='admin1', is_admin=True)
#         admin_user.set_password('admin1')
#         db.session.add(admin_user)

#         regular_user = User(username='user1', is_admin=False)
#         regular_user.set_password('user1')
#         db.session.add(regular_user)

#         db.session.commit()
#         print("Base de données initialisée avec des utilisateurs par défaut.")
#     else:
#         print("La base de données contient déjà des utilisateurs.")