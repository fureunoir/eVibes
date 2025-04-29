import os
import threading
import time

import redis
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OperationalError
from psycopg2 import connect
from redis.exceptions import ConnectionError  # noqa: A004


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Waiting for services...")

        def wait_for_db():
            db_up = False
            while not db_up:
                try:
                    conn = connect(
                        dbname=os.environ.get("POSTGRES_DB"),
                        user=os.environ.get("POSTGRES_USER"),
                        password=os.environ.get("POSTGRES_PASSWORD"),
                        host=os.environ.get("DB_HOST", "database"),
                    )
                    conn.close()
                    db_up = True
                except (OperationalError, Psycopg2OperationalError):
                    self.stdout.write("Database unavailable, waiting 1 second...")
                    time.sleep(1)
            self.stdout.write(self.style.SUCCESS("Database available!"))

        def wait_for_redis():
            redis_up = False
            while not redis_up:
                try:
                    connection = redis.StrictRedis(
                        host=os.environ.get("REDIS_HOST", "redis"),
                        port=int(os.environ.get("REDIS_PORT", 6379)),
                        db=int(os.environ.get("REDIS_DB", 0)),
                        password=os.environ.get("REDIS_PASSWORD", None),
                        socket_timeout=5,
                        retry_on_timeout=True,
                    )
                    connection.ping()
                    redis_up = True
                except ConnectionError:
                    self.stdout.write("Redis unavailable, waiting 1 second...")
                    time.sleep(1)
            self.stdout.write(self.style.SUCCESS("Redis available!"))

        # Create and start threads for database and Redis
        db_thread = threading.Thread(target=wait_for_db)
        redis_thread = threading.Thread(target=wait_for_redis)

        db_thread.start()
        redis_thread.start()

        # Wait for both threads to complete
        db_thread.join()
        redis_thread.join()

        self.stdout.write(self.style.SUCCESS("All services are available!"))
