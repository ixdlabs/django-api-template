# Example API

## Template Guide

### Cloning

```bash
$ git clone https://github.com/ixdlabs/lk-solitrapower-erp-backend
```

### Pre-commit hooks setup

```bash
$ pre-commit install
```

### Intellij IDEA Setup

1. Go to `Project Structure > Project` and set the correct SDK. (Create a venv/conda environment)
2. In `Project Structure > Modules` select `django-api-template` and set its name to correct project name.
3. Go to `Edit Configurations` and Add `Django Server` configuration. Select `Use SDK of Module` as the interpreter.

## Guide

### Python Environment Setup

Use `venv`, `conda` or a similar virtual environment to install the dependencies.

#### venv

Use the following command to create the new environment.

```bash
$ python -m venv .venv
$ source .venv/bin/activate
```

#### Miniconda (Alternative)

Install [Miniconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) to create a new virtual
environment for project dependencies. Then use the following command to create the new environment. You may need to
restart the terminal/command prompt to properly activate the new environment.

```bash
$ conda create -n example python=3.10
$ conda activate example
```

### Install Requirements

After the environment is created and activated, install the necessary dependencies using
the [requirements.txt](requirements.txt) file.

```bash
$ pip install -r requirements.txt
```

Check if following command prints the available command. If the installation is successful, this should not cause an
error.

```bash
$ python manage.py
```

### Postgres Setup (For production)

Install [postgres](https://www.postgresql.org/download/) and setup it according to your OS instructions. Use following
command to login to the `psql` shell.

```bash
$ psql -U postgres
```

Then enter below commands.

```sql
CREATE ROLE db_user WITH LOGIN PASSWORD 'password';
CREATE
DATABASE example_db;
GRANT ALL PRIVILEGES ON DATABASE
example_db TO db_user;
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

Then load the fixtures. (Optional) This will load the initial data for the project.
Dumping fixtures can be done as `python manage.py dumpdata APP.MODEL > apps/APP/fixtures/APP_MODEL.json`.

```bash
$ python manage.py loaddata admin_interface_theme_uswds.json
```

Finally, create the user account. This will be the default admin user for the system. Give a preferred username and
password.

```bash
$ python manage.py superuser --username superadmin --password userpassword
# Or to create interactively
$ python manage.py createsuperuser
```

Afterwards try running the project. The default url for the dashboard
is [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

```bash
$ python manage.py runserver
```

### MailHog Setup

Set `USE_MAILHOG` to `True` and run `MailHog` to capture outgoing emails.
