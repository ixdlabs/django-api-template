# Django API Template

## Cloning

```bash
$ git clone https://github.com/ixdlabs/django-api-template
```

## Environment Setup

You should have python 3.11 or above installed in your system. Use `venv` to install the dependencies.

### venv

Use the following command to create the new environment.

```bash
$ python -m venv .venv
$ source .venv/bin/activate
# Or in Windows
$ .venv\Scripts\activate
```

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

### Environment Variables Configuration

Some operations in the project rely on environment variables. These are listed in the `.env.example` file. To configure them, copy this file and rename it to `.env`. The Django project automatically loads variables from this file, allowing you to set environment-specific values conveniently.

## Formatting and Linting

This project uses [pre-commit](https://pre-commit.com/) hooks to check the code before committing. Install the hooks by
running the following command.

```bash
$ pre-commit install
```

For linting, this project uses [mypy](http://mypy-lang.org/). You can run the linter using the following command.

```bash
$ mypy .
```

## Testing

This project includes a testing and coverage setup using Django's built-in test framework and coverage.py.

To run all the tests:

```bash
$ python manage.py test
```

To run tests with coverage:

```bash
$ coverage run --source='.' manage.py test
```

To generate HTML coverage report:

```bash
$ coverage html
```

and the coverage report will be available at: `htmlcov/index.html`

## Database Setup

This project uses `sqlite3` as the default database for development. It will automatically create a `sqlite.db` file in the project root.
This was chosen for simplicity and ease of use during development. You can start the project without any additional database setup.

If you want to emulate the production environment, you can use `postgres` as the database. Follow the instructions below to set up the database.

### Postgres (Production Setup)

Install [postgres](https://www.postgresql.org/download/) and setup it according to your OS instructions. Use following
command to login to the `psql` shell.

```bash
$ psql -U postgres
```

Then enter below commands.

```sql
CREATE ROLE db_user WITH LOGIN PASSWORD 'password';
CREATE DATABASE django_api_template_db;
GRANT ALL PRIVILEGES ON DATABASE django_api_template_db TO db_user;
\q
```

Then login to `psql` as `db_user` and check if the setup is done correctly. Password should be `password`.

```bash
$ psql -U db_user django_api_template_db
```

Remember to set the `DATABASE_URL` environment variable.

```
DATABASE_URL=postgres://db_user:password@localhost:5432/django_api_template_db
```

## Django Setup

First run the database migration and create the necessary tables. Make sure you are in the correct virtual
environment. **Whenever there is a database model change, you should re-run this.**

```bash
$ python manage.py migrate
```

Then create the static files required for the project. **You should run this again when you pull from the upstream.**

```bash
$ python manage.py collectstatic
```

Then compile translation message files. Run this whenever you add/update translations or pull new locale files.

```bash
$ python manage.py compilemessages
```

> Note: Install gettext if missing
>
> - Ubuntu/Debian: `sudo apt-get install gettext`
> - macOS: `brew install gettext && brew link --force gettext`
> - Windows (Chocolatey): `choco install gettext`

Finally, create the user account. This will be the default admin user for the system. Give a preferred username and
password.

```bash
# This will create the first super admin (nothing will happen if there is one already)
$ python manage.py superuser --username superadmin  --email superadmin@example.com --password userpassword
# Or to create interactively
$ python manage.py createsuperuser
```

Afterward, try running the project. The default url for the dashboard
is [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

```bash
$ python manage.py runserver
```

### Packages

This project uses [Django](https://www.djangoproject.com/) as the web framework. Django is a high-level Python Web
framework that encourages rapid development and clean, pragmatic design.

Slight modifications are made to the default Django project structure to make it more modular and easy to maintain. For
example, the apps are put inside the `apps` directory and the `settings.py` and other configuration files are moved to
the `config` directory.

## Additional Tooling

### RabbitMQ

This project uses [RabbitMQ](https://www.rabbitmq.com/) as the message broker for Celery, caching, and other asynchronous tasks. You can run RabbitMQ using Docker with the following commands parallel to the Django server.

```bash
$ cd tools/rabbitmq
$ docker build -t rabbitmq .
$ docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq
```

You can access the RabbitMQ management interface at [http://localhost:15672/](http://localhost:15672/) with the default username and password as `guest` and `guest`.

### Redis

This project uses [Redis](https://redis.io/) for caching and background task queuing.

To run Redis locally with authentication and optional ACL (username + password) support:

```bash
$ cd tools/redis
$ docker build -t redis .
$ docker run -d --name redis -p 6379:6379 -e REDIS_PASSWORD=password redis
```

If redis is not setup, cache will default to `django.core.cache.backends.locmem.LocMemCache`.

### Mailpit

Mailpit is a tool to capture outgoing emails. You can use it to test the email sending functionality. Install Mailpit using Docker with the following commands parallel to the Django server.

```bash
$ cd tools/mailpit
$ docker build -t mailpit .
$ docker run -d --name mailpit -p 8025:8025 -p 1025:1025 mailpit
```

You can access the Mailpit interface at [http://localhost:8025/](http://localhost:8025/) to view the captured emails.

For the project to use Mailpit, you need to set the `USE_MAILCAPTURE` environment variable to `True` in the `.env` file. This will enable the email capture functionality in the project.

## Celery Setup

This project uses [Celery](https://docs.celeryproject.org/en/stable/) for handling asynchronous tasks. Celery is a distributed task queue that allows you to run tasks in the background, making your application more responsive and efficient. As the broker, it uses RabbitMQ, which is set up in the previous section.

For the Celery worker to run, you also need to set the `CELERY_BROKER_URL` environment variable in the `.env` file. The default value is set to `amqp://guest:guest@localhost:5672`, which is the RabbitMQ setup we created earlier.

### Running Celery Worker (Development)

Celery worker can be run with the following command.

```bash
$ celery -A config worker -l info # Celery worker - handles the tasks
$ celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler  # Celery beat - schedules the periodic tasks
```

### Disable Celery

If you prefer not to use Celery—such as during development—you can disable it by setting the following environment variable:

```
USE_CELERY=False
```

When this is set, you do not need to run the Celery workers or set up RabbitMQ. However, note that scheduled tasks and asynchronous background jobs will not function in this mode. This configuration is intended only for development or testing, not for production use.

## Docker Compose (Production Setup)

You can start the server in a production-ready configuration using Docker Compose. Ensure Docker and Docker Compose are installed on your system beforehand.

From the project root directory, run:

```bash
$ docker-compose up --build
```

This command will build the images and start all necessary services (e.g., web, worker, beat, RabbitMQ, PostgreSQL).

## VS Code

Using the `launch.json` included with this project, you can either run each component separately or run all via the Run and Debug option of `Start All`.

Following settings are recommended to put in your `settings.json`.

```json
{
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "black-formatter.args": ["--line-length=120"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/.mypy_cache": true,
    "**/.venv": true
  },

  "python.analysis.autoImportCompletions": true,
  "python.analysis.indexing": true,
  "python.analysis.packageIndexDepths": [
    {
      "name": "django",
      "depth": 10,
      "includeAllSymbols": true
    },
    {
      "name": "rest_framework",
      "depth": 10,
      "includeAllSymbols": true
    },
    {
      "name": "drf_spectacular",
      "depth": 5,
      "includeAllSymbols": true
    },
    {
      "name": "unfold",
      "depth": 10,
      "includeAllSymbols": true
    }
  ]
}
```

Additionally, to make sure unit tests are discovered properly by VS Code following configurations are needed in settings.json file in the project level. This file is commited in the repo.

```json
{
  "python.testing.unittestArgs": ["-p", "test_*.py"],
  "python.testing.pytestEnabled": false,
  "python.testing.unittestEnabled": true
}
```

Furthermore, in `.env` file, add the following:

```bash
MANAGE_PY_PATH=manage.py
```

## Localization

To add localization support, refer to the
[official Django localization guide](https://docs.djangoproject.com/en/stable/topics/i18n/translation/).

To add Sinhala translations (as an example), run the following command:

```bash
$ python manage.py makemessages -l si
```

This will create .po files under `locale/si/LC_MESSAGES/`.
Edit these files to provide translations for your strings.

### Translating third-party packages

If you need to override translations for external packages (e.g., `rest_framework`, etc.):

1. Create a new app under apps/i18n/ named after the package, e.g.: `apps/i18n/rest_framework_locale/`.
2. Inside this app, add a locale/ directory and copy the .po file from the original package: `apps/i18n/rest_framework_locale/locale/si/LC_MESSAGES/django.po`
3. Modify the translations as needed.
4. Add this app to `I18N_OVERRIDE_APPS` to ensure your overrides take precedence.
5. Don’t forget to compile translations after editing.

## Required Scheduled Tasks

To enable full functionality of the system, the following scheduled tasks must be configured via the Django Admin panel (under Scheduled Tasks). Each task includes a description and its recommended schedule.

| **Task**         | **Details**                                                                                                                                                     |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Example Task** | - **Path**: `apps.example.tasks.task`<br> - **Description**: Example task.<br> - **Schedule**: Monthly on the 1st (Crontab: `0 0 1 * *`)<br> - **Args**: _None_ |

## OpenTelemetry Integration

This project uses [OpenTelemetry](https://opentelemetry.io/) for observability. It is recommended to use [SigNoz](https://signoz.io/) as the OpenTelemetry backend, though any compatible backend will work.

### Configuration

To enable telemetry, set the environment variable `OTEL_EXPORTER_OTLP_ENDPOINT` to point to your OpenTelemetry backend (e.g., `http://127.0.0.1:4317` for gRPC, or `http://127.0.0.1:4318` for HTTP). This endpoint should be reachable from your application container or host.

> **Note:** When using Docker Compose, the default configuration sets `OTEL_EXPORTER_OTLP_ENDPOINT` to the host network's port `4317`.

### Running the Application with OpenTelemetry

Ensure that all relevant environment variables (e.g., `OTEL_EXPORTER_OTLP_ENDPOINT`) are set before starting the application.

```bash
# Start the development server with OpenTelemetry enabled
python manage.py runserver --noreload

# Start the production server using Gunicorn
gunicorn --config tools/infra/gunicorn.conf.py config.wsgi:application

# Start using Docker Compose (assumes backend is running at localhost:4317)
docker-compose up --build
```
