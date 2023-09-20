# Example API

## Template Guide

### Cloning

```bash
$ git clone https://github.com/ixdlabs/django-api-template
```

### Intellij IDEA Setup

Follow the below steps to set up the project in Intellij IDEA. (Tested on Intellij IDEA 2023.2.1)

1. Go to `Project Structure > Project` and change the project name and set the correct SDK. (Create a venv/conda
   environment)
2. In `Project Structure > Modules` select `django-api-template` and set its name to correct project name.

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

Afterward, try running the project. The default url for the dashboard
is [http://127.0.0.1:8001/](http://127.0.0.1:8000/)

```bash
$ python manage.py runserver
```

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

#### Django and Core Libraries

| Package            | Purpose                                                                                             |
|--------------------|-----------------------------------------------------------------------------------------------------|
| django             | Web framework for building the application and its core functionalities.                            |
| django-environ     | Simplifies handling environment variables and settings configuration.                               |
| django-model-utils | Provides useful utilities for working with Django models. Used mainly for UUID and Timestamp models |
| django-filter      | Enables easy and customizable filtering of querysets in Django.                                     |

Following packages are installed not for direct usage, but as feature enhancements for the above packages.

- psycopg2-binary (For postgres database)
- Pillow (For image processing)
- argon2-cffi (For password hashing)
- gunicorn (For production deployment)

#### Django REST Framework and Authentication

| Package                       | Purpose                                                              |
|-------------------------------|----------------------------------------------------------------------|
| djangorestframework           | A powerful toolkit for building Web APIs in Django.                  |
| django-cors-headers           | Adds Cross-Origin Resource Sharing (CORS) headers support.           |
| drf-spectacular               | Simplifies the generation of API documentation for DRF.              |
| drf-standardized-errors       | Standardized error responses for Django REST Framework APIs.         |
| dj-rest-auth                  | Adds authentication views and serializers for Django REST Framework. |
| djangorestframework-simplejwt | Provides JSON Web Token (JWT) authentication support for DRF.        |

#### Django Admin

| Package                | Purpose                                               |
|------------------------|-------------------------------------------------------|
| django-admin-interface | A modern and customizable admin interface for Django. |
| django-import-export   | Adds import and export functionality to Django admin. |

#### Third-Party Integrations

| Package                    | Purpose                                                                         |
|----------------------------|---------------------------------------------------------------------------------|
| django-anymail             | Integrates various transactional email service providers with Django.           |
| sentry-sdk                 | Integrates Sentry for real-time error tracking and monitoring.                  |
| django-constance[database] | Allows dynamic Django settings using the admin interface or configuration file. |
| django-storages[boto3]     | Enables the use of Amazon S3 or other storage backends with Django.             |

#### Testing and Code Quality

| Package    | Purpose                                                                   |
|------------|---------------------------------------------------------------------------|
| pre-commit | A framework for managing and maintaining multi-language pre-commit hooks. |
| mypy       | A static type checker for Python, used for type checking the codebase.    |

#### Debugging and Development Tools

| Package              | Purpose                                                           |
|----------------------|-------------------------------------------------------------------|
| django-debug-toolbar | A set of panels displaying various debug information for Django.  |
| django-extensions    | Adds various developer-friendly features to the Django framework. |

Additionally, the following packages are installed for type stubs.

- djangorestframework-stubs
- django-stubs
- types-python-dateutil
- types-requests

#### Dependency Management and Upgrades

| Package      | Purpose                                                         |
|--------------|-----------------------------------------------------------------|
| pip-upgrader | Facilitates upgrading Python packages to their latest versions. |
