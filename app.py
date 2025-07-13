from flask import Flask
from config import Config
from models import User, db
from flask_login import LoginManager
from auth import auth_bp
from routes import main_bp
from flask_migrate import Migrate
from flask_mail import Mail
import logging

app = Flask(__name__)
app.config.from_object(Config)
app.config['MAIL_DEBUG'] = True  # <-- Add this line
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

logging.basicConfig(level=logging.DEBUG)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)                                                                                                     

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
for rule in app.url_map.iter_rules():
    print(rule)
if __name__ == '__main__':
 app.run(debug=True)
# mail= mail()
# mail = Mail()

# # def create_app():
# #     app = Flask(__name__)
# #     app.config.from_object(Config)
    
# #     mail.init_app(app)  # THIS IS CRUCIAL
# #     ...
# #     return app