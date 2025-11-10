import json
import os
import uuid
from hashlib import sha256

# A red asterisk using ANSI escape codes
REQUIRED_INDICATOR = "\033[31m*\033[0m"


# Override of the input() function to make it required
def input_required(
    prompt: str, disallow_duplicates: bool = False, number: bool = False
) -> str:
    while True:
        answer = input(REQUIRED_INDICATOR + prompt).strip()

        # Check if answer is empty
        if not answer:
            print("This field is required. Please try again.")
        else:
            # Check if username already exists
            if disallow_duplicates:
                with open("users.json", "r") as file:
                    for user in list(json.load(file)):
                        if user.get("username") == answer:
                            print("Username taken.")
                            break
                    else:
                        return answer
            # Check if answer needs to be a number
            elif number:
                try:
                    return int(answer)
                except ValueError:
                    print("Input must be a number")
            else:
                return answer


# Creating users
def create_user() -> dict:
    # Ask for info
    fname = input_required("First Name: ").strip()
    lname = input("Last Name: ").strip()
    username = input_required("Username: ").strip()
    password = input_required("Password: ").strip()

    # Open users.json in write mode
    with open("users.json", "w") as file:
        # Package data in a dictionary
        data = {
            "first_name": fname,
            "last_name": lname,
            "username": username,
            "password": sha256(password.encode()).hexdigest(),
            "id": str(uuid.uuid4()),
        }

        # Write data into users.json
        file.write(json.dumps([data], indent=4))

        # Return dictionary (for logging in)
        return data


# Logging in with username and password as arguments
def login(username: str, password: str) -> bool:
    # Open users.json in read mode
    with open("users.json", "r") as file:
        # Iterate over entire list
        for user in list(json.load(file)):
            # If username and password match is found, print greet msg
            if user.get("username") == username and user.get("password") == sha256(password.encode()).hexdigest():
                print(
                    (
                        f"Welcome, {user.get("first_name")} {
                            user.get("last_name")}"
                    ).strip()
                )
                break
        # If none are found, return False
        else:
            return False

        # Returns true if username and password matches
        return True


# For finding user(s)
def find_user(username: str = None):
    # If no username is provided get input and no returns
    if not username:
        while True:
            # Ask for input
            username = input(
                "Enter username to search for (Press enter to exit): "
            ).strip()

            # If not empty
            if username:
                # Open users.json in read mode
                with open("users.json", "r") as file:
                    # Iterate over users list
                    for user in list(json.load(file)):
                        # If username matches, print all user data
                        if user.get("username") == username:
                            for key in user.keys():
                                # Formatting label
                                label = key.replace("_", " ").title()
                                print(f"{label}: {user.get(key)}")
                            break
                    # If user is not found
                    else:
                        print("User not found")
            # Exit if input is empty
            else:
                break
    # If username is provided, return user if found (for other functions)
    else:
        # Open users.json in read mode
        with open("users.json", "r") as file:
            for user in list(json.load(file)):
                if user.get("username") == username:
                    return user
            else:
                return None


# Modifying user data
def modify_user():
    while True:
        # Ask for input
        username = input("Enter username to modify (Press enter to exit): ")
        if username:
            # Get user
            user = find_user(username)

            # If user is found
            if user:
                while True:
                    # Print options
                    options = ["First Name", "Last Name",
                               "Username", "Password"]
                    for i in range(len(options)):
                        print(f"{i+1}. {options[i]}")

                    # Ask for input
                    try:
                        option = int(
                            input("Select a field to modify (Press enter to exit): ")
                        )
                        options[option-1]
                    except ValueError:
                        print("Invalid input.")
                        continue
                    except IndexError:
                        print("Input out of range.")
                        continue

                    # If input not empty
                    if option:
                        # Ask user for input to replace current data
                        replacement = input(
                            f"Enter a {
                                options[option-1].lower()} to replace the current one (press Enter to cancel): "
                        )

                        # If input not empty
                        if replacement:
                            # Duplicate user
                            modified_user = user

                            # Update user data
                            modified_user.update(
                                {
                                    options[option - 1]  # Original text
                                    .lower()  # Turn all char to lowercase
                                    .replace(" ", "_"): replacement
                                }
                            )

                            # Open users.json in read and write mode
                            with open("users.json", "r+") as file:
                                users = list(json.load(file))
                                users.remove(user)  # Remove original user

                                # Add modified user
                                users.append(modified_user)
                                file.write(json.dump(users))  # Write to file
                    # If field input is empty
                    else:
                        break
            # If no user is found
            else:
                print("User not found. Please try again.")
        # If username input is empty
        else:
            break


# For removing user(s)
def remove_user():
    while True:
        # Check if there's one user in users list
        with open("users.json", "r") as file:
            if len(list(json.load(file))) <= 1:
                print(
                    "1 user remaining in the list. Logout and delete 'users.json' file to delete"
                )
                break

        # Ask for username input
        username = input("Enter username to delete (press Enter to exit): ")
        if username:
            # Find user
            user = find_user(username)
            if user:
                with open("users.json", "r+") as file:
                    # Remove user and write to file
                    users = list(json.load(file))
                    users.remove(user)
                    file.write(json.dump(users))
                print("User successfully removed.")
            # If user not found
            else:
                print("User not found.")
        # If username input is empty
        else:
            break


# Check if users.json file exists
if not os.path.exists("users.json"):
    print("'users.json' file not found.")
    # Ask user if they want to make a new user
    response = input("Make a new user? [Y/n]: ")
    if response.lower() == "y" or not response:
        # Create new user and login
        user = create_user()
        login(user.get("username"), user.get("password"))
    else:
        exit(0)
# If users.json file exists
else:
    # Check user.json file integrity
    try:
        with open("users.json", "r") as file:
            json.load(file)
    except json.JSONDecodeError:
        print("'users.json' file corrupted. Aborting")
        exit(0)

    # Log in
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
    # Print options
    print("-----------------------------")
    print("What would you like to do?")
    print("1. Create user")
    print("2. Inquire user")
    print("3. Modify user")
    print("4. Remove user")
    print("5. Exit")

    # Ask for input
    selected = input_required("Answer: ", number=True)

    # Do operation according to input
    if selected == 5:
        break
    elif selected == 1:
        print("Enter the new user's information")
        create_user()
    elif selected == 2:
        find_user()
    elif selected == 3:
        modify_user()
    elif selected == 4:
        remove_user()
    else:
        print("Input out of range.")
