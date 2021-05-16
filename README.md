# Covid Helper

## UI
<img src="https://github.com/yogeshchandrasekharuni/covid_helper/blob/main/utils/gui_screenshot.png" width="800">

## Documentation

### Directory structure
```
📦covidhelper
 ┣ 📂data
 ┃ ┣ 📜db_handler.py
 ┃ ┗ 📜readings.db
 ┣ 📂email_handler
 ┃ ┗ 📜email_handler.py
 ┣ 📂logs
 ┃ ┣ 📜base_logger.py
 ┣ 📂utils
 ┃ ┣ 📜credentials.pickle
 ┃ ┣ 📜gui_screenshot.png
 ┃ ┣ 📜thread_killer.py
 ┃ ┣ 📜requirements.txt
 ┃ ┗ 📜tkinter_bg.jpg
 ┣ 📜app.py
 ┣ 📜gui.py
 ┗ 📜launcher.py
 ```

### Classes

```db_handler.DBHandler```
- Handles storing, retrieving and querying to and from the database.

```email_handler.EmailHandler```
- Handles sending, recieving and validating emails.

```baselogger.logger```
- Parent logger, all other files import from it. If logging is to be turned off, make logger an instance of class ```base_logger.NotLogging```.

```thread_killer.KThread```
- Inherits from threading and spawns killable threads.

```app.App```
- CovidHelper application class, sends out reminder emails every _frequency_ seconds, recieves readings in the form of email-replies and stores it in the DB. Also sends out the day's readings every end-of-day.

```gui.AppGUI```
- User Interface that uses Tkinter. Supports settings window for saving user-credentials, plots their readings in the form of a graph and also shows the readings of the day in a table.


### Usage

1. Create a new virtual environment.
```
conda create -n your_env_name
```

2. Create a new burner account in Gmail. This email-ID will be used to send out reminder emails, retrieving readings, etc. You will need to enter its ID and password the first time you open the application.

2. Clone this repository.
```
git clone https://github.com/yogeshchandrasekharuni/covid_helper
```

3. Install the required packages.
```
pip install -r utils/requirements.txt
```

4. Run the launcher.
```
python launcher.py
```

5. In the GUI, open ```Settings``` and add your actual email address and the burner email account's address and password.

6. Click on ```Start/Stop```.

7. Click on ```Refresh stats``` to see the updated graphs and tables.


### Using the executable

- This project has been compiled into a standalone executable file. Incase you are not interested in going through few of the above steps, you can download the zip folder from this link.
