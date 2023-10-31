# taskizy-api
API for Taskizy Web Application

Tech Stack used:
<br/>
[Django Rest Framework](https://www.django-rest-framework.org/)
<br/>
[Djoser (for user authentication)](https://djoser.readthedocs.io/en/latest/index.html)
<br/>
[Simple JWT (for token authentication)](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/#)
<br/>
[PostgreSQL](https://www.postgresql.org/ftp/pgadmin/pgadmin4/v7.6/windows/)

This API was deployed on [Railway](https://railway.app/)

Clone this repository
```
https://github.com/paofrencillo/taskizy-api.git
```

Go to the working directory and run this command (Bash/Git Bash)
```
python -m venv venv && source venv/Scripts/activate && pip install -r requirements.txt
```

To deactivate virtual environment(venv) run this
```
deactivate
```

This repository has 3 branches
<br/>
```
|- main # used by railway app for deploying this app
|- deployment
|- production
```

!!! Note: production and main/deployment branches used different environmental variables upon using this API

### Deployment

- Create a railway.json file on the working directory and paste this block of code
```
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd taskizy && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn taskizy.wsgi",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```
- Run github commands to add, commit, and push changes
- Go to railway dashboard and create a new github template
- Select this [repository](https://github.com/paofrencillo/taskizy-api)
- When finished successfully, create a new PostgreSQL template
- Copy variables (environmental variables) of the PostgreSQL template and paste it on the variables of the github template

