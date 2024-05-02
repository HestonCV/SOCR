import requests

# Base URL of your Flask application
BASE_URL = "http://127.0.0.1:5000"

def register_user(username, email, password):
    url = f"{BASE_URL}/register"
    data = {"username": username, "email": email, "password": password}
    response = requests.post(url, json=data)
    return response.json()

def login_user(username, password):
    url = f"{BASE_URL}/login"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    return response.json()

def pair_camera(token, access_token):
    url = f"{BASE_URL}/pair_camera"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"camera_token": token}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def add_window(name, top_left_x, top_left_y, bottom_right_x, bottom_right_y, camera_id, access_token):
    url = f"{BASE_URL}/add_window"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "name": name,
        "top_left_x": top_left_x,
        "top_left_y": top_left_y,
        "bottom_right_x": bottom_right_x,
        "bottom_right_y": bottom_right_y,
        "camera_id": camera_id
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Replace these values with your desired test data
username = "heston"
email = "heston@example.com"
password = "password123"
camera_token = "234"
window_name = "Front Door"
top_left_x, top_left_y = 0, 0
bottom_right_x, bottom_right_y = 100, 100
camera_id = 1  # Assuming the camera with token '123' has an ID of 1

# Register user
print("Registering user...")
register_response = register_user(username, email, password)
print(register_response)

# Login user
print("\nLogging in...")
login_response = login_user(username, password)
access_token = login_response.get("access_token")
print(f"Access Token: {access_token}")

if access_token:
    # Pair camera
    print("\nPairing camera...")
    pair_response = pair_camera(camera_token, access_token)
    print(pair_response)
    
    # Add window
    print("\nAdding window...")
    window_response = add_window(window_name, top_left_x, top_left_y, bottom_right_x, bottom_right_y, camera_id, access_token)
    print(window_response)
