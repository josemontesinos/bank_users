from types import MethodType
from django.test.runner import DiscoverRunner
from django.db import connections
from django.conf import settings


def prepare_database(self):
    self.connect()
    self.connection.cursor().execute("""
    CREATE SCHEMA django AUTHORIZATION {user};
    GRANT ALL ON SCHEMA django TO {user};
    """.format(user=settings.DATABASES['default']['USER']))


class PostgresSchemaTestRunner(DiscoverRunner):
    """
    This custom test runner creates and sets up the "django" schema in the PostgreSQL test database
    in order to create the built-in Django tables when running the tests.
    """

    def setup_databases(self, **kwargs):
        for connection_name in connections:
            connection = connections[connection_name]
            connection.prepare_database = MethodType(prepare_database, connection)
        return super().setup_databases(**kwargs)
