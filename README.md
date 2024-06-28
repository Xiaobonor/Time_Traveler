# Time Traveler

![badge for project](https://wakapi.xiaobo.app/api/badge/%e5%b0%8f%e6%b3%a2/interval:any/project:Time_Traveler?label=Wakapi)

## Description

This is a web application that helps users plan and manage their travel experiences seamlessly.

## Tech Stack 
* Framework: Flask
* Database: MongoDB
* Cache: Redis  
... more to be added

## IMPORTANT
Don't use flask to run the app in production. Use a WSGI server like Gunicorn or uWSGI.

## Deployment
You can deploy the app using Docker or just setup self.
### Docker
We recommend using Docker compose to deploy the app.  
```bash
wait for update!
```

### Setup
#### 1. Install requirements
Recommend to use virtual environment for python 3.12.  
All requirements are listed in the `requirements.txt` file. To install them, using `pip install -r requirements.txt` should suffice.
#### 2. Configure environment variables
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
AZURE_OPENAI_ENDPOINT=""
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_API_VERSION=""

# -- Keys --
GOOGLE_OAUTH_CLIENT_ID=""
GOOGLE_OAUTH_CLIENT_SECRET=""
OPENAI_API_KEY=""
MAPBOX_ACCESS_TOKEN=""

# -- Database --
MONGO_URI=""
REDIS_URI=""
```

#### 3. Run the app
Recommend to use `python run.py` to run the app in development.  
! Do not use the flask run command to start the application; instead, use python run.py. !

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license. 

### Key Points:

1. **NonCommercial**: You may not use the material for commercial purposes.
2. **ShareAlike**: If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.
3. **Attribution**: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

### Additional Notes:

- **Technical Modifications**: You are allowed to make necessary technical modifications to the material.
- **No Additional Restrictions**: You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
  
If you want to see the official description of the CC BY-NC-SA 4.0 license, you can visit https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.

### Important:

If there is any conflict between the contents of this project and the CC BY-NC-SA 4.0 license, the terms of the CC BY-NC-SA 4.0 license shall prevail. Any interpretations that conflict with the CC BY-NC-SA 4.0 license are invalid unless formally agreed upon by the author in a signed contract.