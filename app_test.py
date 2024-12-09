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

def pair_camera(camera_token, name, access_token):
    url = f"{BASE_URL}/pair_camera"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "camera_token": camera_token,
        "name": name
    }
    response = requests.post(url, headers=headers, json=data)
    print("Pair Camera Status Code:", response.status_code)
    print("Pair Camera Response:", response.json())
    return response.json()

# Test values
username = "testuser"
password = "testpassword"
camera_token = "12345"  # Token of the preprovisioned camera
camera_name = "Front Door"  # Name for the camera

# Login user
login_response = login_user(username, password)
access_token = login_response.get("access_token")
print(f"Access Token: {access_token}")

# Pair camera if login succeeded
if access_token:
    pair_camera(camera_token, camera_name, access_token)
else:
    print("Failed to login. Check username or password.")


def get_cameras(access_token):
    url = f'{BASE_URL}/cameras'
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url=url, headers=headers)
    print(response.status_code)
    return response.json()

# Replace these values with your desired test data
username = "user"
email = "heston@email.com"
password = "password"
camera_token = "123"
window_name = "Front Door"
top_left_x, top_left_y = 0, 0
bottom_right_x, bottom_right_y = 100, 100
camera_id = 1  # Assuming the camera with token '123' has an ID of 1

# # Register user
# print("Registering user...")
# register_response = register_user(username, email, password)
# print(register_response)

# Login user
print("\nLogging in...")
login_response = login_user(username, password)
access_token = login_response.get("access_token")
print(f"Access Token: {access_token}")

if access_token:
    # Pair camera
    print("\nPairing camera...")
    pair_response = pair_camera(camera_token=camera_token, access_token=access_token, name='Camera1')
    print(pair_response)

    cameras_response = get_cameras(access_token=access_token)
    print(cameras_response['cameras'])
    print()

    
    # # Add window
    # print("\nAdding window...")
    # window_response = add_window(window_name, top_left_x, top_left_y, bottom_right_x, bottom_right_y, camera_id, access_token)
    # print(window_response)
