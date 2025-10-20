import uuid
import pickle
import hashlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv

from textual import on
from textual.events import Key
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import HorizontalGroup, Horizontal, Grid, CenterMiddle
from textual.widgets import Input, Button, Label

import os

class user:
    def __init__(self, username: str, password: str, first_name: str, last_name: str):
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

class ErrorScreen(Screen):
    def __init__(self, error_msg: str, name = None, id = None, classes = None):
        self.error_msg = error_msg
        super().__init__(name, id, classes)
        self.styles.align = ("center", "middle")
    
    @on(Key)
    def quit(self):
        self.parent.exit()
    
    def compose(self) -> ComposeResult:
        error_label = Label(self.error_msg, variant="error")
        error_label.styles.border = ("tall", "red")

        any_key = Label("Press any key to exit")
        
        yield error_label
        yield any_key

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

class UserCreateScreen(Screen):
    def __init__(self, current_user: user, name = None, id = None, classes = None):
        self.current_user = current_user
        super().__init__(name, id, classes)
    
    def compose(self):
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
        self.parent.switch_screen(HomeScreen(self.current_user))

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
        self.parent.switch_screen(UserCreateScreen(self.current_user))

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

        with open("users.dat", "rb") as file:
            users = pickle.loads(Fernet(os.getenv("KEY")).decrypt(pickle.loads(file.read())))

        username = self.query_one("#username_input").value.strip()
        password = self.query_one("#password_input").value.strip()
        
        for user in users:
            if user.username == username and user.password == hashlib.sha256(password.encode()).digest():
                self.parent.switch_screen(HomeScreen(user))
                break
        else:
            self.set_timer(1, lambda: self.mount(Label("Invalid Credentials", id="login_callback"))) 

class MainApp(App):
    theme = "textual-dark"
    CSS_PATH = "style.tcss"

    def on_mount(self) -> None:
        if not os.path.exists("users.dat"):
            self.push_screen(ErrorScreen("ERROR: 'users.dat' file not found. Was the starter program ran?"))
        else:
            load_dotenv()
            self.push_screen(LoginScreen())

if __name__ == "__main__":
    app = MainApp()
    app.run()