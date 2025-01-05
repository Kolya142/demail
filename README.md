# Demail


## Install

1. **Set up the salt**:
   - Generate:
     ```bash
     head -c 40 /dev/urandom | od -An -v -tx1 | tr -d ' \n' > salt.txt
     chmod 600 salt.txt
     ```

3. **Configure the server hostname**:
   - In `main.html`, replace `http://127.0.0.1` with your server's hostname:
     ```html
      const response = await fetch(
          `http://127.0.0.1:9999/clear_all_smessages/${l_pass.value}/${l_username.value}`
      );
     ```

## Run

```bash
screen -dm bash -c "cd /server/demail; python3 main.py"
```