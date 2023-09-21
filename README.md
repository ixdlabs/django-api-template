# Example API

## Template Guide

### Cloning

```bash
$ git clone https://github.com/ixdlabs/django-api-template
```

### Intellij IDEA Setup

Follow the below steps to set up the project in Intellij IDEA. (Tested on Intellij IDEA 2023.2.1)

1. Rename all occurrences of `django-api-template` to the project name.
2. Rename `django-api-template.iml` to the project name.

## Guide

### Python Environment Setup

You should have python 3.10 or above installed in your system. Use `venv`, `conda` or a similar virtual environment to
install the dependencies.

#### venv

Use the following command to create the new environment.

```bash
$ python -m venv .venv
$ source .venv/bin/activate
```

You can also use the IDE to create the environment.

### Install Requirements

After the environment is created and activated, install the necessary dependencies using
the [requirements.txt](requirements.txt) file. (Make sure you are in the correct virtual environment)

```bash
$ pip install -r requirements.txt
```

Check if following command prints the available command. If the installation is successful, this should not cause an
error.

```bash
$ python manage.py
```

### Pre-commit hooks setup

This project uses [pre-commit](https://pre-commit.com/) hooks to check the code before committing. Install the hooks by
running the following command.

```bash
$ pre-commit install
```

### Postgres Setup (For production only)

> Developers do not need to follow this section. This is only for production deployment/testing as is in production. The
> default dev configuration is for `sqlite3` database which will be automatically created in the project root
> as `sqlite.db`.

Install [postgres](https://www.postgresql.org/download/) and setup it according to your OS instructions. Use following
command to login to the `psql` shell.

```bash
$ psql -U postgres
```

Then enter below commands.

```sql
CREATE ROLE db_user WITH LOGIN PASSWORD 'password';
CREATE DATABASE example_db;
GRANT ALL PRIVILEGES ON DATABASE example_db TO db_user;
\q
```

Then login to `psql` as `db_user` and check if the setup is done correctly. Password should be `password`.

```
psql -U db_user example_db
```

#### Windows specific instructions

1. Install [postgresql](https://www.postgresql.org/) in the local machine and setup correctly. **Do not change default
   port or other settings.** Give a password to `postgres` user when asked.
2. Login to `pgAdmin` using the username and password give in the setup process. From the `Browser` panel,
   select `Server>postgres>Login/Group Roles` and right click and create the role. Give `db_user` as role name and
   give `password` as the password.
3. Then right click `Server>postgres>Databases` and Create new database. Give `example_db` as the database name and
   set `db_user` as the owner.
4. Then try to login to `psql` shell using default port, server, database `example_db` and `db_user` user.

### Django Setup

First run the database migration and create the necessary tables. Make sure you are in the correct virtual
environment. **Whenever there is a database model change, you should re-run this.**

```bash
$ python manage.py migrate
```

Then create the static files required for the project. **You should run this again when you pull from the upstream.**

```bash
$ python manage.py collectstatic
```

Finally, create the user account. This will be the default admin user for the system. Give a preferred username and
password.

```bash
$ python manage.py superuser --username superadmin  --email superadmin@example.com --password userpassword
# Or to create interactively
$ python manage.py createsuperuser
```

Install the default admin themes by running following command.

```bash
$ python manage.py loaddata fixtures/themes.json
```

Afterward, try running the project. The default url for the dashboard
is [http://127.0.0.1:8001/](http://127.0.0.1:8000/)

```bash
$ python manage.py runserver
```

### Celery Setup

The default celery setup is run assuming you have a local rabbitmq server running. (In `localhost:5672`) To run the server along with the celery worker, use the `Run Server + Celery` configuration in the IDE. (This will not run rabbitmq, only the server and celery worker will run)

### MailHog Setup

MailHog is a tool to capture outgoing emails. You can use it to test the email sending functionality. Install MailHog by
following the instructions in the mailhog [repository](https://github.com/mailhog/MailHog).

Set `USE_MAIL_HOG` to `True` and run `MailHog` to capture outgoing emails.

 ```bash
 $ USE_MAIL_HOG=True python manage.py runserver
 ```

Or you may use `Run Server + MailHog` configuration in the IDE. (This will not run MailHog, only the server will run
with `USE_MAIL_HOG=True`)

### Packages

This project uses [Django](https://www.djangoproject.com/) as the web framework. Django is a high-level Python Web
framework that encourages rapid development and clean, pragmatic design.

Slight modifications are made to the default Django project structure to make it more modular and easy to maintain. For
example, the apps are put inside the `apps` directory and the `settings.py` and other configuration files are moved to
the `config` directory.
