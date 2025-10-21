import uuid
import pickle
import hashlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv

from textual import on
from textual.events import Key
from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.containers import HorizontalGroup, Horizontal, Grid, CenterMiddle
from textual.widgets import Input, Button, Label

import os

class user:
    def __init__(self, username: str, password: str, first_name: str, last_name: str = ""):
        self.username = username
        self.password = hashlib.sha256(password.encode()).digest()
        self.first_name = first_name
        self.last_name = last_name
        self.id = str(uuid.uuid4())

    def export(self) -> dict:
        return {
            "username": self.username,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "id": self.id
        }
    
    def __str__(self):
        return f"First Name: {self.first_name} Last Name: {self.last_name}"

class Header(Horizontal):
    def __init__(self, user: user):
        self.current_user = user
        user_indicator = Label(f"Logged in as {self.current_user.first_name} {self.current_user.last_name}".strip(), id="current_user")
        logout = Button("Logout", variant="error", id="logout", compact=True)

        super().__init__(user_indicator, logout)

    @on(Button.Pressed, "#logout")
    def logout(self):
        self.parent.parent.switch_screen(LoginScreen(self.current_user))

class FirstNameField(HorizontalGroup):
    def compose(self):
        _input = Input(id=f"fname_input", compact=True)
        _input.action_submit = lambda: self.parent.query_one("#lname_input").focus()

        yield Label("First Name:", id="fname_label")
        yield _input.focus()

class LastNameField(HorizontalGroup):
    def compose(self):
        _input = Input(id=f"lname_input", compact=True)
        _input.action_submit = lambda: self.parent.query_one("#username_input").focus()

        yield Label("Last Name:", id="lname_label")
        yield _input

class UsernameField(HorizontalGroup):
    def compose(self):
        _input = Input(id="username_input", compact=True)
        _input.action_submit = lambda: self.parent.query_one("#password_input").focus()
        
        yield Label("Username:", id="username_label") 
        yield _input

class PasswordField(HorizontalGroup):
    def compose(self):
        _input = Input(id="password_input", password=True, compact=True)
        _input.action_submit = lambda: self.parent.query_one("Button").press()
        
        yield Label("Password:", id="password_label")
        yield _input

class ErrorModal(ModalScreen):
    def __init__(self, message: str = "An error has occured.", name = None, id = None, classes = None):
        self.message = message
        super().__init__(name, id, classes)
    
    BINDINGS = [("q", "clear", "Clear modal")]
    
    def compose(self):
        yield Label(self.message + "\n")
        yield Label("Press any key to clear")
    
    @on(Key)
    def clear(self):
        self.app.pop_screen()

class UserCreateScreen(Screen):
    def __init__(self, current_user: user = None, name = None, id = None, classes = None):
        self.current_user = current_user
        super().__init__(name, id, classes)
    
    def compose(self):
        if self.current_user:
            yield Header(self.current_user)
        yield CenterMiddle(
            FirstNameField(),
            LastNameField(),
            UsernameField(),
            PasswordField(),
            Horizontal(
                Button("Submit", variant="success", id="submit_create"),
                Button("Cancel", variant="error", id="cancel_create"),
                id="buttons"
            )
        )
    
    @on(Button.Pressed, "#cancel_create")
    def cancel(self):
        if self.current_user:
            self.app.switch_screen(HomeScreen(self.current_user))
        else:
            self.app.exit()
    
    @on(Button.Pressed, "#submit_create")
    def submit(self):
        fname = self.query_one("#fname_input").value.strip()
        lname = self.query_one("#lname_input").value.strip()
        username = self.query_one("#username_input").value.strip()
        password = self.query_one("#password_input").value.strip()
        
        for data in [fname, username, password]:
            if not data:
                self.app.push_screen(ErrorModal("One or more required fields are empty. Please verify and try again."))
                break
        else:
            if self.current_user:
                key = os.getenv("KEY")
                with open("users.dat", "rb") as file:
                    users = list(pickle.loads(Fernet(key).decrypt(pickle.loads(file.read()))))

                users.append(user(username, password, fname, lname))
                with open("users.dat", "wb") as file:
                    pickle.dump(Fernet(key).encrypt(pickle.dumps(users)), file)

                self.app.switch_screen(HomeScreen(self.current_user))
            else:
                key = Fernet.generate_key().decode()
                with open(".env", "w") as file:
                    file.write(f"KEY={key}")

                with open("users.dat", "wb") as file:
                    pickle.dump(Fernet(key).encrypt(pickle.dumps([user(username, password, fname, lname)])), file)
                
                self.app.switch_screen(LoginScreen())
            self.app.push_screen(ErrorModal("User successfully added!"))

class FirstTimeScreen(Screen):
    def compose(self):
        yield CenterMiddle(
            Label("users.dat and/or .env file not found. Looks like this is your first time running this program"),
            Label("Would you like to make a new user?"),
            Horizontal(
                Button("Yes", variant="success", id="firsttime_yes"),
                Button("No", variant="error", id="firsttime_no")
            )
        )
    
    @on(Button.Pressed, "#firsttime_yes")
    def create(self):
        self.app.switch_screen(UserCreateScreen())

    @on(Button.Pressed, "#firsttime_no")
    def quit(self):
        self.app.exit()

class HomeScreen(Screen):
    def __init__(self, current_user: user, name = None, id = None, classes = None):
        self.current_user = current_user
        super().__init__(name, id, classes)
    
    def compose(self):
        yield Header(self.current_user)
        home_buttons = Grid(
            Button("Create user", id="create", variant="success", compact=True).focus(),
            Button("Find user", id="find", variant="primary", compact=True),
            Button("Modify user", id="modify", variant="warning", compact=True),
            Button("Delete user", id="delete", variant="error", compact=True),
            Button("Export users", id="export", compact=True),
            Button("About", id="about", compact=True),
            id="home_buttons"
        )
        yield home_buttons
    
    @on(Button.Pressed, "#create")
    def create_user(self):
        self.app.switch_screen(UserCreateScreen(self.current_user))

class LoginScreen(Screen):
    def compose(self):
        yield CenterMiddle(
            UsernameField(),
            PasswordField(),
            Button("Login", variant="success", id="login")
        )
    
    @on(Button.Pressed, "#login")
    async def login(self):
        try:
            await self.query_one("#login_callback").remove()
        except:
            pass

        load_dotenv()
        with open("users.dat", "rb") as file:
            users = pickle.loads(Fernet(os.getenv("KEY")).decrypt(pickle.loads(file.read())))

        username = self.query_one("#username_input").value.strip()
        password = self.query_one("#password_input").value.strip()
        
        for user in users:
            if user.username == username and user.password == hashlib.sha256(password.encode()).digest():
                self.app.switch_screen(HomeScreen(user))
                break
        else:
            self.set_timer(1, lambda: self.mount(Label("Invalid Credentials", id="login_callback"))) 

class MainApp(App):
    theme = "textual-dark"
    CSS_PATH = "style.tcss"

    def on_mount(self) -> None:
        if not os.path.exists("users.dat"):
            self.push_screen(FirstTimeScreen())
        elif not os.path.exists(".env"):
            self.push_screen(FirstTimeScreen())
        else:
            self.push_screen(LoginScreen())

if __name__ == "__main__":
    app = MainApp()
    app.run()