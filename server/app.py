from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    # Return only id, name, super_name — exclude hero_powers
    heroes_list = [hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes]
    return jsonify(heroes_list), 200


@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({'error': 'Hero not found'}), 404
    # Include hero_powers nested with power info
    hero_dict = hero.to_dict()
    # By default, hero_powers will include power nested due to serialization rules
    return jsonify(hero_dict), 200


@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    # Return only id, name, description — exclude hero_powers
    powers_list = [power.to_dict(only=('id', 'name', 'description')) for power in powers]
    return jsonify(powers_list), 200


@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({'error': 'Power not found'}), 404
    power_dict = power.to_dict(only=('id', 'name', 'description'))
    return jsonify(power_dict), 200


@app.route('/powers/<int:id>', methods=['PATCH'])
def patch_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({'error': 'Power not found'}), 404

    data = request.get_json()
    if 'description' not in data:
        return jsonify({'errors': ['validation errors']}), 400

    try:
        power.description = data['description']
        db.session.commit()
    except ValueError:
        db.session.rollback()
        return jsonify({'errors': ['validation errors']}), 400

    power_dict = power.to_dict(only=('id', 'name', 'description'))
    return jsonify(power_dict), 200


@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    required_fields = ['strength', 'power_id', 'hero_id']

    if not all(field in data for field in required_fields):
        return jsonify({'errors': ['validation errors']}), 400

    try:
        hero_power = HeroPower(
            strength=data['strength'],
            power_id=data['power_id'],
            hero_id=data['hero_id']
        )
        db.session.add(hero_power)
        db.session.commit()
    except ValueError:
        db.session.rollback()
        return jsonify({'errors': ['validation errors']}), 400

    # Return hero_power including nested hero and power info
    hero_power_dict = hero_power.to_dict()
    return jsonify(hero_power_dict), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)