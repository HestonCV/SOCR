from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'Key' # Placeholder for now

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    cameras = db.relationship('Camera', backref='user')

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(50), nullable=True)
    windows = db.relationship('Window', backref='camera')

class Window(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    top_left_x = db.Column(db.Integer, nullable=False)
    top_left_y = db.Column(db.Integer, nullable=False)
    bottom_right_x = db.Column(db.Integer, nullable=False)
    bottom_right_y = db.Column(db.Integer, nullable=False)

# End Points
    
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing data'}), 400 # Bad Request
    
    username = data['username']
    email = data['email']
    password = data['password']

    existing_username = User.query.filter_by(username=username).first()
    existing_email = User.query.filter_by(email=email).first()
    if existing_username or existing_email:
        return jsonify({'message': 'User already exists'}), 409 # Conflict
    
    # Create new user
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, email=email, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User created sucessfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create user', 'error': str(e)}), 500 # Internal Server Error
    
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing data'}), 400 # Bad Request
    
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401 # Unauthorized

@app.route('/pair_camera', methods=['POST'])
@jwt_required()
def pair_camera():
    existing_user = User.query.get(get_jwt_identity())
    data = request.get_json()

    # Check if user exists
    if not existing_user:
        return jsonify({'message': 'Unauthorized access'}), 401

    camera_token = data.get('camera_token')

    # Check for provided camera token
    if not camera_token:
        return jsonify({'message': 'Missing camera token'}), 400
    
    camera = Camera.query.filter_by(token=camera_token).first()

    if not camera or camera.user:
        return jsonify({'message': 'Invalid or already used pairing token'}), 400
    
    camera.user_id = existing_user.id

    try:
        db.session.commit()

        return jsonify({'message': 'Camera paired successfully'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to pair camera', 'error': str(e)}), 500 # Internal Server Error
    
@app.route('/add_window', methods=['POST'])
@jwt_required
def add_window():
    existing_user = User.query.get(get_jwt_identity())
    data = request.get_json()

    # Check if user exists
    if not existing_user:
        return jsonify({'message': 'Unauthorized access'}), 401
    
    name = data.get('name')
    top_left_x = data.get('top_left_x')
    top_left_y = data.get('top_left_y')
    bottom_right_x = data.get('bottom_right_x')
    bottom_right_y = data.get('bottom_right_y')
    camera_id = data.get('camera_id')

    if not (name and top_left_x is not None and top_left_y is not None and 
            bottom_right_x is not None and bottom_right_y is not None and camera_id):
        return jsonify({'message': 'Invalid data'}), 400
    
    camera = Camera.query.get(camera_id)

    if not camera or camera.user_id != existing_user.id:
        return jsonify({'message': 'Camera not found or not owned by user'}), 400
    
    new_window = Window(camera_id=camera_id,
                        name=name,
                        top_left_x=top_left_x,
                        top_left_y=top_left_y,
                        bottom_right_x=bottom_right_x,
                        bottom_right_y=bottom_right_y)
    try:
        db.session.add(new_window)
        db.session.commit()

        return jsonify({'message': 'Window created successfully'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create window', 'error': str(e)}), 500 # Internal Server Error


import base64
import io
from PIL import Image

@app.route('handle_image', methods=['POST'])
@jwt_required
def handle_image():
    existing_camera = Camera.query.get(get_jwt_identity())

    if not existing_camera:
        return jsonify({'message': 'Unauthorized access'}), 401
    
    data = request.get_json()

    if 'image' not in data:
        return jsonify({'message': 'Missing image data'}), 400

    image_base64 = data['image']

    try:
        # Decode the base64-encoded image
        image_data = base64.b64decode(image_base64.split(',')[1])

        # Convert the decoded image data to a PIL image object
        image = Image.open(io.BytesIO(image_data))

        # Use classification model
        
        windows = existing_camera.windows

        # check window settings and classifications

        # notify user

        return jsonify({'message': 'Image received and processed'}), 200

    except Exception as e:
        return jsonify({'message': 'Failed to process image', 'error': str(e)}), 500


    

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print('Server oops', e)
    app.run(debug=True)

