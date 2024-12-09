from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    window_id = db.Column(db.Integer, db.ForeignKey('window.id'), nullable=False)
    threshold_value = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(20), nullable=False)  # e.g., '<', '>', '<=', '>='
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    window = db.relationship('Window', backref='alerts')

    
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
    if existing_username:
        return jsonify({'message': 'Username is taken.'}), 409 # Conflict
    if existing_email:
        return jsonify({'message': 'Email is already associated with a user.'})
    
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
        access_token = create_access_token(identity=user.id)
        return jsonify({
                        'message': 'Login success.',
                        'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401 # Unauthorized






@app.route('/pair_camera', methods=['POST'])
@jwt_required()
def pair_camera():
    data = request.get_json()
    
    # Extract camera token and name from the request JSON
    camera_token = data.get('camera_token')
    name = data.get('name')
    
    if not camera_token:
        return jsonify({'message': 'Camera token is required'}), 400
    if not name:
        return jsonify({'message': 'Camera name is required'}), 400

    # Get the user identity from JWT token
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Unauthorized access'}), 401
    
    # Find the camera by token

    camera = Camera.query.filter_by(token=camera_token).first()
    if not camera:
        return jsonify({'message': 'Camera not found'}), 404
    if camera.user_id:
        return jsonify({'message': 'Camera is already paired'}), 409  # Conflict if already paired

    # Pair camera with the user and set the name
    camera.user_id = user.id
    camera.name = name
    try:
        db.session.commit()
        return jsonify({'message': 'Camera paired successfully', 'camera': {'id': camera.id, 'name': camera.name}}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to pair camera', 'error': str(e)}), 500

    
@app.route('/cameras', methods=['GET'])
@jwt_required()
def get_cameras():
    # Get the username (or user identifier) from the JWT token
    user = User.query.get(get_jwt_identity())
    
    # Validate if the user exists
    if not user:
        return jsonify({'message': 'Unauthorized access'}), 401

    # Retrieve all cameras associated with the user
    cameras = Camera.query.filter_by(user_id=user.id).all()
    
    # Format the camera data
    cameras_data = []
    for camera in cameras:
        camera_info = {
            'id': camera.id,
            'name': camera.name,
        }
        cameras_data.append(camera_info)

    return jsonify({'cameras': cameras_data}), 200





@app.route('/add_window', methods=['POST'])
@jwt_required()
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

@app.route('/cameras/<int:camera_id>/windows', methods=['GET'])
@jwt_required()
def get_windows(camera_id):
    # Get the user from the JWT token
    existing_user = User.query.get(get_jwt_identity())
    
    # Validate if the user exists
    if not existing_user:
        return jsonify({'message': 'Unauthorized access'}), 401

    # Check if the camera exists and belongs to the user
    camera = Camera.query.filter_by(id=camera_id, user_id=existing_user.id).first()
    if not camera:
        return jsonify({'message': 'Camera not found or not owned by user'}), 404

    # Retrieve all windows associated with the specified camera
    windows = Window.query.filter_by(camera_id=camera_id).all()
    
    # Format the window data
    windows_data = []
    for window in windows:
        window_info = {
            'id': window.id,
            'name': window.name,
            'top_left_x': window.top_left_x,
            'top_left_y': window.top_left_y,
            'bottom_right_x': window.bottom_right_x,
            'bottom_right_y': window.bottom_right_y,
        }
        windows_data.append(window_info)

    return jsonify({'windows': windows_data}), 200



# Endpoint to create an alert for a window
@app.route('/windows/<int:window_id>/alerts', methods=['POST'])
@jwt_required()
def create_alert(window_id):
    # Get the user from JWT token
    existing_user = User.query.get(get_jwt_identity())
    if not existing_user:
        return jsonify({'message': 'Unauthorized access'}), 401

    # Check if the window exists and belongs to the user
    window = Window.query.get(window_id)
    if not window or window.camera.user_id != existing_user.id:
        return jsonify({'message': 'Window not found or not owned by user'}), 404

    data = request.get_json()
    threshold_value = data.get('threshold_value')
    condition = data.get('condition')

    # Validate the input data
    if threshold_value is None or condition not in ['<', '>', '<=', '>=']:
        return jsonify({'message': 'Invalid data'}), 400

    # Create a new alert
    new_alert = Alert(window_id=window_id,
                      threshold_value=threshold_value,
                      condition=condition)
    try:
        db.session.add(new_alert)
        db.session.commit()
        return jsonify({'message': 'Alert created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create alert', 'error': str(e)}), 500


# Endpoint to retrieve alerts for a specific window
@app.route('/windows/<int:window_id>/alerts', methods=['GET'])
@jwt_required()
def get_alerts(window_id):
    # Get the user from the JWT token
    existing_user = User.query.get(get_jwt_identity())
    if not existing_user:
        return jsonify({'message': 'Unauthorized access'}), 401

    # Check if the window exists and belongs to the user
    window = Window.query.get(window_id)
    if not window or window.camera.user_id != existing_user.id:
        return jsonify({'message': 'Window not found or not owned by user'}), 404

    # Retrieve all alerts associated with the specified window
    alerts = Alert.query.filter_by(window_id=window_id).all()
    print(len(alerts))

    # Format the alert data
    alerts_data = []
    for alert in alerts:
        alert_info = {
            'id': alert.id,
            'threshold_value': alert.threshold_value,
            'condition': alert.condition,
            'created_at': alert.created_at.isoformat()
        }
        alerts_data.append(alert_info)

    return jsonify({'alerts': alerts_data}), 200


@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Yay'}), 200

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print('Server oops', e)

    app.run(host="0.0.0.0", port=5000, debug=True) 





# # Soft AP Endpoint - Receives Wi-Fi and Starts Pairing
# # This will be on the actual camera
# @app.route('/camera/setup', methods=['POST'])
# def camera_setup():
#     data = request.get_json()
    
#     if 'ssid' not in data or 'password' not in data or 'pairing_code' not in data:
#         return jsonify({'message': 'Missing required setup data'}), 400

#     # Wi-Fi credentials to be saved on camera for connecting
#     ssid = data['ssid']
#     password = data['password']
#     pairing_code = data['pairing_code']
    
#     # The camera saves Wi-Fi credentials and attempts to connect (simulation)
#     return jsonify({'message': 'Wi-Fi credentials received. Connecting...'}), 200