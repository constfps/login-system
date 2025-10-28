import json
import os
import uuid

REQUIRED_INDICATOR = "\033[31m*\033[0m"


def input_required(prompt: str, disallow_duplicates: bool = False, number: bool = False) -> str:
    while True:
        answer = input(REQUIRED_INDICATOR + prompt).strip()
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
            elif number:
                try:
                    return int(answer)
                except ValueError:
                    print("Input must be a number")
            else:
                return answer


def create_user() -> dict:
    fname = input_required("First Name: ")
    lname = input("Last Name: ")
    username = input_required("Username: ")
    password = input_required("Password: ")

    with open("users.json", "w") as file:
        data = {
            "first_name": fname,
            "last_name": lname,
            "username": username,
            "password": password,
            "id": str(uuid.uuid4()),
        }
        file.write(json.dumps([data], indent=4))
        return data


def login(username: str, password: str) -> bool:
    with open("users.json", "r") as file:
        for user in list(json.load(file)):
            if user.get("username") == username and user.get("password") == password:
                print(
                    (
                        f"Welcome, {user.get("first_name")} {
                            user.get("last_name")}"
                    ).strip()
                )
                break
        else:
            return False
        return True


def find_user(username: str = None):
    if not username:
        while True:
            username = input_required(
                "Enter username to search for (Press enter to exit): "
            ).strip()
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
        username = input("Enter username to modify (Press enter to exit): ")
        if username:
            user = find_user(username)
            if user:
                while True:
                    options = ["First Name", "Last Name", "Username", "Password"]
                    for i in range(len(options)):
                        print(f"{i+1}. {options[i]}")
                    option = input_required(
                        "Select a parameter to modify (Press enter to exit): "
                    )
                    if option:
                        replacement = input_required(f"Enter a {options[option-1]} to replace the current one: ", number=True)
                        if replacement:
                            modified_user = user
                            modified_user.update({options[option-1].lower().replace(" ", "_"): replacement})
                            with open("users.json", "r+") as file:
                                users = list(json.load(file))
                                users.remove(user)
                                users.append(modified_user)
                        else:
                            break
                    else:
                        break
            else:
                print("User not found. Please try again.")
        else:
            break


def remove_user():
    while True:
        username = input("Enter username to delete (press Enter to exit): ")
        if username:
            user = find_user(username)
            if user:
                with open("users.json", "r+") as file:
                    users = list(json.load(file))
                    users.remove(user)
                print("User successfully removed.")
            else:
                print("User not found.")
        else:
            break


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

    selected = input_required("Answer: ", number=True)

    if selected == 5:
        exit()
    elif selected == 1:
        print("Enter the new user's information")
        create_user()
    elif selected == 2:
        find_user()
    elif selected == 3:
        modify_user()
