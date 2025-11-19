import json
import os
import uuid
import re
from hashlib import sha256

# A red asterisk using ANSI escape codes
REQUIRED_INDICATOR = "\033[31m*\033[0m"


# Override of the input() function to make it required
def input_required(
    prompt: str,
    disallow_duplicates: bool = False,
    number: bool = False,
    password_check: bool = False,
) -> str:
    while True:
        if password_check:
            print("""Requirements:
- Minimum of 8 in length
- At least 1 lowercase letter
- At least 1 uppercase letter
- At least 1 digit
- At least 1 symbol (!@#$%?)
- No spaces""")
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
            # Check if answer must adhere to minimum password complexity
            elif password_check:
                # Construct password requirement with RegEx
                lowercase = "(?=.*[a-z])"
                uppercase = "(?=.*[A-Z])"
                digit = "(?=.*\\d)"
                special = "(?=.*[!@#$%^&*?])"
                minimum_length = "[A-Za-z\\d!@#$%?]{8,}"
                pattern = f"^{lowercase}{uppercase}{
                    digit}{special}{minimum_length}$"

                # Check if pattern matches with given password
                match = re.match(pattern, answer)
                if match:
                    return answer
                else:
                    print("Password is not secure enough.")
            else:
                return answer


# Creating users
def create_user() -> dict:
    # Ask for info
    fname = input_required("First Name: ").strip().lower().capitalize()
    lname = input("Last Name: ").strip().lower().capitalize()
    username = input_required("Username: ").strip()
    password = input_required("Password: ", password_check=True).strip()

    # Package new user as dictionary
    user = {
        "first_name": fname,
        "last_name": lname,
        "username": username,
        "password": sha256(password.encode()).hexdigest(),
        "id": str(uuid.uuid4()),
    }

    # Import current users list if user.json exists
    if os.path.exists("users.json") and os.path.getsize("users.json") != 0:
        with open("users.json", "r") as file:
            users = json.load(file)
    else:
        users = []

    # Open users.json in write mode
    with open("users.json", "w") as file:
        # Append the new user
        users.append(user)

        # Write data into users.json
        file.write(json.dumps(users, indent=4))

        # Return dictionary (for logging in)
        return user


# Logging in with username and password as arguments
def login(username: str, password: str) -> bool:
    # Open users.json in read mode
    with open("users.json", "r") as file:
        # Iterate over entire list
        for user in list(json.load(file)):
            # If username and password match is found, print greet msg
            if (
                user.get("username") == username
                and user.get("password") == sha256(password.encode()).hexdigest()
            ):
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
                                # To skip over password field
                                if not key == "password":
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
                    options = ["First Name", "Last Name", "Username", "Password"]
                    for i in range(len(options)):
                        print(f"{i+1}. {options[i]}")

                    # Ask for input
                    option = input("Select a field to modify (Press enter to exit): ")

                    # If input not empty
                    if option:
                        # Check if input is valid
                        try:
                            option = int(option)
                            options[option - 1]
                        except ValueError:
                            print("Invalid input.")
                            continue
                        except IndexError:
                            print("Input out of range.")
                            continue

                        # Ask user for input to replace current data
                        replacement = input(f"Enter a {options[option-1].lower()} to replace the current one (press Enter to cancel): ")

                        # If input not empty
                        if replacement:
                            # Duplicate user
                            modified_user = user.copy()

                            # Update user data
                            modified_user.update(
                                {
                                    options[option - 1]  # Original text
                                    .lower()  # Turn all char to lowercase
                                    .replace(" ", "_"): replacement
                                }
                            )

                            # Open users.json in read and write mode
                            with open("users.json", "r") as file:
                                users = list(json.load(file))
                            
                            # Remove original user
                            users.remove(user)  

                            # Add modified user
                            users.append(modified_user)

                            # Write to file new data
                            with open("users.json", "w") as file:
                                file.write(json.dumps(users, indent=4))  
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
                print("1 user remaining in the list. Logout and delete 'users.json' file to delete")
                break

        # Ask for username input
        username = input("Enter username to delete (press Enter to exit): ")
        if username:
            # Find user
            user = find_user(username)
            # If matching user is found
            if user:
                with open("users.json", "r") as file:
                    # Remove user
                    users = list(json.load(file))
                    users.remove(user)
                
                # Write changes to file
                with open("users.json", "w") as file:
                    file.write(json.dumps(users, indent=4))

                print("User successfully removed.")
            # If user not found
            else:
                print("User not found.")
        # If username input is empty
        else:
            break


# Check if users.json file exists
if not os.path.exists("users.json") or os.path.getsize("users.json") == 0:
    print("'users.json' file not found or is empty.")
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