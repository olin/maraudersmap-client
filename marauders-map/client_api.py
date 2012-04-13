import requests
import json
import urllib
from copy import copy
import webbrowser

from configuration import Settings

class _SendableObject(object):
    def __init__(self, init, attrs):
        super(_SendableObject, self).__setattr__('_attrs', attrs)
        super(_SendableObject, self).__setattr__('_d', init)

    def __setattr__(self, key, value):
        if key in self._attrs:
            self._d[key] = value
            #super(_SendableObject, self).__setattr__(key, value)
        else:
            raise KeyError(
                "%s does not support setting '%s'" %
                (self.__class__.__name__, key))

    def __getattr__(self, key):
        if key in self._attrs:
            return getattr(self,'_d')[key]
        raise KeyError(
            "%s does not support setting '%s'" %
            (self.__class__.__name__, key))

    def __repr__(self):
        return "<%s:%s>" % (self.__class__.__name__, self._d)

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

    def __init__(self, **kargs):
        super(User, self).__init__(kargs, {'username', 'alias'})
        for key, value in kargs.iteritems():
            setattr(self, key, value)

        if 'username' not in kargs:
            raise KeyError("username not specified")

    def put(self):
        r = requests.put(
                '%s/users/%s' %
                (Settings.SERVER_ADDRESS, self.username), data=self._d)

class Place(_SendableObject):

    def __init__(self, **kargs):
        super(Place, self).__init__(kargs, {'alias', 'floor', 'name', 'id'})
        for key, value in kargs.iteritems():
            setattr(self, key, value)

    def post(self):
        r = requests.post(
            '%s/places/' % Settings.SERVER_ADDRESS, data=self._d)
        response = json.loads(r.text)['place']
        self.id = response['id']

    def put(self):
        r = requests.put(
            '%s/places/%s' % (Settings.SERVER_ADDRESS, self.id), data=self._d)
        response = json.loads(r.text)['place']

class Bind(_SendableObject):

    def __init__(self, **kargs):
        super(Bind, self).__init__(kargs, {'username', 'signals', 'place', 'x', 'y', 'id'})
        for key, value in kargs.iteritems():
            setattr(self, key, value)

    def post(self):

        upload_dict = copy(self._d)
        if 'signals' in self._d:
            del upload_dict['signals']

        for key, value in self._d.get('signals', dict()).iteritems():
            upload_dict['signals[%s]' % key] = value

        place_id = upload_dict['place'].id
        del upload_dict['place']
        upload_dict['place'] = place_id

        # Now upload_dict is the same as _d, but with the 'signals' key
        # replaced by keys of the form 'signals[MAC_ADDRESS]'

        r = requests.post(
            '%s/binds/' % Settings.SERVER_ADDRESS, data=upload_dict)
        print r.text
        response = json.loads(r.text)['bind']
        self.id = response['id']

class Position(_SendableObject):
    """
    To tell the server where a user is, do the following::
        Position(username='TheUsername', bind=likeliest_bind).put()
    """
    def __init__(self, **kargs):
        super(Position, self).__init__(kargs, {'username', 'bind', 'id'})
        for key, value in kargs.iteritems():
            setattr(self, key, value)

    def post(self):
        r = requests.post(
                '%s/positions/' % Settings.SERVER_ADDRESS, data=self._d)
        response = json.loads(r.text)['position']
        self.id = response['id']

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

def delete_user(username):
    r = requests.delete(
        '%s/users/%s' % (Settings.SERVER_ADDRESS, username))
    return r.text

# Places

def get_places(**crit):
    r = requests.get(
        '%s/places/?%s' % (Settings.SERVER_ADDRESS, urllib.urlencode(crit)))
    return [Place(**place_dict) for place_dict in json.loads(r.text)['places']]

def get_place(identifier):
    r = requests.get(
        '%s/places/%s' % (Settings.SERVER_ADDRESS, identifier))
    place_dict = json.loads(r.text)['place']
    return Place(**place_dict)

def delete_place(identifier):
    r = requests.delete(
        '%s/places/%s' % (Settings.SERVER_ADDRESS, identifier))
    return r.text

# Binds

def get_binds(**crit):
    """Get binds that match a set of criteria.
    For example, to get the binds nearest to the current user's location::
       signals = signal_strength.get_avg_signals_dict()
       nearest_binds = get_binds(nearest=signals)
    """
    upload_dict = copy(crit)
    if 'nearest' in crit:
        del upload_dict['nearest']

    if 'signals' in crit:
        del upload_dict['signals']

    for key, value in crit.get('signals', dict()).iteritems():
        upload_dict['signals[%s]' % key] = value

    # Now upload_dict is the same as crit, but with the 'signals' key
    # replaced by keys of the form 'signals[MAC_ADDRESS]'

    for key, value in crit.get('nearest', dict()).iteritems():
        upload_dict['nearest[%s]' % key] = value

    # Now upload_dict is the same as before, but with the 'nearest' key
    # replaced by keys of the form 'nearest[MAC_ADDRESS]'

    r = requests.get(
        '%s/binds/?%s' % (Settings.SERVER_ADDRESS, urllib.urlencode(upload_dict)))
    return [Bind(**bind_dict) for bind_dict in json.loads(r.text)['binds']]

def get_bind(identifier):
    r = requests.get(
            '%s/binds/%s' % (Settings.SERVER_ADDRESS, identifier))
    bind_dict = json.loads(r.text)['bind']
    return Bind(**bind_dict)

def delete_bind(identifier):
    r = requests.delete(
            '%s/binds/%s' % (Settings.SERVER_ADDRESS, identifier))
    return r.text

# Positions

def get_positions(**crit):
    r = requests.get(
        '%s/positions/?%s' %
        (Settings.SERVER_ADDRESS, urllib.urlencode(crit)))
    return [Position(**position_dict) for position_dict in json.loads(r.text)['positions']]

def get_position(identifier):
    r = requests.get(
        '%s/positions/%s' % (Settings.SERVER_ADDRESS, identifier))
    position_dict = json.loads(r.text)['position']
    return Position(**position_dict)



def delete_position(identifier):
    r = requests.delete(
        '%s/positions/%s' % (Settings.SERVER_ADDRESS, identifier))
    return r.text

def open_map():
    """Opens the Marauder's Map user interface in the default web browser.

    """
    webbrowser.open(Settings.WEB_ADDRESS)

if __name__ == '__main__':

    # Test suite

    Settings.init()

    print "USERS:"
    print get_users()
    User(username='jceipek', alias='Julian Ceipek').put()
    print get_user('jceipek')
    delete_user('jceipek')
    print get_users()
    print

    print "PLACES:"
    print get_places()
    place = Place(name='Computer Lab', floor='MHLL', alias='Den of Theives')
    place.put()
    print get_place(place.id)
    delete_place(place.id)
    print get_places()
    print

    print "BINDS:"
    print get_binds()
    #XXX: Looks like this is not working:
    bind = Bind(username='tryan', place=get_places()[0].id, signals={'AA:AA:AA:AA:AA:AA': 100}, x=50, y=50)
    bind.put()
    print get_bind(bind.id)
    delete_bind(bind.id)
    print

    print "POSITIONS:"
    print get_positions()
    pos = Position(username='tryan', bind=get_binds()[0].id)
    pos.put()
    print get_position(pos.id)
    delete_position(pos.id)
    print
