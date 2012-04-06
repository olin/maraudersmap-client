import requests
import json
import urllib

from configuration import Settings

class _SendableObject(object):
    def __init__(self, init, attrs):
        super(_SendableObject, self).__setattr__('_attrs', attrs)
        super(_SendableObject, self).__setattr__('_d', init)

    def __setattr__(self, key, value):
        if key == '_attrs' or key == '_d':
            super(_SendableObject, self).__setattr__(key, value)
        elif key in self._attrs:
            print dir(super(_SendableObject, self))
            self._d[key] = value
            #super(_SendableObject, self).__setattr__(key, value)
        else:
            raise KeyError(
                "%s does not support setting '%s'" %
                (self.__class__.__name__, key))

    def __getattr__(self, key):
        if key == '_attrs' or key == '_d':
            print dir(self)
            return getattr(super(_SendableObject, self), key)
        elif key in self._attrs:
            return super(_SendableObject, self).__getattr__('_d')[key]
        raise KeyError(
            "%s does not support setting '%s'" %
            (self.__class__.__name__, key))

class User(_SendableObject):
    """An object that represents a user that can be pulled from and pushed to
    the server.

    Note: The parameters are all keyword arguments.
    For example: `User(username='jceipek', alias='Julian Ceipek')`

    :param username: (required) Unique username (i.e. jceipek)
    :type username: str

    :param alias: (optional) A more readable version of the username
    :type alias: str
    """
    _attrs = {'username', 'alias'}

    def __init__(self, **kargs):

        for key, value in kargs.iteritems():
            self.__setattr__(key, value)

        if 'username' not in kargs:
            raise KeyError("username not specified")

    def put(self):
        r = requests.put(
                '%s/users/%s' %
                (Settings.SERVER_ADDRESS, self.username), data=self._d)

class Place(_SendableObject):

    _attrs = {'alias', 'floor', 'name', 'id'}

    def __init__(self, **kargs):

        for key, value in kargs.iteritems():
            self[key] = value

    def put(self):
        r = requests.post(
            '%s/places/' % Settings.SERVER_ADDRESS, data=self._d)
        return json.loads(r.text)['place']

class Bind(_SendableObject):
    _attrs = {'username', 'signals', 'place', 'x', 'y', 'id'}
    def __init__(self, **kargs):

        for key, value in kargs.iteritems():
            self[key] = value

class Position(_SendableObject):
    _attrs = {'username', 'bind', 'id'}
    def __init__(self, **kargs):

        for key, value in kargs.iteritems():
            self[key] = value

# import client_api; a = client_api._SendableObject2({},{'a'}); a.a = 5


# returns an array of users that match a given criterion **crit
# @param(**crit): the criterions. The ** will make crit a dictionary of the
#   keyword arguments.

def get_users(**crit):
    r = requests.get(
        '%s/users/?%s' % (Settings.SERVER_ADDRESS, urllib.urlencode(crit)))
    return [User(**user_dict) for user_dict in json.loads(r.text)['users']]

# returns a particular user with the given username

def get_user(username):
    r = requests.get(
        '%s/users/%s' % (Settings.SERVER_ADDRESS,username))
    user_dict = json.loads(r.text)['user']
    return User(**user_dict)

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
#put_user('jceipek', alias='Julian Ceipek')
User(username='jceipek', alias='Julian Ceipek').put()
print get_user('jceipek')
delete_user('jceipek')
patch_user('tryan', alias='Timmmmmmmy')
print get_users()
patch_user('tryan', alias='Tim Ryan')
print

print "PLACES:"
print get_places()
place = post_place(name='Computer Lab', floor='MHLL', alias='Den of Theives')
patch_place(place['id'], alias='Compy 386')
print get_place(place['id'])
delete_place(place['id'])
print get_places()
print

print "BINDS:"
print get_binds()
bind = post_bind(username='tryan', place=get_places()[0]['id'], signals={'AA:AA:AA:AA:AA:AA': 100}, x=50, y=50)
print get_bind(bind['id'])
delete_bind(bind['id'])
print

print "POSITIONS:"
print get_positions()
pos = post_position(username='tryan', bind=get_binds()[0]['id'])
print get_position(pos['id'])
delete_position(pos['id'])
print
