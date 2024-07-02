# 🚀 Time Traveler

![badge for project](https://wakapi.xiaobo.app/api/badge/%e5%b0%8f%e6%b3%a2/interval:any/project:Time_Traveler?label=Wakapi)

### 🌐 Description

This is a web application that helps users plan and manage their travel experiences seamlessly.  
You can try it on [Time Traveler(not yet)](notyeet).

### 🔥 Features
babababa (To be added)

## 🛠 Tech Stack
* Framework: Flask
* Database: MongoDB
* Cache: Redis  
#### 📜 What we use
* Captcha: Cloudflare Turnstile  
* Search: Bing Search API
* OAuth: Google OAuth
* LLM: OpenAI GPT
* Map: Mapbox

## 🚀 Deployment

Before deploying the app, make sure you have all the prerequisites installed and api keys ready.

### 📋 Prerequisites
* Python 3.12
* MongoDB
* Redis
* Docker (optional)
#### 🔑 APIs
* OpenAI (or Azure OpenAI)
* Azure (Bing Search API)
* Cloudflare Turnstile
* Google (OAuth)
* Mapbox

You can deploy the app using Docker or just setup self.
### 🐳 Docker
You can just use docker run, but we recommend to use docker-compose.  
This is an example of docker-compose.yml:
```yaml
services:
  time_traveler:
    image: xiaobocute/time_traveler:latest
    container_name: time_traveler
    restart: always
    environment:
      HOST: "0.0.0.0"
      PORT: 80
      DEBUG: "False"
      SECRET_KEY: ""
      SESSION_TIMEOUT: 604800
      HOST_DOMAIN: ""
      USE_AZURE_OPENAI: "False"
      AZURE_OPENAI_ENDPOINT: ""
      AZURE_OPENAI_API_KEY: ""
      AZURE_OPENAI_API_VERSION: ""
      AZURE_BING_SEARCH_ENDPOINT: ""
      AZURE_BING_SEARCH_API_KEY: ""
      GOOGLE_OAUTH_CLIENT_ID: ""
      GOOGLE_OAUTH_CLIENT_SECRET: ""
      OPENAI_API_KEY: ""
      MAPBOX_ACCESS_TOKEN: ""
      TURNSTILE_SECRET_KEY: ""
      MONGO_URI: ""
      REDIS_URI: ""
    expose:
      - "80"
    networks:
      - webnet
```

### 🛠 Setup
#### 1️⃣ Install requirements
Recommend to use virtual environment for python 3.12.  
All requirements are listed in the `requirements.txt` file. To install them, using `pip install -r requirements.txt` should suffice.
#### 2️⃣ Configure environment variables
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
HOST_DOMAIN=""

# -- Settings --
# If True, the app will use Azure OpenAI API, otherwise it will use OpenAI API.
USE_AZURE_OPENAI=False

# -- AZURE --
AZURE_OPENAI_ENDPOINT=""
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_API_VERSION=""
AZURE_BING_SEARCH_ENDPOINT=""
AZURE_BING_SEARCH_API_KEY=""

# -- Keys --
GOOGLE_OAUTH_CLIENT_ID=""
GOOGLE_OAUTH_CLIENT_SECRET=""
OPENAI_API_KEY=""
MAPBOX_ACCESS_TOKEN=""
TURNSTILE_SECRET_KEY=""

# -- Database --
MONGO_URI=""
REDIS_URI=""

# -- Assistant --
TADE_ID=""
```

#### 3️⃣ Run the app
Use `python run.py` to run the app in development.  
! Do not use the flask run command to start the application; instead, use python run.py. !

## 📜 License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license. 

### 📌 Key Points:

1. **NonCommercial**: You may not use the material for commercial purposes.
2. **ShareAlike**: If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.
3. **Attribution**: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

### 📝 Additional Notes:

- **Technical Modifications**: You are allowed to make necessary technical modifications to the material.
- **No Additional Restrictions**: You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
  
If you want to see the official description of the CC BY-NC-SA 4.0 license, you can visit https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.

### 🚨 Important:

If there is any conflict between the contents of this project and the CC BY-NC-SA 4.0 license, the terms of the CC BY-NC-SA 4.0 license shall prevail. Any interpretations that conflict with the CC BY-NC-SA 4.0 license are invalid unless formally agreed upon by the author in a signed contract.