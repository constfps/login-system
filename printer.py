from cryptography.fernet import Fernet
import pickle
import os  
from dotenv import load_dotenv

if not os.path.exists("users.dat"):
    print("users.dat file not found. Aborting")
    exit(1)
elif not os.path.exists(".env"):
    print(".env file not found. Aborting")
    exit(1)

load_dotenv()

key = os.getenv("KEY")
with open("users.dat", "rb") as file:
    for user in pickle.loads(Fernet(key).decrypt(pickle.loads(file.read()))):
        print(user)