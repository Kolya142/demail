from hashlib import sha256, sha512
import atexit
from flask import Flask, request
from asgiref.wsgi import WsgiToAsgi
import datetime
import json
import stat
import os

def get_chmod(path):
    return stat.S_IMODE(os.stat(path).st_mode)

def srm(path):    
    for _ in range(10):
        with open(path, 'wb') as f:
            f.write(os.urandom(5000))
    os.remove(demail_keys_path)

app = Flask(__name__)
salt_path = "/root/.demail-salt"
if get_chmod(salt_path) != 0o600:
    print("ERROR: too open salt file, requires 600")
    r = input("remove it for secure?(Y/N)")
    if r == "Y":
        srm(salt_path)
    exit(1)
salt = open(salt_path).read()
keys = {}

demail_keys_path = "/root/.demail-keys.json"

if os.path.exists(demail_keys_path):
    if get_chmod(salt_path) != 0o600:
        print("ERROR: too open keys file, requires 600")
        r = input("remove it for secure?(Y/N)")
        if r == "Y":
            srm(demail_keys_path)
        exit(1)
    with open(demail_keys_path, 'r') as f:
        keys = json.load(f)

    srm(demail_keys_path)

@atexit.register
def cleanup():
    print("saving keys...")
    with open(demail_keys_path, 'w') as f:
        json.dump(keys, f)
    os.chmod(demail_keys_path, 0o600)

def hash(v):
    return sha256(v.encode()).hexdigest()

def check_username(user):
    return os.path.exists(f"accounts/{user}")

def get_password(user):
    passwords = json.loads(open("passwords.json").read())
    return passwords[user]

def check_password(user, passwd):
    if not check_username(user):
        return False
    return get_password(user) == hash(passwd)

def generate_key(p, s, u):
    global keys
    if s in keys:
        return keys[s]
    key = hash(p + s + salt + os.urandom(32).hex())
    keys[s] = key
    return key

def simple_encoder(raw_key, message):
    key = int.from_bytes(sha512(raw_key.encode()).digest(), 'big')
    for _ in range(256):
        key ^= key << 8
        key ^= key >> 16
    msg = int.from_bytes(message, 'big') ^ key

    return msg.to_bytes((msg.bit_length() + 7) // 8, 'big')


@app.route('/send/<sender>/<passwd>/<user>', methods = ['POST'])
def send(sender, passwd, user):
    content = request.data.decode()
    if not check_password(sender, passwd):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    dt = f"{datetime.datetime.now()}".replace(' ', '-')
    key = generate_key(passwd, sender, user)
    content = simple_encoder(key, content.encode()).hex()
    with open(f"accounts/{sender}/sended.txt", 'a') as f:
        f.write(f"{user} {dt} {content}\n")

    if os.path.exists(f"accounts/{user}"):
        with open(f"accounts/{user}/recived.txt", 'a') as f:
            f.write(f"{sender} {dt} {sha512(key.encode()).hexdigest()} {content}\n")
    else:
        return f"Failed: user {user} doent exists"
    return "sended"

@app.route('/get_all_rmessages/<passwd>/<user>')
def get_all_rmessages(passwd, user):
    if not check_password(user, passwd):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    msgs = open(f"accounts/{user}/recived.txt").read().split('\n')
    out = ""
    for msg in msgs:
        sp = msg.split(maxsplit=4)
        if len(sp) != 4:
            continue
        c = bytes.fromhex(sp[3])
        if sp[0] not in keys or sha512(keys[sp[0]].encode()).hexdigest() != sp[2]:
            out += f"у меня нет ключа для расшифровывания этого сообщения({c.hex()})\n"
            continue
        out += f'{sp[0]}({sp[1]}): {simple_encoder(keys[sp[0]], c).decode(errors='ignore')}\n'
    return out

@app.route('/clear_all_rmessages/<passwd>/<user>')
def clear_all_rmessages(passwd, user):
    if not check_password(user, passwd):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    open(f"accounts/{user}/recived.txt", 'w').write("")
    return "Cleared"

@app.route('/clear_all_smessages/<passwd>/<user>')
def clear_all_smessages(passwd, user):
    if not check_password(user, passwd):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    open(f"accounts/{user}/sended.txt", 'w').write("")
    return "Cleared"

@app.route('/get_all_smessages/<passwd>/<user>')
def get_all_smessages(passwd, user):
    if not check_password(user, passwd):
        print("failed: username incorrect")
        return f"Failed: login/password incorrect"
    msgs = open(f"accounts/{user}/sended.txt").read().split('\n')
    out = ""
    key = keys[user]
    for msg in msgs:
        sp = msg.split(maxsplit=3)
        if len(sp) != 3:
            continue
        c = bytes.fromhex(sp[2])
        out += f'{simple_encoder(key, c).decode(errors='ignore')}({sp[1]}) -> {sp[0]}\n'
    return out

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

def create_app():
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
    return app

app = create_app()
if __name__ == '__main__':
    app.run("0.0.0.0", 9932)
