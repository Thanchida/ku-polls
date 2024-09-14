## Installation Guide
1. Clone the repository
```commandline
git clone https://github.com/Thanchida/ku-polls.git
```

2. Navigate to the project directory
```commandline
cd ku-polls
```

3. Create a virtual environment
```commandline
python3 -m venv env
```

4. Activate the virtual environment
    * On MS Window use
   ```commandline
    \env\Scripts\activate
   ```
   * On macOS and Linux use
   ```commandline
    source env/bin/activate
   ```

5. Install the requirements package
```commandline
pip install -r requirements.txt
```

6. Set value for externalized variable
   * On MS Window use
      ```commandline
       copy .env.sample .env
      ```
   * On macOS and Linux use
     ```commandline
      cp .env.sample .env
     ```
After that, change the values in the .env file.

7. Run migrations
```commandline
python3 manage.py migrate
```

8. Install data from data fixtures
```commandline
python3 manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json
```

9. Run tests
```commandline
python3 manage.py test
```