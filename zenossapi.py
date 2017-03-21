# Zenoss-4.x JSON API Example (python)
#
# To quickly explore, execute 'python -i api_example.py'
#
# >>> z = ZenossAPIExample()
# >>> events = z.get_events()
# etc.

import requests
import json
import urllib
import urllib2
import pprint
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

input = open('C:\Users\kamalkant.singhal\PycharmProjects\PythonRepo\Test\zenoss-api.conf','r')
CONF = json.load(input)

ZENOSS_INSTANCE = CONF['url']
ZENOSS_USERNAME = CONF['username']
ZENOSS_PASSWORD = CONF['password']

ROUTERS = { 'MessagingRouter': 'messaging',
            'EventsRouter': 'evconsole',
            'ProcessRouter': 'process',
            'ServiceRouter': 'service',
            'DeviceRouter': 'device',
            'NetworkRouter': 'network',
            'TemplateRouter': 'template',
            'DetailNavRouter': 'detailnav',
            'ReportRouter': 'report',
            'MibRouter': 'mib',
            'ZenPackRouter': 'zenpack' }

class ZenossAPIConnect():
    def __init__(self, debug=False):
        """
        Initialize the API connection, log in, and store authentication cookie
        """
        # Use the HTTPCookieProcessor as urllib2 does not save cookies by default
        self.urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        if debug: self.urlOpener.add_handler(urllib2.HTTPHandler(debuglevel=1))
        self.reqCount = 1

        # Contruct POST params and submit login.
        loginParams = urllib.urlencode(dict(
                        __ac_name = ZENOSS_USERNAME,
                        __ac_password = ZENOSS_PASSWORD,
                        submitted = 'true',
                        came_from = ZENOSS_INSTANCE + '/zport/dmd'))
        self.urlOpener.open(ZENOSS_INSTANCE + '/zport/acl_users/cookieAuthHelper/login',
                            loginParams)


    def _router_request(self, router, method, data=[]):
        if router not in ROUTERS:
            raise Exception('Router "' + router + '" not available.')

        # Contruct a standard URL request for API calls
        req = urllib2.Request(ZENOSS_INSTANCE + '/zport/dmd/' +
                              ROUTERS[router] + '_router')

        #response = urllib2.urlopen(req, context=ssl._create_unverified_context())

        # NOTE: Content-type MUST be set to 'application/json' for these requests
        req.add_header('Content-type', 'application/json; charset=utf-8')

        # Convert the request parameters into JSON
        reqData = json.dumps([dict(
                    action=router,
                    method=method,
                    data=data,
                    type='rpc',
                    tid=self.reqCount)])

        # Increment the request count ('tid'). More important if sending multiple
        # calls in a single request
        self.reqCount += 1

        # Submit the request and convert the returned JSON to objects
        return json.loads(self.urlOpener.open(req, reqData).read())

    def get_devices(self, deviceClass='/zport/dmd/Devices', deviceName=''):
        return self._router_request('DeviceRouter', 'getDevices',
                                    data=[{'uid': deviceClass,
                                        'params': {'name': deviceName} }])['result']

    def set_production_state(self, uids, prodState, hash):
        data = dict(uids=[uids], prodState=prodState, hashcheck=hash)
        return self._router_request('DeviceRouter', 'setProductionState', [data])

    def get_events(self, device=None, component=None, eventClass=None):
        data = dict(start=0, limit=100, dir='DESC', sort='severity')
        data['params'] = dict(severity=[5,4,3], eventState=[0,1])

        if device: data['params']['device'] = device
        if component: data['params']['component'] = component
        if eventClass: data['params']['eventClass'] = eventClass

        return self._router_request('EventsRouter', 'query', [data])['result']

    def get_device_uids(self, uid):
        data = dict(uid=uid)
        return self._router_request('DeviceRouter', 'getDeviceUids', [data])

    def add_device(self, deviceName, deviceClass, productionState='1000'):
        data = dict(deviceName=deviceName, deviceClass=deviceClass, productionState=productionState)
        return self._router_request('DeviceRouter', 'addDevice', [data])

    def create_event_on_device(self, device, component, severity, summary, evclass='', evclasskey=''):
        if severity not in ('Critical', 'Error', 'Warning', 'Info', 'Debug', 'Clear'):
            raise Exception('Severity "' + severity +'" is not valid.')

        data = dict(device=device, summary=summary, severity=severity,
                    component=component, evclasskey=evclasskey, evclass=evclass)
        return self._router_request('EventsRouter', 'add_event', [data])

    """
    def write_log_to_event(self, evid=None, message=None):
        eventid = dict(evid)
        msg = "This is an test fire"
        data = eventid + msg
        return self._router_request('EventsRouter', 'write_log', data)
    """

z = ZenossAPIConnect()
events = z.get_events()

"""
def myprint(events):
  for k, v in events.iteritems():
    if isinstance(v, dict):
      myprint(v)
    else:
      print "{0} : {1}".format(k, v)

myprint(events)
"""

pprint.pprint(events, width=4)
print type(events)
#print events