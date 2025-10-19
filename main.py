import uuid
import pickle
import hashlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv

from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import HorizontalGroup
from textual.widgets import Input, Button, Footer, Header, Label

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

class UsernameField(HorizontalGroup):
    def compose(self):
        _input = Input(id="username_input", compact=True)
        _input.action_submit = lambda: self.parent.query_one("#password_input").focus()
        
        yield Label("Username:", id="username_label") 
        yield _input

class PasswordField(HorizontalGroup):
    def compose(self):
        _input = Input(id="password_input", password=True, compact=True)
        _input.action_submit = lambda: self.parent.query_one("#login").press()
        
        yield Label("Password:", id="password_label")
        yield _input

class ErrorScreen(Screen):
    def __init__(self, error_msg: str, name = None, id = None, classes = None):
        self.error_msg = error_msg
        super().__init__(name, id, classes)
    
    def compose(self) -> ComposeResult:
        error_label = Label(self.error_msg, variant="error")
        error_label.styles.align = ("center", "middle")
        error_label.styles.border = ("solid", "red")
        
        yield error_label

class LoginScreen(Screen):
    def compose(self):
        yield UsernameField()
        yield PasswordField()
        yield Button("Login", variant="success", id="login")
    
    @on(Button.Pressed, "#login")
    def login(self):
        with open("users.dat", "rb") as file:
            users = pickle.loads(Fernet(os.getenv("KEY")).decrypt(pickle.loads(file.read())))

        username = self.query_one("#username_input").value.strip()
        password = self.query_one("#password_input").value.strip()
        
        for user in users:
            if user.username == username and user.password == hashlib.sha256(password.encode()).digest():
                self.mount(Label(f"Logged in as {user.first_name} {user.last_name}".strip()))
                break
        else:
            self.mount(Label("Invalid Credentials"))

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