import requests

class Menu:
    def __init__(self, server_url):
        self.server_url = server_url 
        self.nav_stack = ['initial_page']
        self.render_active_page()
        self.jwt_token = None
    
    def back(self):
        # Remove page from top of stack and render the new active page
        self.nav_stack.pop()
        self.render_active_page()
    
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
        # Define pages
        pages = {
            'initial_page': self.initial_page,
            'login': self.login_page,
            'register': self.register_page,
            'main_menu': self.main_menu_page,
            'create_window': self.create_window_page,
            'select_camera': self.select_camera_page,
        }

        print('\n\n----------------------------------------\n')
        # Render page from top of stack
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
            # Get selection
            while True:
                selection = input('|- Enter your selection: ')
                selection = selection.strip().lower()

                if selection == '1': 
                    self.forward('select_camera')
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
        process_selection()
    
    def create_window_page(self, camera_name):
        def process_input():
            name = input("|- Enter the windows name: ")
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
            # TODO: send to server and await response. 
            response = True
            if response:
                print('Window creation successful, alert set.')
                self.back()

        self.render_page_header(header_message=f'Create Window: {camera_name}')
        process_input()

    def select_camera_page(self):
        def process_input():
            cameras = ['camera1', 'camera2', 'camera3']

            for index, camera in enumerate(cameras):
                print(f'|----- {index+1}. {camera}')

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

        self.render_page_header(header_message='Create Window')
        process_input()


if __name__ == '__main__':
    menu = Menu('http://127.0.0.1:5000')
