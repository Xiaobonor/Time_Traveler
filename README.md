# Time_Traveler

## IMPORTANT
Don't use flask to run the app in production. Use a WSGI server like Gunicorn or uWSGI.

## Setup
### 1. Install requirements
Recommend to use virtual environment for python 3.12.  
All requirements are listed in the `requirements.txt` file. To install them, using "pip install -r requirements.txt" should suffice.
### 2. Configure environment variables
Edit `.env` file in the root directory and add the following environment variables:
```
# -- Flask --
HOST="0.0.0.0"
PORT=80
# If DEBUG True, flask will run in debug mode.
# If SECRET_KEY not False, flask will generate a random key every time it starts.
DEBUG=True
SECRET_KEY=""
SESSION_TIMEOUT=604800

# -- Settings --
# If True, the app will use Azure OpenAI API, otherwise it will use OpenAI API.
USE_AZURE_OPENAI=False

# -- AZURE --
AZURE_ENDPOINT=""
AZURE_KEY=""

# -- Keys --
GOOGLE_OAUTH_CLIENT_ID=""
GOOGLE_OAUTH_CLIENT_SECRET=""
OPENAI_API_KEY=False

# -- Database --
MONGO_URI=""
REDIS_URI=""
```
### 3. Run the app
Recommend to use `python run.py` to run the app in development.  
! Do not use the flask run command to start the application; instead, use python run.py. !