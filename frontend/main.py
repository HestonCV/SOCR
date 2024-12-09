import requests

class Menu:
    def __init__(self, server_url):
        self.server_url = server_url 
        self.nav_stack = ['initial_page']
        self.render_active_page()
        self.access_token = None
    
    def back(self, optional=None):
        # Remove page from top of stack and render the new active page
        self.nav_stack.pop()
        self.render_active_page(optional)
    
    def forward(self, page, optional=None):
        # Add page to top of stack and render the new active page
        self.nav_stack.append(page)
        self.render_active_page(optional)
    
    def render_page_header(self, header_message=''):
        
        if header_message:
            header_message = '- ' + header_message

        print(f'\nExtra Eyes {header_message}')
        print('|-------------------------')
        if len(self.nav_stack) > 0:
            if self.nav_stack[-1] == 'initial_page':
                print('|(X/x) -> Quit')
                return
            
            if self.nav_stack[-1] == 'main_menu':
                print('|(B/b) -> Logout')
                return
            
            if self.nav_stack[-1] == 'check_out':
                return
            
            if len(self.nav_stack) > 1:
                print('|(B/b) -> Back')
                return
        
    
    def render_active_page(self, optional=None):
        pages = {
            'initial_page': self.initial_page,
            'login': self.login_page,
            'register': self.register_page,
            'main_menu': self.main_menu_page,
            'create_window': self.create_window_page,
            'select_camera_add': self.select_camera_add_page,
            'select_camera_view': self.select_camera_view_page,
            'view_windows': self.view_windows_page,
            'select_camera_alert': self.select_camera_alert_page,
            'select_window_alert': self.select_window_alert_page,
            'create_alert': self.create_alert_page,
            'select_camera_view_alerts': self.select_camera_view_alerts_page,  # New page for selecting camera for viewing alerts
            'select_window_view_alerts': self.select_window_view_alerts_page,  # New page for selecting window for viewing alerts
            'view_alerts': self.view_alerts_page  # New page for viewing alerts
        }

        print('\n\n----------------------------------------\n')
        if len(self.nav_stack) > 0:
            active_page = self.nav_stack[-1]
            if optional:
                pages[active_page](optional)
            else:
                pages[active_page]()
        else:
            return

    
    def initial_page(self):
        
        # Process input from user
        def process_selection():

            while True:
                selection = input('|- Enter your selection: ')
                selection = selection.strip().lower()
                
                # If register page was selected
                if selection == '1':
                    self.forward('login')
                    return
                # if login page was selected
                elif selection == '2': 
                    self.forward('register')
                    return
                elif selection == 'x':
                    return
                else:
                    print('|----- Invalid Selection.')

        # Render Initial Page UI
        self.render_page_header(header_message="Welcome")
        print('|----- 1. Login')
        print('|----- 2. Register')
        process_selection()
        
    def login_page(self):
        def process_input():
            username = input("|- Enter your username: ")
            if username.lower() == 'b':
                self.back()
                return
            password = input("|- Enter your password: ")
            if password.lower() == 'b':
                self.back()
                return
            
            user_data = {
                'username': username,
                'password': password
            }
            
            response = requests.post(self.server_url + '/login', json=user_data)
            json_response = response.json()
            print(json_response['message'])
            if response.status_code == 200:
                self.access_token = json_response['access_token']
                self.forward('main_menu')
            else:
                process_input()

        self.render_page_header(header_message='Login')
        process_input()
    
    def register_page(self):
        def process_input():
            email = input("|- Enter your email: ")
            if email.lower() == 'b':
                self.back()
                return
            username = input("|- Enter a new username: ")
            if username.lower() == 'b':
                self.back()
                return
            password = input("|- Enter a new password: ")
            if password.lower() == 'b':
                self.back()
                return

            # Register user with server
            user_data = {
                'email': email,
                'username': username,
                'password': password
            }
            response = requests.post(self.server_url + '/register', json=user_data)
            json_response = response.json()
            print(json_response['message'])
            if response.status_code == 201:
                self.back()
            else:
                process_input()

        self.render_page_header(header_message='Register')
        process_input()

    def main_menu_page(self):
        def process_selection():
            while True:
                selection = input('|- Enter your selection: ')
                selection = selection.strip().lower()

                if selection == '1': 
                    self.forward('select_camera_add')
                    return
                elif selection == '2':
                    self.forward('select_camera_view')
                    return
                elif selection == '3':
                    self.forward('select_camera_alert')
                    return
                elif selection == '4':
                    self.forward('select_camera_view_alerts')
                    return
                elif selection == 'b':
                    self.nav_stack = ['initial_page']
                    self.render_active_page()
                    return
                else:
                    print('|----- Invalid Selection.')

        # Render Main Menu UI
        self.render_page_header(header_message="Main Menu")
        print('|----- 1. Create Window')
        print('|----- 2. View Windows')
        print('|----- 3. Add Alert')  
        print('|----- 4. View Alerts')  # New option for viewing alerts
        process_selection()
    
    def create_window_page(self, camera):
        def process_input():
            name = input("|- Enter the window name: ")
            if name.lower() == 'b':
                self.back()
                return
            top_left_x = input("|- Enter top left x coord: ")
            if top_left_x.lower() == 'b':
                self.back()
                return
            top_left_y = input("|- Enter top left y coord: ")
            if top_left_y.lower() == 'b':
                self.back()
                return
            bottom_right_x = input("|- Enter bottom right x coord: ")
            if bottom_right_x.lower() == 'b':
                self.back()
                return
            bottom_right_y = input("|- Enter bottom right y coord: ")
            if bottom_right_y.lower() == 'b':
                self.back()
                return

            data = {
                'name': name,
                'top_left_x': top_left_x,
                'top_left_y': top_left_y,
                'bottom_right_x': bottom_right_x,
                'bottom_right_y': bottom_right_y,
                'camera_id': camera['id']
            }

            headers = {'Authorization': f'Bearer {self.access_token}'}

            response = requests.post(url=self.server_url + '/add_window', json=data, headers=headers)
            if response:
                json_response = response.json()
                print(json_response['message'])

                if response.status_code == 201:
                    self.back()
                else:
                    process_input()
            else:
                print('Error reaching server')
                process_input()

        self.render_page_header(header_message=f'Create Window: {camera["name"]}')
        process_input()

    def select_camera_add_page(self):
        def process_input():
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(url=self.server_url + '/cameras', headers=headers)
            json_response = response.json()
        
            cameras = json_response['cameras']

            for index, camera in enumerate(cameras):
                print(f'|----- {index+1}. {camera["name"]}')

            while True:
                selection = input('|- Enter your selection: ')
                if selection == 'b':
                    self.back()
                    return
                
                selection = int(selection.strip().lower())
                if selection > 0 and selection <= len(cameras):
                    # TODO: use the camera information to handle the window page correctly
                    self.forward('create_window', cameras[selection-1])
                    break
                elif selection == 'b':
                    self.back()
                    return
                else:
                    print('|----- Invalid Selection.')

        self.render_page_header(header_message='Create Window: Select Camera')
        process_input()

    def select_camera_view_page(self):
        def process_input():
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(url=self.server_url + '/cameras', headers=headers)
            json_response = response.json()
        
            cameras = json_response['cameras']

            for index, camera in enumerate(cameras):
                print(f'|----- {index+1}. {camera["name"]}')

            while True:
                selection = input('|- Enter your selection: ')
                if selection == 'b':
                    self.back()
                    return
                
                selection = int(selection.strip().lower())
                if selection > 0 and selection <= len(cameras):
                    # TODO: use the camera information to handle the window page correctly
                    self.forward('view_windows', cameras[selection-1])
                    break
                elif selection == 'b':
                    self.back()
                    return
                else:
                    print('|----- Invalid Selection.')

        self.render_page_header(header_message='View Windows: Select Camera')
        process_input()
    
    def view_windows_page(self, camera):
        def process_input():
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(url=self.server_url + f'/cameras/{camera["id"]}/windows', headers=headers)
            json_response = response.json()
        
            windows = json_response['windows']

            for index, window in enumerate(windows):
                print(f'|----- {window["name"]}: ({window["top_left_x"]}, {window["top_left_y"]}) ({window["bottom_right_x"]}, {window["bottom_right_y"]})')

            while True:
                selection = input('|- Enter your selection: ')
                if selection == 'b':
                    self.back()
                    return

        self.render_page_header(header_message='View Windows: Select Camera')
        process_input()
    
    def select_camera_alert_page(self):
        def process_input():
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(url=self.server_url + '/cameras', headers=headers)
            json_response = response.json()
        
            cameras = json_response['cameras']

            for index, camera in enumerate(cameras):
                print(f'|----- {index+1}. {camera["name"]}')

            while True:
                selection = input('|- Enter your selection: ')
                if selection == 'b':
                    self.back()
                    return
                
                selection = int(selection.strip().lower())
                if selection > 0 and selection <= len(cameras):
                    self.forward('select_window_alert', cameras[selection-1])
                    break
                else:
                    print('|----- Invalid Selection.')

        self.render_page_header(header_message='Add Alert: Select Camera')
        process_input()

    def select_window_alert_page(self, camera):
        def process_input():
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(url=self.server_url + f'/cameras/{camera["id"]}/windows', headers=headers)
            json_response = response.json()
        
            windows = json_response['windows']

            for index, window in enumerate(windows):
                print(f'|----- {index+1}. {window["name"]}: ({window["top_left_x"]}, {window["top_left_y"]}) ({window["bottom_right_x"]}, {window["bottom_right_y"]})')

            while True:
                selection = input('|- Enter your selection: ')
                if selection == 'b':
                    self.back()
                    return

                selection = int(selection.strip().lower())
                if selection > 0 and selection <= len(windows):
                    self.forward('create_alert', windows[selection-1])
                    break
                else:
                    print('|----- Invalid Selection.')

        self.render_page_header(header_message=f'Add Alert: Select Window for Camera {camera["name"]}')
        process_input()

    def create_alert_page(self, window):
        def process_input():
            condition = input("|- Enter the alert condition (<, >, <=, >=): ")
            if condition.lower() == 'b':
                self.back(window)
                return
            threshold_value = input("|- Enter the threshold value: ")
            if threshold_value.lower() == 'b':
                self.back(window)
                return
            
            data = {
                'condition': condition,
                'threshold_value': float(threshold_value),
            }

            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.post(url=self.server_url + f'/windows/{window["id"]}/alerts', json=data, headers=headers)
            
            if response:
                json_response = response.json()
                print(json_response['message'])
                if response.status_code == 201:
                    self.back(window)
                else:
                    process_input()
            else:
                print('Error reaching server')
                process_input()

        self.render_page_header(header_message=f'Create Alert for Window: {window["name"]}')
        process_input()


    def select_camera_view_alerts_page(self):
        def process_input():
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(url=self.server_url + '/cameras', headers=headers)
            json_response = response.json()
        
            cameras = json_response['cameras']

            for index, camera in enumerate(cameras):
                print(f'|----- {index+1}. {camera["name"]}')

            while True:
                selection = input('|- Enter your selection: ')
                if selection == 'b':
                    self.back()
                    return
                
                selection = int(selection.strip().lower())
                if selection > 0 and selection <= len(cameras):
                    self.forward('select_window_view_alerts', cameras[selection-1])
                    break
                else:
                    print('|----- Invalid Selection.')

        self.render_page_header(header_message='View Alerts: Select Camera')
        process_input()

    def select_window_view_alerts_page(self, camera):
        def process_input():
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(url=self.server_url + f'/cameras/{camera["id"]}/windows', headers=headers)
            json_response = response.json()
        
            windows = json_response['windows']

            for index, window in enumerate(windows):
                print(f'|----- {index+1}. {window["name"]}: ({window["top_left_x"]}, {window["top_left_y"]}) ({window["bottom_right_x"]}, {window["bottom_right_y"]})')

            while True:
                selection = input('|- Enter your selection: ')
                if selection == 'b':
                    self.back()
                    return

                selection = int(selection.strip().lower())
                if selection > 0 and selection <= len(windows):
                    self.forward('view_alerts', windows[selection-1])
                    break
                else:
                    print('|----- Invalid Selection.')

        self.render_page_header(header_message=f'View Alerts: Select Window for Camera {camera["name"]}')
        process_input()

    def view_alerts_page(self, window):
        def process_input():
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(url=self.server_url + f'/windows/{window["id"]}/alerts', headers=headers)
            
            # Check if the response is successful and contains JSON data
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    alerts = json_response.get('alerts', [])

                    if not alerts:
                        print('|----- No alerts set for this window.')
                    else:
                        print('|----- Alerts for window:', window["name"])
                        for index, alert in enumerate(alerts):
                            print(f'|----- Alert {index+1}: Condition: {alert["condition"]} {alert["threshold_value"]}')

                except ValueError:
                    print('|----- Failed to retrieve alerts: Invalid server response')
            else:
                print(f'|----- Error {response.status_code}: Could not retrieve alerts for this window.')

            while True:
                selection = input('|- (B/b) Back to previous menu: ')
                if selection.lower() == 'b':
                    self.back()
                    return

        self.render_page_header(header_message=f'View Alerts for Window: {window["name"]}')
        process_input()





if __name__ == '__main__':
    menu = Menu('http://127.0.0.1:5000')
