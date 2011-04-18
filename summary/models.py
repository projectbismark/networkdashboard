# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Apps(models.Model):
    appid = models.IntegerField(primary_key=True)
    subid = models.IntegerField(primary_key=True)
    catid = models.IntegerField()
    app = models.CharField(max_length=60)
    subapp = models.CharField(max_length=90)
    description = models.TextField()
    class Meta:
        db_table = u'APPS'

class ArpLogs(models.Model):
    deviceid = models.CharField(unique=True, max_length=45, blank=True)
    timestamp = models.IntegerField(unique=True, null=True, blank=True)
    macid = models.CharField(max_length=60, blank=True)
    ip = models.IntegerField(unique=True, null=True, blank=True)
    class Meta:
        db_table = u'ARP_LOGS'

class Devices(models.Model):
    deviceid = models.CharField(max_length=45, primary_key=True)
    macid = models.CharField(max_length=60, blank=True)
    type = models.CharField(max_length=60, blank=True)
    os = models.CharField(max_length=30, blank=True)
    version = models.CharField(max_length=30, blank=True)
    class Meta:
        db_table = u'DEVICES'
    def __str__(self):
        return self.deviceid

class DhcpLogs(models.Model):
    deviceid = models.CharField(unique=True, max_length=45, db_column='DEVICEID', blank=True) # Field name made lowercase.
    timestamp = models.IntegerField(unique=True, null=True, db_column='TIMESTAMP', blank=True) # Field name made lowercase.
    action = models.CharField(max_length=60, db_column='ACTION', blank=True) # Field name made lowercase.
    ip = models.IntegerField(unique=True, null=True, db_column='IP', blank=True) # Field name made lowercase.
    macid = models.CharField(max_length=60, db_column='MACID', blank=True) # Field name made lowercase.
    client = models.CharField(max_length=150, db_column='CLIENT', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'DHCP_LOGS'

class Events(models.Model):
    eventid = models.IntegerField(primary_key=True)
    event = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'EVENTS'

class EventLogs(models.Model):
    deviceid = models.CharField(unique=True, max_length=45, blank=True)
    timestamp = models.IntegerField(unique=True, null=True, blank=True)
    eventid = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'EVENT_LOGS'

class Flows(models.Model):
    uid = models.IntegerField(primary_key=True)
    flowid = models.IntegerField(unique=True)
    deviceid = models.CharField(max_length=45)
    srcip = models.IntegerField()
    dstip = models.IntegerField()
    proto = models.IntegerField()
    srcport = models.IntegerField()
    dstport = models.IntegerField()
    uppkts = models.IntegerField()
    dwpkts = models.IntegerField()
    upbytes = models.IntegerField()
    dwbytes = models.IntegerField()
    tsstart = models.FloatField()
    tsend = models.FloatField()
    appid = models.IntegerField()
    class Meta:
        db_table = u'FLOWS'

class Flows17Jul26Oct2010(models.Model):
    uid = models.IntegerField(primary_key=True)
    flowid = models.IntegerField(unique=True)
    deviceid = models.CharField(max_length=45)
    srcip = models.IntegerField()
    dstip = models.IntegerField()
    proto = models.IntegerField()
    srcport = models.IntegerField()
    dstport = models.IntegerField()
    uppkts = models.IntegerField()
    dwpkts = models.IntegerField()
    upbytes = models.IntegerField()
    dwbytes = models.IntegerField()
    tsstart = models.FloatField(unique=True)
    tsend = models.FloatField()
    app = models.CharField(max_length=60)
    class Meta:
        db_table = u'FLOWS_17jul_26oct_2010'

class Flows26Oct7Dec2010(models.Model):
    uid = models.IntegerField(primary_key=True)
    flowid = models.IntegerField(unique=True)
    deviceid = models.CharField(max_length=45)
    srcip = models.IntegerField()
    dstip = models.IntegerField()
    proto = models.IntegerField()
    srcport = models.IntegerField()
    dstport = models.IntegerField()
    uppkts = models.IntegerField()
    dwpkts = models.IntegerField()
    upbytes = models.IntegerField()
    dwbytes = models.IntegerField()
    tsstart = models.IntegerField(unique=True)
    tsend = models.IntegerField()
    app = models.CharField(max_length=60)
    class Meta:
        db_table = u'FLOWS_26oct_7dec_2010'

class FlowsSamples(models.Model):
    uid = models.IntegerField(unique=True)
    uppkts = models.IntegerField()
    dwpkts = models.IntegerField()
    upbytes = models.IntegerField()
    dwbytes = models.IntegerField()
    tsstart = models.FloatField()
    tsend = models.FloatField(unique=True)
    class Meta:
        db_table = u'FLOWS_SAMPLES'

class FlowsSamples17Jul26Oct2010(models.Model):
    uid = models.ForeignKey(Flows17Jul26Oct2010, db_column='uid')
    uppkts = models.IntegerField()
    dwpkts = models.IntegerField()
    upbytes = models.IntegerField()
    dwbytes = models.IntegerField()
    tsstart = models.FloatField()
    tsend = models.FloatField(unique=True)
    class Meta:
        db_table = u'FLOWS_SAMPLES_17jul_26oct_2010'

class FlowsSamples26Oct7Dec2010(models.Model):
    uid = models.ForeignKey(Flows26Oct7Dec2010, db_column='uid')
    uppkts = models.IntegerField()
    dwpkts = models.IntegerField()
    upbytes = models.IntegerField()
    dwbytes = models.IntegerField()
    tsstart = models.IntegerField()
    tsend = models.IntegerField(unique=True)
    class Meta:
        db_table = u'FLOWS_SAMPLES_26oct_7dec_2010'

class FlowsSamplesNewformat(models.Model):
    uid = models.IntegerField(unique=True)
    uppkts = models.IntegerField()
    dwpkts = models.IntegerField()
    upbytes = models.IntegerField()
    dwbytes = models.IntegerField()
    tsstart = models.FloatField()
    tsend = models.FloatField(unique=True)
    class Meta:
        db_table = u'FLOWS_SAMPLES_newformat'

class FlowsNewformat(models.Model):
    uid = models.IntegerField(primary_key=True)
    flowid = models.IntegerField(unique=True)
    deviceid = models.CharField(max_length=45)
    srcip = models.IntegerField()
    dstip = models.IntegerField()
    proto = models.IntegerField()
    srcport = models.IntegerField()
    dstport = models.IntegerField()
    uppkts = models.IntegerField()
    dwpkts = models.IntegerField()
    upbytes = models.IntegerField()
    dwbytes = models.IntegerField()
    tsstart = models.FloatField()
    tsend = models.FloatField()
    appid = models.IntegerField()
    subid = models.IntegerField()
    class Meta:
        db_table = u'FLOWS_newformat'

class Measurements(models.Model):
    id = models.IntegerField(primary_key=True)
    deviceid = models.CharField(max_length=45, blank=True)
    userid = models.IntegerField(null=True, blank=True)
    srcip = models.IntegerField(null=True, blank=True)
    dstip = models.IntegerField(null=True, blank=True)
    timestamp = models.IntegerField(unique=True, null=True, blank=True)
    param = models.CharField(max_length=60, blank=True)
    avg = models.FloatField(null=True, blank=True)
    std = models.FloatField(null=True, blank=True)
    min = models.FloatField(null=True, blank=True)
    max = models.FloatField(null=True, blank=True)
    med = models.FloatField(null=True, blank=True)
    iqr = models.FloatField(null=True, blank=True)
    tool = models.CharField(max_length=60, blank=True)
    class Meta:
        db_table = u'MEASUREMENTS'

class Sla(models.Model):
    slaid = models.IntegerField(primary_key=True)
    isp = models.CharField(max_length=90, blank=True)
    sla = models.CharField(max_length=150, blank=True)
    dl = models.IntegerField(null=True, blank=True)
    ul = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'SLA'

class Traceroutes(models.Model):
    id = models.IntegerField(primary_key=True)
    deviceid = models.CharField(max_length=45, blank=True)
    userid = models.IntegerField(null=True, blank=True)
    srcip = models.IntegerField(null=True, blank=True)
    dstip = models.IntegerField(null=True, blank=True)
    timestamp = models.IntegerField(null=True, blank=True)
    hops = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'TRACEROUTES'

class TracerouteHops(models.Model):
    tid = models.IntegerField(null=True, blank=True)
    id = models.IntegerField(null=True, blank=True,primary_key=True)
    ip = models.IntegerField(null=True, blank=True)
    rtt = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'TRACEROUTE_HOPS'

class Userdevice(models.Model):
    userid = models.IntegerField(null=True, blank=True)
    deviceid = models.CharField(max_length=45, blank=True)
    start = models.IntegerField(null=True, blank=True)
    end = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'USERDEVICE'

class Users(models.Model):
    userid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300, blank=True)
    email = models.CharField(max_length=90, blank=True)
    address = models.CharField(max_length=900, blank=True)
    phone = models.CharField(max_length=60, blank=True)
    class Meta:
        db_table = u'USERS'

class Usersla(models.Model):
    userid = models.IntegerField(null=True, blank=True)
    slaid = models.IntegerField(null=True, blank=True)
    start = models.IntegerField(null=True, blank=True)
    end = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'USERSLA'

class ViewMeasurements(models.Model):
    slaid = models.IntegerField(null=True, blank=True)
    isp = models.CharField(max_length=90, blank=True)
    sla = models.CharField(max_length=150, blank=True)
    sla_start = models.IntegerField(null=True, blank=True)
    sla_end = models.IntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    deviceid = models.CharField(max_length=45, blank=True)
    userid = models.IntegerField(null=True, blank=True)
    srcip = models.IntegerField(null=True, blank=True)
    dstip = models.IntegerField(null=True, blank=True)
    timestamp = models.IntegerField(null=True, blank=True)
    param = models.CharField(max_length=60, blank=True)
    avg = models.FloatField(null=True, blank=True)
    std = models.FloatField(null=True, blank=True)
    min = models.FloatField(null=True, blank=True)
    max = models.FloatField(null=True, blank=True)
    med = models.FloatField(null=True, blank=True)
    iqr = models.FloatField(null=True, blank=True)
    tool = models.CharField(max_length=60, blank=True)
    class Meta:
        db_table = u'VIEW_MEASUREMENTS'

class WifiAssoc(models.Model):
    stationmac = models.CharField(max_length=60, db_column='STATIONMAC', blank=True) # Field name made lowercase.
    firstseen = models.IntegerField(null=True, db_column='FIRSTSEEN', blank=True) # Field name made lowercase.
    lastseen = models.IntegerField(null=True, db_column='LASTSEEN', blank=True) # Field name made lowercase.
    power = models.IntegerField(null=True, db_column='POWER', blank=True) # Field name made lowercase.
    numpkts = models.IntegerField(null=True, db_column='NUMPKTS', blank=True) # Field name made lowercase.
    bssid = models.CharField(max_length=60, db_column='BSSID', blank=True) # Field name made lowercase.
    probedessid = models.CharField(max_length=150, db_column='PROBEDESSID', blank=True) # Field name made lowercase.
    deviceid = models.CharField(max_length=45, db_column='DEVICEID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'WIFI_ASSOC'

class WifiScan(models.Model):
    deviceid = models.CharField(max_length=45, db_column='DEVICEID', blank=True) # Field name made lowercase.
    bssid = models.CharField(max_length=60, db_column='BSSID', blank=True) # Field name made lowercase.
    firstseen = models.IntegerField(null=True, db_column='FIRSTSEEN', blank=True) # Field name made lowercase.
    lastseen = models.IntegerField(null=True, db_column='LASTSEEN', blank=True) # Field name made lowercase.
    channel = models.IntegerField(null=True, db_column='CHANNEL', blank=True) # Field name made lowercase.
    speed = models.IntegerField(null=True, db_column='SPEED', blank=True) # Field name made lowercase.
    privacy = models.CharField(max_length=150, db_column='PRIVACY', blank=True) # Field name made lowercase.
    cipher = models.CharField(max_length=150, db_column='CIPHER', blank=True) # Field name made lowercase.
    auth = models.CharField(max_length=150, db_column='AUTH', blank=True) # Field name made lowercase.
    power = models.IntegerField(null=True, db_column='POWER', blank=True) # Field name made lowercase.
    numbeacons = models.IntegerField(null=True, db_column='NUMBEACONS', blank=True) # Field name made lowercase.
    numiv = models.IntegerField(null=True, db_column='NUMIV', blank=True) # Field name made lowercase.
    idlen = models.IntegerField(null=True, db_column='IDLEN', blank=True) # Field name made lowercase.
    essid = models.CharField(max_length=150, db_column='ESSID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'WIFI_SCAN'

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=240)
    class Meta:
        db_table = u'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group_id = models.IntegerField(unique=True)
    permission_id = models.IntegerField()
    class Meta:
        db_table = u'auth_group_permissions'

class AuthMessage(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    message = models.TextField()
    class Meta:
        db_table = u'auth_message'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    content_type_id = models.IntegerField()
    codename = models.CharField(unique=True, max_length=255)
    class Meta:
        db_table = u'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=90)
    first_name = models.CharField(max_length=90)
    last_name = models.CharField(max_length=90)
    email = models.CharField(max_length=225)
    password = models.CharField(max_length=384)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    is_superuser = models.IntegerField()
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    class Meta:
        db_table = u'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    group_id = models.IntegerField()
    class Meta:
        db_table = u'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    permission_id = models.IntegerField()
    class Meta:
        db_table = u'auth_user_user_permissions'

class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)
    action_time = models.DateTimeField()
    user_id = models.IntegerField()
    content_type_id = models.IntegerField(null=True, blank=True)
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(max_length=600)
    action_flag = models.IntegerField()
    change_message = models.TextField()
    class Meta:
        db_table = u'django_admin_log'

class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300)
    app_label = models.CharField(unique=True, max_length=255)
    model = models.CharField(unique=True, max_length=255)
    class Meta:
        db_table = u'django_content_type'

class DjangoSession(models.Model):
    session_key = models.CharField(max_length=120, primary_key=True)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        db_table = u'django_session'

class DjangoSite(models.Model):
    id = models.IntegerField(primary_key=True)
    domain = models.CharField(max_length=300)
    name = models.CharField(max_length=150)
    class Meta:
        db_table = u'django_site'

