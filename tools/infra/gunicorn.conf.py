from config.otel import setup_open_telemetry

bind = "0.0.0.0:8000"
workers = 5
timeout = 120


# https://signoz.io/docs/instrumentation/opentelemetry-python/#running-applications-with-gunicorn-uwsgi
def post_fork(server, worker):
    setup_open_telemetry("django-api-template-backend")
