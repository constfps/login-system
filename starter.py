from main import user
from cryptography.fernet import Fernet
import pickle
import os

# Create user and store in array
username = input("Username: ")
password = input("Password: ")
fname = input("First Name: ")
lname = input("Last Name: ")

data = user(username, password, fname, lname)
array = [data]

# Generate encryption key and store in .env file
key = Fernet.generate_key().decode() # Key generated is generated as byte literal so we decode to string to simplify
with open(".env", "w") as file:
    file.write(f"KEY={key}")

# Check if "user.dat" file exists and ask user if they still want to proceed
if os.path.exists("users.dat"):
    if input("Existing 'users.dat' file detected. Proceed? (y/n): ") == "n":
        print("Program aborted")
        exit(0)

print(data.password)

with open("users.dat", "wb") as file:
    pickle.dump(Fernet(key).encrypt(pickle.dumps(array)), file)