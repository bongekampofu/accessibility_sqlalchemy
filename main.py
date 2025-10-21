
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prefs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    prefs = db.relationship('Preference', backref='user', uselist=False)


class Preference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    font_size = db.Column(db.String(10), default='16px')
    theme = db.Column(db.String(20), default='light')
    base_font = db.Column(db.String(100), default='Inter, Arial, sans-serif')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


def init_db():

    with app.app_context():
        db.create_all()


        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            demo = User(username='demo')
            demo_prefs = Preference(user=demo)
            db.session.add_all([demo, demo_prefs])
            db.session.commit()



@app.route('/')
def index():
    username = request.args.get('username', 'demo')
    user = User.query.filter_by(username=username).first()
    if not user:
        return "User not found", 404
    prefs = user.prefs
    return render_template('index.html', prefs=prefs, username=username)


@app.route('/save_prefs', methods=['POST'])
def save_prefs():
    """Save form-based accessibility preferences."""
    username = request.form.get('username', 'demo')
    font_size = request.form.get('font_size', '16px')
    theme = request.form.get('theme', 'light')
    base_font = request.form.get('base_font', 'Inter, Arial, sans-serif')

    user = User.query.filter_by(username=username).first()
    if not user:
        return "User not found", 404

    prefs = user.prefs
    prefs.font_size = font_size
    prefs.theme = theme
    prefs.base_font = base_font

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return "Failed to save preferences", 500

    return redirect(url_for('index', username=username))


@app.route('/api/save_prefs', methods=['POST'])
def api_save_prefs():
    """Save preferences via JSON API."""
    data = request.get_json() or {}
    username = data.get('username', 'demo')
    font_size = data.get('font_size', '16px')
    theme = data.get('theme', 'light')
    base_font = data.get('base_font', 'Inter, Arial, sans-serif')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'ok': False, 'error': 'User not found'}), 404

    prefs = user.prefs
    prefs.font_size = font_size
    prefs.theme = theme
    prefs.base_font = base_font
    db.session.commit()

    return jsonify({'ok': True})



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
