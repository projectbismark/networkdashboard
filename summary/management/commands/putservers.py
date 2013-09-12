from django.core.management.base import BaseCommand, CommandError
from networkdashboard.summary.geoip_helper import getLocation
import pygeoip
import psycopg2
import json
from networkdashboard.summary.models import *
from django.conf import settings
from time import gmtime, strftime
from django.db import transaction, connection

class Command(BaseCommand):
    def handle(self, *args, **options):
        conn_string = "host='" + settings.DATABASES['default']['HOST'] + \
                   "' dbname='" + settings.DATABASES['default']['NAME'] + \
                   "' user='" + settings.DATABASES['default']['USER'] + \
                   "' password='" + settings.DATABASES['default']['PASSWORD'] + "'";
                   
        cursor = connection.cursor()
        cursor.execute("INSERT INTO test VALUES (1);");
        transaction.commit_unless_managed()
