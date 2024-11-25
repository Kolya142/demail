# Demail

this readme was written by chatgpt.

## Installation

1. **Set up the salt file**:
   - First, create the salt file:
     ```bash
     echo SALT > /root/.demail-salt
     ```

2. **Set the correct file permissions**:
   - Ensure that the salt file is only accessible by the root user for security purposes:
     ```bash
     chmod 600 /root/.demail-salt
     ```

3. **Configure the server hostname**:
   - In `main.html`, replace `sh-fall.ru` with your own server's hostname to ensure proper communication:
     ```html
     <!-- Change the hostname in the following line -->
      const response = await fetch(
          `https://sh-fall.ru:9932/clear_all_smessages/${l_pass.value}/${l_username.value}`
      );
     ```
4. **Optional: translate main.html**

## Running the Application

It is recommended to run the application in a detached `screen` session to ensure it continues running even after you disconnect from the terminal.

```bash
screen -dm bash -c "cd /server/demail; python3 main.py"
