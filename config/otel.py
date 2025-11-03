import logging
import os
from logging.config import dictConfig
from typing import Any
from urllib.parse import urlparse

import requests
from django.conf import settings
from opentelemetry._logs import get_logger_provider, set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
from opentelemetry.instrumentation.threading import ThreadingInstrumentor
from opentelemetry.instrumentation.urllib import URLLibInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, set_tracer_provider


def otel_request_instrument_request_hook(span: Span, request: requests.PreparedRequest):
    if span and span.is_recording():
        span.set_attribute("http.target", request.path_url)
        parsed = urlparse(request.url)
        if parsed.hostname is not None:
            span.set_attribute("net.peer.name", parsed.hostname)


def otel_redis_instrument_request_hook(span: Span, instance, args, kwargs):
    if span and span.is_recording():
        if args and args[0] != "GET":
            return  # For security reasons, we will not send SET args
        span.set_attribute("db.redis.args", str(args))
        span.set_attribute("db.redis.kwargs", str(kwargs))


def setup_open_telemetry(service_name: str):
    otel_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otel_endpoint is None:
        return

    # Integrated Open Telemetry Python Libraries
    # https://opentelemetry-python-contrib.readthedocs.io
    DjangoInstrumentor().instrument()
    LoggingInstrumentor().instrument()
    ThreadingInstrumentor().instrument()
    Psycopg2Instrumentor().instrument()
    SQLite3Instrumentor().instrument()
    CeleryInstrumentor().instrument()
    URLLibInstrumentor().instrument()
    URLLib3Instrumentor().instrument()
    RequestsInstrumentor().instrument(request_hook=otel_request_instrument_request_hook)
    RedisInstrumentor().instrument(request_hook=otel_redis_instrument_request_hook)

    # Resource
    resource = Resource.create(
        attributes={
            "service.name": service_name,
            "deployment.environment": os.environ.get("OTEL_DEPLOYMENT_ENVIRONMENT", default="development"),
        }
    )

    # Set tracer provider
    span_exporter = OTLPSpanExporter(endpoint=otel_endpoint)
    span_processor = BatchSpanProcessor(span_exporter)
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(span_processor)
    set_tracer_provider(tracer_provider)

    # Set metric provider
    metric_exporter = OTLPMetricExporter(endpoint=otel_endpoint)
    metric_reader = PeriodicExportingMetricReader(metric_exporter)
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    set_meter_provider(meter_provider)

    # Set logger provider
    log_exporter = OTLPLogExporter(endpoint=otel_endpoint)
    log_processor = BatchLogRecordProcessor(log_exporter)
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(log_processor)
    set_logger_provider(logger_provider)

    # Change loggers to also send to open telemetry
    logging_config: dict[str, Any] = settings.LOGGING
    logging_config["loggers"]["django.db.backends"]["handlers"] = ["otel"]
    logging_config["loggers"]["django_structlog"]["handlers"] = ["otel"]
    logging_config["loggers"]["django_structlog.middlewares"]["handlers"] = ["otel"]
    logging_config["loggers"]["django_structlog.celery"]["handlers"] = ["otel"]
    logging_config["loggers"]["root"]["handlers"] = ["otel"]
    dictConfig(logging_config)


# Fix for https://github.com/open-telemetry/opentelemetry-python/issues/3649
class OtelLogHandler(LoggingHandler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level, get_logger_provider())

    @staticmethod
    def _get_attributes(record: logging.LogRecord):
        attributes = LoggingHandler._get_attributes(record)
        if "_logger" in attributes:
            del attributes["_logger"]  # type: ignore
        return attributes
