from flask import Flask, render_template, session
from user.routes import user_bp
from admin.routes import admin_bp
from datetime import datetime
import config
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env and loads vars into environment

# Now os.getenv() in utils.py will work


app = Flask(__name__)
app.secret_key = 'a8f#9B@3_lF2zX*kp$90@'  # Needed for sessions
app.config.from_object(config)

# Register Blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Home route
@app.route('/')
def home():
    user_name = session.get('user_name')  # None if not logged in
    return render_template('home.html', user_name=user_name)

# Inject current year into all templates
@app.context_processor
def inject_year():
    return dict(current_year=datetime.now().year)

if __name__ == '__main__':
    app.run(debug=True)
