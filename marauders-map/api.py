import urllib

import webbrowser
from configuration import Settings
import signal_strength
from getpass import getuser


class Location(object):
    """An object to represent the combination of a place name and a coordinate.

    :param encoded_name: The server-side representation of the name
        of the place. **Ex:** *WH,in,rm309*
    :type encoded_name: str
    :param coordinate: The x,y,w coordinate of the place.
    :type coordinate: :class:`Coordinate`

    """

    def __init__(self, encoded_name, coordinate):
        self.coordinate = coordinate
        self.encoded_name = encoded_name
        self.__readable_name = self.get_readable_name()

    @property
    def readable_name(self):
        return self.__readable_name

    def get_readable_name(self):
        """Parses the encoded_name and converts it into a
            human-readable string.

        This is useful for menu entries, for example.

        :returns:  str -- the readable name

        .. warning::
            This doesn't work properly; it is from the original code.

        """
        # location strings look like WH,in,rm309
        location = self.encoded_name.replace("OC", "MH")  # Once upon a time,
                                                         # Milas hall was
                                                         # called Olin Center
        # XXX: Should be changed on server, probably

        try:
            building, inside, description = location.split(",")
        except:
            return None

        floor = building[2]
        building = building[0:2]

        if (inside == "in"):
            inside = "inside"
        elif (inside == "out"):
            inside = "outside"
        if (floor == "1"):
            floor = "1st"
        elif (floor == "2"):
            floor = "2nd"
        elif (floor == "3"):
            floor = "3rd"
        elif (floor == "4"):
            floor = "4th"
        elif (floor == "0"):
            floor = "LL"

        if (description.find("rm") != -1 or
            description.find("room") != -1 or
            description.find("Room") != -1 or
            description.find("ROOM") != -1):

            # this has a room
            description = description.replace("rm", "")
            description = description.replace("room", "")
            description = description.replace("Room", "")
            description = description.replace("ROOM", "")

            location = '%s %s%s' % (inside, building, description)
        else:
            if (floor != "LL"):
                location = '%s %s %s floor%s' % \
                (inside, building, floor, description)
            else:
                location = '%s %s (%s) %s' % \
                (inside, building, floor, description)

        self.__readable_name = location

        return location


class Coordinate(object):
    """An optimized way of representing an x,y,w location and (optionally)
    a distance.

    :param x: x coordinate in pixels, on image w
    :type x: int
    :param y: y coordinate in pixels, on image w
    :type y: int
    :param w: There are two images of maps in the original marauder's map.
        This parameter specifies to which map the x,y coordinates
        refer, 1 or 2.
    :param distance: Not entirely sure what this is for...
    :type distance: int
    :type w: int

    .. note::
        It is not possible to add attributes to this object

    """

    __slots__ = ('x', 'y', 'w', 'distance')

    def __init__(self, x, y, w, distance=0):
        self.x = x
        self.y = y
        self.w = w  # Which map the coord refers to (1 or 2)
        self.distance = distance

# XXX: Sketchy global variable to get around server api requirement of
# getting location without posting it

# XXX: Using this method until the server api gets fixed. I know it
# is REALLY BAD - Julian
global last_signal_strength_string
last_signal_strength_string = None


def open_map():
    """Opens the Marauder's Map user interface in the default web browser.

    """
    webbrowser.open(Settings.WEB_ADDRESS)


def send_to_server(strPHPScript, dictParams):
    """Uses urllib to send a dictionary to a PHP script on the server
    specified in configuration.py

    :param strPHPScript: name of the php script to invoke on the server.
        **Ex:** *'update.php'*
    :type strPHPScript: str
    :param dictParams: dictionary of parameters to send to the server.
    :type dictParams: dict

    :returns: a tuple ``(successBOOL, responseSTR/explanation_of_failureSTR)``

    """

    # Construct url with the parameters specified in the dictionary
    strUrl = "%s/%s?%s" % \
    (Settings.SERVER_ADDRESS, strPHPScript, urllib.urlencode(dictParams))

    print strUrl

    try:
        u = urllib.urlopen(strUrl)
        ret = u.read().strip()
        u.close()
    except:
        return False, 'Could not connect to server!'

    #See if successful
    if not ret.startswith('success:'):
        return False, ret
    else:
        return True, ret[len('success:'):]


def __update(username, place_name=None, status=None, refresh=True):
    """Update can tell you where you are or tell the server where you are.

    Update gets a list of potential locations where the user might be.
    If place_name is specified, it will tell the server to display the
    user at the location specified. Otherwise, the map will not be affected.

    :param username: The user name of the user to update
    :type username: str
    :param place_name: Encoded string representing the location to
        post to the server. If this is passed in, the user will
        show up on the map there.
    :type place_name: str
    :param status: We haven't been able to figure out what this is for...
    :type status: str
    :param refresh: If true, the function will recompute the signal
        strength of the nearby access points and send that data rather
        than the last known data.
    :type refresh: bool

    :returns: list of :class:`Location` objects, sorted from most to least
        likely.

    .. note: __update never affects the database on the server.

    """

    #XXX: Using this method until the server api gets fixed. I know it is
    # REALLY BAD - Julian
    global last_signal_strength_string
    if refresh or last_signal_strength_string == None:
        signal_strength_nodes = signal_strength.get_avg_signal_nodes(samples=3,
                                                               tsleep=0.15)
        signal_strength_str = ";".join([str(node) for node in
                                                        signal_strength_nodes])
        last_signal_strength_string = signal_strength_str
    else:
        signal_strength_str = last_signal_strength_string

    dict_send = dict()
    dict_send['username'] = username
    dict_send['data'] = signal_strength_str
    dict_send['platform'] = __getPlatform()

    if place_name:
        dict_send['placename'] = place_name

    if status:
        dict_send['status'] = status

    flag, result = send_to_server('update.php', dict_send)
    if not flag:
        print 'Error:', result
        return flag, result
    potential_locations = list()
    for point in result.split(';'):
        if len(point) == 0:
            continue
        # placename , distance , mapx, mapy, mapw
        point = point.split('|')
        distance_from_place = float(point[1])
        x, y, w = int(point[2]), int(point[3]), int(point[4])
        coord = Coordinate(x, y, w, distance=distance_from_place)
        place_name = point[0]
        potential_locations.append(Location(place_name, coord))

    return True, potential_locations


def getLocation():
    """Get location from server.

    :returns: a list of potential :class:`Location` objects,
        sorted from most to least likely.

    """

    return __update(getuser())


def post_location(place_name):
    """Post encoded location to server after measuring the signal strength
    agin, without changing the database.

    :param place_name: Encoded string representing the location to post to
        the server. The user will show up on the map there.
    :type place_name: str

    :returns: a list of potential :class:`Location` objects,
        sorted from most to least likely.

    """

    print "Name to post:", place_name

    return __update(getuser(), place_name=place_name)


def weak_post_location(place_name):
    """
    Post encoded location to server, without changing the database and without
        refreshing signal strength.

    :param place_name: Encoded string representing the location to post to
        the server. The user will show up on the map there.
    :type place_name: str

    :returns: a list of potential :class:`Location` objects,
        sorted from most to least likely.

    """

    print "Name to post:", place_name

    return __update(getuser(), place_name=place_name, refresh=False)


def __getPlatform():
    """Return a standard readable string based on the operating system.

    :returns: A string; generally one of 'mac', 'win', 'linux'.
        In other cases, returns sys.platform

    """

    import sys
    if sys.platform.startswith('darwin'):
        return 'mac'
    elif sys.platform.startswith('win'):
        return 'win'
    elif sys.platform.startswith('linux'):
        return 'linux'
    return sys.platform  # non-standard platform


def do_train(placename, coord):
    """Tell server that a location in x,y,w space maps to a certain
        signal strength dictionary (data) and encoded placename string.

    :param placename: Encoded string representing the location to
        post to the server.
    :type placename: str
    :param coord: x,y,w coordinate to post
    :type coord: :class:`Coordinate`

    :returns: Unknown, TODO

    .. warning: This actually modifies the database on the server and
        can create novel locations or improve the database entry for existing
        locations. Try to avoid calling this without user interaction.

    """

    mapx, mapy, mapw = coord.x, coord.y, coord.w

    signal_strength_nodes = signal_strength.get_avg_signal_nodes(samples=3,
                                                            tsleep=0.15)
    signal_strength_str_list = [str(node) for node in signal_strength_nodes]
    signal_strength_str = ";".join(signal_strength_str_list)

    #XXX: Using this method until the server api gets fixed.
    # I know it is REALLY BAD - Julian
    global last_signal_strength_string
    last_signal_strength_string = signal_strength_str

    dict_send = {
                'username': getuser(),
                'placename': placename,
                'mapx': mapx,
                'mapy': mapy,
                'mapw': mapw,
                'data': signal_strength_str
               }
    dict_send['platform'] = __getPlatform()

    ret_status, result = send_to_server('train.php', dict_send)
    print dict_send
    if not ret_status:
        print 'Error:', result
        return ret_status, result

    return True, result


def __unserialize_person_data(server_response_string):
    """Parses a server-generated pipe-separated string and returns a
        dictionary of user information.

    :param server_response_string: The response to parse.
    :type: server_response_string: str

    :returns: dict of the form
        ``{'username':str, 'placename':str, 'status':str, 'lastupdate':str}``

    """

    personData = dict()
    if server_response_string == 'nobody':
        return 'nobody'
    server_response_array = server_response_string.split('|')
    person_data['username'] = server_response_array[0]
    person_data['placename'] = server_response_array[1]
    person_data['status'] = server_response_array[2]
    person_data['lastupdate'] = server_response_array[3]
    return person_data


def do_query(username):
    #XXX: UNTESTED
    """Get a dictionary containing username, placename, status, and
        lastupdate of person with given username

    :param username: Username of user to get information about.
    :type username: str

    :returns: a tuple ``(serverSuceededBOOL,reasonFailedStr/pointExistsBOOL)``

    """

    flag, result = send_to_server('query.php', {'username': username})
    if not flag:
        print 'Error:', result
        return flag, result

    result = __unserialize_person_data(result)
    return True, result


def do_datapointexistence(place_name):
    """Check if a point with a specific encoded place_name exists.

    :param place_name: Encoded string representing the location to
        post to the server.
    :type place_name: str

    :returns: a tuple ``(serverSuceededBOOL,reasonFailedStr/pointExistsBOOL)``

    """

    flag, result = send_to_server('pointexistence.php',
                                  {'placename': place_name})
    if not flag:
        print 'Error:', result
        return flag, result

    if result == 'true':
        return True, True
    else:
        return True, False


def do_cloak(username):
    """Tell the server to stop displaying a user with username on the map.
        If an Update happens, the user will reappear on the map again.

    This should require authentication and should only be possible for
    the active user.

    :param username: Username of user to conceal on the map.
    :type username: str

    :returns: a tuple ``(serverSuceededBOOL,serverResponseSTR)``

    """

    flag, result = send_to_server('cloak.php', {'username': username})
    if not flag:
        print 'Error:', result
        return flag, result

    return flag, result


if __name__ == '__main__':
    #~ do_update('bfisher','righthere')
    print do_datapointexistence('AC30,out,rm308')
    print do_datapointexistence('AC30,,out,rm308')
