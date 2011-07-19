# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class ArpLogs(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    eventstamp = models.DateTimeField()
    macid = models.TextField() # This field type is a guess.
    ip = models.IPAddressField()
    id = models.TextField(unique=True) # This field type is a guess.
    class Meta:
        db_table = u'arp_logs'

class Devices(models.Model):
    deviceid = models.TextField(primary_key=True) # This field type is a guess.
    name = models.CharField(max_length=255)
    device_type = models.CharField(max_length=20)
    os = models.CharField(max_length=20)
    version = models.CharField(max_length=20)
    active = models.BooleanField()
    last_update = models.DateTimeField()
    class Meta:
        db_table = u'devices'

class DhcpLogs(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    eventstamp = models.DateTimeField()
    dhcp_action = models.CharField(max_length=4)
    ip = models.IPAddressField()
    macid = models.TextField() # This field type is a guess.
    client = models.CharField(max_length=255)
    id = models.TextField(unique=True) # This field type is a guess.
    class Meta:
        db_table = u'dhcp_logs'

class EventLogs(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    eventstamp = models.DateTimeField()
    eventid = models.DecimalField(max_digits=11, decimal_places=-4)
    id = models.TextField(unique=True) # This field type is a guess.
    class Meta:
        db_table = u'event_logs'

class Events(models.Model):
    eventid = models.DecimalField(max_digits=11, decimal_places=-4, primary_key=True)
    event = models.CharField(max_length=50)
    class Meta:
        db_table = u'events'

class Ip(models.Model):
    cip = models.TextField() # This field type is a guess.
    sip = models.IPAddressField()
    id = models.TextField(unique=True) # This field type is a guess.
    class Meta:
        db_table = u'ip'

class MBitrate(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_bitrate'

class MCapacity(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_capacity'

class MDnsdelay(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_dnsdelay'

class MDnsdelayc(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_dnsdelayc'

class MDnsdelaync(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_dnsdelaync'

class MDnsfail(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_dnsfail'

class MDnsfailc(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_dnsfailc'

class MDnsfailnc(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_dnsfailnc'

class MJitter(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_jitter'

class MLmrtt(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_lmrtt'

class MPktloss(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_pktloss'

class MRtt(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_rtt'

class MShaperate(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_shaperate'

class MUlrttdw(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_ulrttdw'

class MUlrttup(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_ulrttup'

class MAggl3Bitrate(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'm_aggl3bitrate'

class PgBuffercache(models.Model):
    bufferid = models.IntegerField()
    relfilenode = models.TextField() # This field type is a guess.
    reltablespace = models.TextField() # This field type is a guess.
    reldatabase = models.TextField() # This field type is a guess.
    relforknumber = models.SmallIntegerField()
    relblocknumber = models.TextField() # This field type is a guess.
    isdirty = models.BooleanField()
    usagecount = models.SmallIntegerField()
    class Meta:
        db_table = u'pg_buffercache'

class Sla(models.Model):
    isp = models.CharField(max_length=30)
    sla = models.CharField(max_length=30)
    dl = models.TextField() # This field type is a guess.
    ul = models.TextField() # This field type is a guess.
    id = models.TextField(primary_key=True) # This field type is a guess.
    class Meta:
        db_table = u'sla'

class Testseries(models.Model):
    shortcode = models.CharField(max_length=4, primary_key=True)
    testname = models.CharField(max_length=40)
    id = models.TextField(unique=True) # This field type is a guess.
    class Meta:
        db_table = u'testseries'

class Traceroutes(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    hops = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    class Meta:
        db_table = u'traceroutes'

class Userdevices(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    startdt = models.DateTimeField()
    enddt = models.DateTimeField()
    testseries = models.TextField() # This field type is a guess.
    userid = models.TextField() # This field type is a guess.
    id = models.TextField(unique=True) # This field type is a guess.
    class Meta:
        db_table = u'userdevices'

class Users(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=80)
    street = models.CharField(max_length=80)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=30)
    postalcode = models.CharField(max_length=30)
    country = models.CharField(max_length=2)
    phone = models.CharField(max_length=20)
    skype = models.CharField(max_length=80)
    sip = models.CharField(max_length=80)
    id = models.TextField(primary_key=True) # This field type is a guess.
    class Meta:
        db_table = u'users'

class Usersla(models.Model):
    startdt = models.DecimalField(max_digits=20, decimal_places=-4)
    enddt = models.DecimalField(max_digits=20, decimal_places=-4)
    userid = models.TextField() # This field type is a guess.
    slaid = models.TextField() # This field type is a guess.
    id = models.TextField(unique=True) # This field type is a guess.
    class Meta:
        db_table = u'usersla'

class WifiAssoc(models.Model):
    stationmac = models.TextField() # This field type is a guess.
    firstseen = models.DecimalField(max_digits=20, decimal_places=-4)
    lastseen = models.DecimalField(max_digits=20, decimal_places=-4)
    power = models.DecimalField(max_digits=11, decimal_places=-4)
    numpkts = models.DecimalField(max_digits=11, decimal_places=-4)
    bssid = models.TextField() # This field type is a guess.
    probedessid = models.CharField(max_length=32)
    deviceid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'wifi_assoc'

class WifiScan(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    bssid = models.TextField() # This field type is a guess.
    firstseen = models.DecimalField(max_digits=20, decimal_places=-4)
    lastseen = models.DecimalField(max_digits=20, decimal_places=-4)
    channel = models.SmallIntegerField()
    speed = models.DecimalField(max_digits=11, decimal_places=-4)
    privacy = models.CharField(max_length=50)
    cipher = models.CharField(max_length=50)
    auth = models.CharField(max_length=50)
    power = models.DecimalField(max_digits=11, decimal_places=-4)
    numbeacons = models.DecimalField(max_digits=11, decimal_places=-4)
    numiv = models.DecimalField(max_digits=11, decimal_places=-4)
    idlen = models.DecimalField(max_digits=11, decimal_places=-4)
    essid = models.CharField(max_length=32)
    class Meta:
        db_table = u'wifi_scan'

class MeasurementsTmpl(models.Model):
    deviceid = models.TextField() # This field type is a guess.
    srcip = models.IPAddressField()
    dstip = models.IPAddressField()
    eventstamp = models.DateTimeField()
    average = models.FloatField()
    std = models.FloatField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    median = models.FloatField()
    iqr = models.FloatField()
    exitstatus = models.IntegerField()
    id = models.TextField(unique=True) # This field type is a guess.
    toolid = models.ForeignKey(Tools, db_column='toolid')
    class Meta:
        db_table = u'measurements_tmpl'

class Tools(models.Model):
    tool = models.CharField(max_length=10)
    version = models.CharField(max_length=10)
    tool_desc = models.CharField(max_length=80)
    id = models.TextField(primary_key=True) # This field type is a guess.
    class Meta:
        db_table = u'tools'

class TracerouteHops(models.Model):
    id = models.ForeignKey(Traceroutes, db_column='id')
    hop = models.SmallIntegerField()
    ip = models.IPAddressField()
    rtt = models.FloatField()
    django_bs = models.TextField(unique=True) # This field type is a guess.
    class Meta:
        db_table = u'traceroute_hops'

