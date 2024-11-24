from flask import Flask
import datetime
import json
import os

app = Flask(__name__)

@app.route('/send/<content>/<sender>/<passwd>/<user>')
def send(content, sender, passwd, user):
    passwords = json.loads(open("passwords.json").read())
    if not os.path.exists(f"accounts/{sender}"):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    if passwords[sender] != passwd:
        print("failed: password incorrect")
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
    if not os.path.exists(f"accounts/{user}"):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    if passwords[user] != passwd:
        print("failed: password incorrect")
        return f"Failed: login/password incorrect"
    return open(f"accounts/{user}/recived.txt").read()

@app.route('/get_all_smessages/<passwd>/<user>')
def get_all_smessages(passwd, user):
    passwords = json.loads(open("passwords.json").read())
    if not os.path.exists(f"accounts/{user}"):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    if passwords[user] != passwd:
        print("failed: password incorrect")
        return f"Failed: login/password incorrect"
    return open(f"accounts/{user}/sended.txt").read()

@app.route('/reg/<passwd>/<user>')
def reg(passwd, user):
    if os.path.exists(f"accounts/{user}"):
        print("failed: username incorrect")
        return f"Failed: user exists"
    passwords = json.loads(open("passwords.json").read())
    passwords[user] = passwd
    json.dump(passwords, open("passwords.json", 'w'))
    os.mkdir(f"accounts/{user}")
    return "Registered"

@app.route('/')
def main():
    return open("main.html")

if __name__ == '__main__':
    app.run(port = 9932, host="0.0.0.0", ssl_context=('/server/cert.crt', '/server/cert.key'))
