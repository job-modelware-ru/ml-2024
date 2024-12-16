# Analysis module
## Setting up the environment

* Install dependencies
```
pip install -r requirements.txt
```

* Install MongoDB from https://www.mongodb.com/try/download/community

* Create file analysis/.env, for example:
```
MONGODB_IP=127.0.0.1
MONGODB_PORT=27017
DATABASE_NAME=Youtube
SSH_CONNECTION=true
SSH_IP=231.54.123.231
SSH_USERNAME=suser
SSH_PASSWORD=qwerty
```

If ssh connection false, then leave ssh_options blank
