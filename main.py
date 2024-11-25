from hashlib import sha256
from flask import Flask
import datetime
import json
import os

app = Flask(__name__)

def hash(v):
    return sha256(v.encode()).hexdigest()

def check_username(user):
    return os.path.exists(f"accounts/{user}")

def check_password(user, passwd):
    if not check_username(user):
        return False
    passwords = json.loads(open("passwords.json").read())
    return passwords[user] == hash(passwd)

@app.route('/send/<content>/<sender>/<passwd>/<user>')
def send(content, sender, passwd, user):
    passwords = json.loads(open("passwords.json").read())
    if not check_password(sender, passwd):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    dt = f"{datetime.datetime.now()}".replace(' ', '-')
    with open(f"accounts/{sender}/sended.txt", 'a') as f:
        f.write(f"{user} {dt} {content}\n")

    if os.path.exists(f"accounts/{user}"):
        with open(f"accounts/{user}/recived.txt", 'a') as f:
            f.write(f"{sender} {dt} {content}\n")
    else:
        return f"Failed: user {user} doent exists"
    return "sended"

@app.route('/get_all_rmessages/<passwd>/<user>')
def get_all_rmessages(passwd, user):
    passwords = json.loads(open("passwords.json").read())
    if not check_password(user, passwd):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    return open(f"accounts/{user}/recived.txt").read()

@app.route('/clear_all_rmessages/<passwd>/<user>')
def clear_all_rmessages(passwd, user):
    passwords = json.loads(open("passwords.json").read())
    if not check_password(user, passwd):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    open(f"accounts/{user}/recived.txt", 'w').write("")
    return "Cleared"

@app.route('/clear_all_smessages/<passwd>/<user>')
def clear_all_smessages(passwd, user):
    passwords = json.loads(open("passwords.json").read())
    if not check_password(user, passwd):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    open(f"accounts/{user}/sended.txt", 'w').write("")
    return "Cleared"

@app.route('/get_all_smessages/<passwd>/<user>')
def get_all_smessages(passwd, user):
    passwords = json.loads(open("passwords.json").read())
    if not check_password(user, passwd):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    return open(f"accounts/{user}/sended.txt").read()

@app.route('/reg/<passwd>/<user>')
def reg(passwd, user):
    if check_username(user):
        print("failed: username incorrect")
        return f"Failed: user exists"
    passwords = json.loads(open("passwords.json").read())
    passwords[user] = hash(passwd)
    json.dump(passwords, open("passwords.json", 'w'))
    os.mkdir(f"accounts/{user}")
    return "Registered"

@app.route('/')
def main():
    return open("main.html")

if __name__ == '__main__':
    app.run(port = 9932, host="0.0.0.0", ssl_context=('/server/cert.crt', '/server/cert.key'))
