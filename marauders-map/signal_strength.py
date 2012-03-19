import os
import sys
import subprocess
import json

class SignalNode(object):
    '''A highly optimized object to keep track of the signal strength
    associated with a node. It is hashable, so it can be a key in a dict
    or an element in a set.

    MAC_address and name are immutable once the instance is created,
    but signal_strength can be changed

    :param MAC_address: BSSID of the access point.
    :type MAC_address: str
    :param name: SSID of the access point
    :type name: str
    :param signal_strength: Access point signal strength, as measured from the user's machine.
    :type signal_strength: int
    '''

    __slots__ = ('__MAC_address', '__name', 'signal_strength')
    def __init__(self, MAC_address, name, signal_strength):
        self.__MAC_address = MAC_address
        self.__name = name        
        self.signal_strength = signal_strength

    @property
    def identifier(self):
        """Unique string identifier for the access point (independent of signal_strength)

        """
        return self.__MAC_address + self.__name

    @property
    def MAC_address(self):
        '''BSSID of the access point, as a string (MAC address)

        Example: '00:20:D8:2D:2C:C1'
        '''
        return self.__MAC_address

    @property
    def name(self):
        '''Name of the node, as a string.

        Example: OLIN_WH
        '''
        return self.__name

    def __str__(self):
        return "%s,%i" % (self.__MAC_address, self.signal_strength)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.__MAC_address + self.__name + str(self.signal_strength))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


def get_avg_signal_nodes(samples=3, tsleep=0.15):
    """Gets the average signal strength of the nearby nodes.

    :param samples: Number of measurements to make & average
    :type samples: int
    :param tsleep: Number of seconds to wait between measurements 
        (although it will take a bit longer since getCoords() takes a while to execute)
    :type tsleep: float

    :returns: list of :class:`SignalNode` objects
    """
    return get_avg_signal_nodes_dict(samples=samples, tsleep=tsleep).values()
    
def get_avg_signal_nodes_dict(samples=3, tsleep=0.15):
    """Gets the average signal strength of the nearby nodes.

    :param samples: Number of measurements to make & average
    :type samples: int
    :param tsleep: Number of seconds to wait between measurements 
        (although it will take a bit longer since getCoords() takes a while to execute)
    :type tsleep: float

    :returns: dict of the form {MAC_AddressSTR : :class:`SignalNode`\ }
    """
    import time
    all_surrounding_nodes = dict() 

    for i in range(samples):
        res = get_signal_node_dict()
        for node_identifier in res:
            if node_identifier in all_surrounding_nodes:
                all_surrounding_nodes[node_identifier].signal_strength += res[node_identifier].signal_strength
            else:
                all_surrounding_nodes[node_identifier] = res[node_identifier]
        time.sleep(tsleep)
    

    #TODO: Figure out what to in terms of division if the else statement above is triggered.

    # And divide each by sample count
    for node in all_surrounding_nodes.values():
        node.signal_strength /= float(samples)

    return all_surrounding_nodes

def get_signal_node_dict():
    '''
    Scans (or gets cached versions, on some systems) of wireless signal strengths around the computer,
    using platform-dependent methods.
    Returns a dict mapping SignalNode identifiers to SignalNodes
    '''
    
    # WINDOWS
    if sys.platform.startswith('win'):        
        # Should work on Windows > XP SP3
        return __get_signal_nodes_win()
    # LINUX
    elif sys.platform.startswith('linux'):
        # This should work on most recent versions of Linux, according to Riley - Julian
        # TODO: Fall back to old method for systems without nm-tool
        # In that case, users will need to run the application as root, however
        return __get_signal_nodes_network_manager()
    # MAC OS X
    elif sys.platform.startswith('darwin'):
        return __get_signal_nodes_mac()
    
def __interpret_DB(signal_string):
    '''
    Most platforms (nm-tool doesn't for some reason) return the Received Signal Strength Indication (RSSI) in dBm units (http://en.wikipedia.org/wiki/DBm)
    The following is a convenient way to indicate, for example, that -85 is weaker than -10
    '''
    return 100 + int(signal_string)
    
def __getExePath():
    return '.\\windowsGetWirelessStrength\\Get Wireless Strengths\\bin\\Release\\'

def __get_signal_nodes_win():
    signal_nodes_dict = dict()
    # Should work on Windows > XP SP3
    o = subprocess.Popen(os.path.join(__getExePath(), 'Get Wireless Strengths.exe'), stderr=subprocess.PIPE, stdout=subprocess.PIPE,shell=True).stdout#shell=true hides shell
    res = o.read()
    o.close()
    data = json.loads(res)
    for row in data:
        RSSI,SSID,BSSID = row['RSSI'], row['SSID'],row['BSSID']
        if 'OLIN' in SSID and 'GUEST' not in SSID: #Only take into account OLIN wifi and non-guest WIFI
            curr_node = SignalNode(BSSID, SSID, __interpret_DB(RSSI))
            signal_nodes_dict[curr_node.identifier] = curr_node
    return signal_nodes_dict

def __get_signal_nodes_mac():
    import plistlib
    # '/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport -s -x'
    # This is an undocumented system utility available on Mac OS X
    # From the included help:
    # -s[<arg>] --scan=[<arg>]       Perform a wireless broadcast scan.
    #           Will perform a directed scan if the optional <arg> is provided
    # -x        --xml                Print info as XML
    signal_nodes_dict = dict()
    
    ntwks = list()
    try:
        # Get information about networks 
        cmd = '/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport'
        o = subprocess.Popen(['/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport', '-s', '-x'], stdout=subprocess.PIPE).stdout
        ntwks = plistlib.readPlist(o)
    except Exception as e:
        print "Failed to find networks.  The command '%s' may not exist." % '/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport'
        print "Traceback is:\n%s" % e            
    
    for network in ntwks:
        if 'OLIN' in network['SSID_STR'] and 'GUEST' not in network['SSID_STR']:
            # Now we are pretty sure that this is a non-guest Olin network
            # Unless someone else has a router with 'OLIN' in the SSID
            
            # The BSSID (MAC address) is of the form 0:20:d8:2d:65:2
            # Now we need to convert it to the format 00:20:D8:2D:65:20
            macbytes = network['BSSID'].split(':')
            bssid = list()
            for byte in macbytes:
                if len(byte) < 2:
                    bssid.append(('0%s' % byte).upper())
                else:
                    bssid.append(byte.upper())
            curr_node = SignalNode(':'.join(bssid), network['SSID_STR'], __interpret_DB(network['RSSI']))
            signal_nodes_dict[curr_node.identifier] = curr_node
    return signal_nodes_dict

def __get_signal_nodes_network_manager():
    '''
    Uses nm-tool on Linux to get the signal strength as a dict of SignalNode identifiers -> SignalNodes
    Note: I couldn't find out the signal strength units. Hopefully they are compatible.
    '''
    p1 = subprocess.Popen("nm-tool", stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', '-E', "(\*|\s)OLIN_"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['grep', '-Eo', "OLIN_.*"], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p2.stdout.close()
    result = p3.communicate()[0].strip().split('\n')
    p1.wait()
    p2.wait()
    signal_nodes_dict = dict()

    for line in result:
        # Format is now
        # ['OLIN_GUEST:      Infra', ' 00:26:3E:30:2B:82', ' Freq 2442 MHz', ' Rate 54 Mb/s', ' Strength 25 WPA']
        access_pt_info = line.split(',')
        sepLoc = access_pt_info[0].find(':')
        if sepLoc <= 0: #fail gracefully if we are parsing a line we shouldn't be...
            continue
        ssid = access_pt_info[0][:sepLoc]
        bssid = access_pt_info[1].strip()
        strength = int(access_pt_info[4].strip().split(' ')[1]) - 10 # As far as I can tell, this is the relationship to __interpret_DB's output - Julian
        curr_node = SignalNode(bssid, ssid, strength)
        signal_nodes_dict[curr_node.identifier] = curr_node
    return signal_nodes_dict

if __name__ == '__main__':
    # test code
    print ";".join([str(node) for node in get_avg_signal_nodes(samples=3, tsleep=0.15)])
