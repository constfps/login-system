import json
import os
import uuid

REQUIRED_INDICATOR = "\033[31m*\033[0m"


def input_required(prompt: str, disallow_duplicates: bool = False) -> str:
    while True:
        answer = input(prompt)
        if not answer:
            print("This field is required. Please try again.")
        else:
            if disallow_duplicates:
                with open("users.json", "r") as file:
                    for user in list(json.load(file)):
                        if user.get("username") == answer:
                            print("Username taken.")
                            break
                    else:
                        return answer
            else:
                return answer


def create_user() -> dict:
    fname = input_required(f"{REQUIRED_INDICATOR}First Name: ")
    lname = input("Last Name: ")
    username = input_required(f"{REQUIRED_INDICATOR}Username: ")
    password = input_required(f"{REQUIRED_INDICATOR}Password: ")

    with open("users.json", "w") as file:
        data = {
            "first_name": fname,
            "last_name": lname,
            "username": username,
            "password": password,
            "id": str(uuid.uuid4())
        }
        file.write(json.dumps([data], indent=4))
        return data


def login(username: str, password: str) -> bool:
    with open("users.json", "r") as file:
        for user in list(json.load(file)):
            if user.get("username") == username and user.get("password") == password:
                print((f"Welcome, {user.get("first_name")} {user.get("last_name")}").strip())
                break
        else:
            return False
        return True


def find_user(username: str = None):
    if username:
        while True:
            username = input_required("Enter username to search for (Press enter to exit): ").strip()
            if username:
                with open("users.json", "r") as file:
                    for user in list(json.load(file)):
                        if user.get("username") == username:
                            for key in user.keys():
                                label = key.replace("_", " ").title()
                                print(f"{label}: {user.get(key)}")
                            break
                    else:
                        print("User not found")
            else:
                break
    else:
        with open("users.json", "r") as file:
            for user in list(json.load(file)):
                if user.get("username") == username:
                    return user
            else:
                return None


def modify_user():
    while True:
        username = input_required("Enter username to modify (Press enter to exit): ")
        if username:
            user = find_user(username)
            if user:
                pass
            else:
                print("User not found. Please try again.")


if not os.path.exists("users.json"):
    print("'users.json' file not found.")
    response = input("Make a new user? [Y/n]: ")
    if response.lower() == "n":
        exit(0)

    user = create_user()
    login(user.get("username"), user.get("password"))
else:
    try:
        with open("users.json", "r") as file:
            json.load(file)
    except json.JSONDecodeError:
        print("'users.json' file corrupted. Aborting")

    logged_in = False
    username = input_required("Username: ")
    password = input_required("Password: ")

    while True:
        if login(username, password):
            break
        else:
            print("Invalid credentials.")
            username = input_required("Username: ")
            password = input_required("Password: ")

while True:
    print("-----------------------------")
    print("What would you like to do?")
    print("1. Create user")
    print("2. Enquire user")
    print("3. Modify user")
    print("4. Remove user")
    print("5. Exit")

    try:
        selected = int(input_required("Answer: "))
    except ValueError:
        print("Invalid input. Please try again.\n")
        continue

    if selected == 5:
        exit()
    elif selected == 1:
        print("Enter the new user's information")
        create_user()
    elif selected == 2:
        find_user()
