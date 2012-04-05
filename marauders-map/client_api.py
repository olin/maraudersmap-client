import requests
import json
import urllib

from configuration import Settings

'''class User(object):
    def __init__(self, response_dict):
        pass



    @property
    def username(self):
        """

        """
        return self.d['username']

    def __get_item__(self, item):
        return self.
        '''

# returns an array of users that match a given criterion **crit
# @param(**crit): the criterions. The ** will make crit a dictionary of the
#   keyword arguments.

def get_users(**crit):
    r = requests.get(
        '%s/users/?%s' % (Settings.SERVER_ADDRESS, urllib.urlencode(crit)))
    return json.loads(r.text)['users']

# returns a particular user with the given username

def get_user(username):
    r = requests.get(
        '%s/users/%s' % (Settings.SERVER_ADDRESS,username))
    return json.loads(r.text)['user']

def put_user(username, **kargs):
    kargs['username'] = username
    r = requests.put(
        '%s/users/%s' % (Settings.SERVER_ADDRESS, username), data=kargs)
    return json.loads(r.text)['user']

def patch_user(username, **kargs):
    patch = [{"replace": "/" + k, "value": v} for k, v in kargs.items()]
    r = requests.patch(
        '%s/users/%s' % (Settings.SERVER_ADDRESS, username),
        data=json.dumps(patch),
        headers={"content-type": "application/json"})
    return json.loads(r.text)['user']

def delete_user(username):
    r = requests.delete(
        '%s/users/%s' % (Settings.SERVER_ADDRESS, username))
    return r.text

# Places

def get_places(**crit):
    r = requests.get(
        '%s/places/?%s' % (Settings.SERVER_ADDRESS, urllib.urlencode(crit)))
    return json.loads(r.text)['places']

def get_place(identifier):
    r = requests.get(
        '%s/places/%s' % (Settings.SERVER_ADDRESS, identifier))
    return json.loads(r.text)['place']

def post_place(**kargs):
    r = requests.post(
        '%s/places/' % Settings.SERVER_ADDRESS, data=kargs)
    return json.loads(r.text)['place']

def patch_place(identifier, **kargs):
    patch = [{"replace": "/" + k, "value": v} for k, v in kargs.items()]
    r = requests.patch(
        '%s/places/%s' % (Settings.SERVER_ADDRESS, identifier),
        data=json.dumps(patch),
        headers={"content-type": "application/json"})
    return json.loads(r.text)['place']

def delete_place(identifier):
    r = requests.delete(
        '%s/places/%s' % (Settings.SERVER_ADDRESS, identifier))
    return r.text

# Binds

def get_binds(**crit):
    r = requests.get(
        '%s/binds/?%s' % (Settings.SERVER_ADDRESS, urllib.urlencode(crit)))
    return json.loads(r.text)['binds']

def get_bind(identifier):
    r = requests.get(
            '%s/binds/%s' % (Settings.SERVER_ADDRESS, identifier))
    return json.loads(r.text)['bind']

def post_bind(**kargs):
    signals = kargs.get('signals', {})
    if kargs.has_key('signals'):
        del kargs['signals']
    for k, v in signals.items():
        kargs['signals[%s]' % k] = v
    r = requests.post(
        '%s/binds/' % Settings.SERVER_ADDRESS, data=kargs)
    print r.text
    return json.loads(r.text)['bind']

def delete_bind(identifier):
    r = requests.delete(
            '%s/binds/%s' % (Settings.SERVER_ADDRESS, identifier))
    return r.text

# Positions

def get_positions(**crit):
    r = requests.get(
        '%s/positions/?%s' %
        (Settings.SERVER_ADDRESS, urllib.urlencode(crit)))
    return json.loads(r.text)['positions']

def get_position(identifier):
    r = requests.get(
        '%s/positions/%s' % (Settings.SERVER_ADDRESS, identifier))
    return json.loads(r.text)['position']

def post_position(**kargs):
    r = requests.post(
            '%s/positions/' % Settings.SERVER_ADDRESS, data=kargs)
    return json.loads(r.text)['position']

def delete_position(identifier):
    r = requests.delete(
        '%s/positions/%s' % (Settings.SERVER_ADDRESS, identifier))
    return r.text

# Test suite

Settings.init()

print "USERS:"
print get_users()
put_user('jceipek', alias='Julian Ceipek')
print get_user('jceipek')
delete_user('jceipek')
patch_user('tryan', alias='Timmmmmmmy')
print get_users()
patch_user('tryan', alias='Tim Ryan')
print

print "PLACES:"
print get_places()
place = post_place(name='Computer Lab', floor='MHLL', alias='Den of Theives')
patch_place(place['identifier'], alias='Compy 386')
print get_place(place['identifier'])
delete_place(place['identifier'])
print get_places()
print

print "BINDS:"
print get_binds()
bind = post_bind(username='tryan', place=get_places()[0]['id'], signals={'AA:AA:AA:AA:AA:AA': 100}, x=50, y=50)
print get_bind(bind['identifier'])
delete_bind(bind['identifier'])
print

print "POSITIONS:"
print get_positions()
pos = post_position(username='tryan', bind=get_binds()[0]['id'])
print get_position(pos['identifier'])
delete_position(pos['identifier'])
print
