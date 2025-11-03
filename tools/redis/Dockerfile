FROM redis:8.0

WORKDIR /app

COPY tools/redis/entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

EXPOSE 6379

ENTRYPOINT ["/app/entrypoint.sh"]
