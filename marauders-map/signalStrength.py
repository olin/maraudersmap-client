import os
import sys
import subprocess
import json

class SignalNode(object):
    '''A highly optimized object to keep track of the signal strength
    associated with a node. It is hashable, so it can be a key in a dict
    or an element in a set.

    MACAddress and name are immutable once the instance is created,
    but signalStrength can be changed

    :param MACAddress: BSSID of the access point.
    :type MACAddress: str
    :param name: SSID of the access point
    :type name: str
    :param signalStrength: Access point signal strength, as measured from the user's machine.
    :type signalStrength: int
    '''

    __slots__ = ('__MACAddress', '__name', 'signalStrength')
    def __init__(self, MACAddress, name, signalStrength):
        self.__MACAddress = MACAddress
        self.__name = name        
        self.signalStrength = signalStrength

    @property
    def identifier(self):
        """Unique string identifier for the access point (independent of signalStrength)

        """
        return self.__MACAddress + self.__name

    @property
    def MACAddress(self):
        '''BSSID of the access point, as a string (MAC address)

        Example: '00:20:D8:2D:2C:C1'
        '''
        return self.__MACAddress

    @property
    def name(self):
        '''Name of the node, as a string.

        Example: OLIN_WH
        '''
        return self.__name

    def __str__(self):
        return "%s,%i" % (self.__MACAddress, self.signalStrength)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.__MACAddress + self.__name + str(self.signalStrength))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


def getAvgSignalNodes(samples=3, tsleep=0.15):
    """Gets the average signal strength of the nearby nodes.

    :param samples: Number of measurements to make & average
    :type samples: int
    :param tsleep: Number of seconds to wait between measurements 
        (although it will take a bit longer since getCoords() takes a while to execute)
    :type tsleep: float

    :returns: list of :class:`SignalNode` objects
    """
    return getAvgSignalNodesDict(samples=samples, tsleep=tsleep).values()
    
def getAvgSignalNodesDict(samples=3, tsleep=0.15):
    """Gets the average signal strength of the nearby nodes.

    :param samples: Number of measurements to make & average
    :type samples: int
    :param tsleep: Number of seconds to wait between measurements 
        (although it will take a bit longer since getCoords() takes a while to execute)
    :type tsleep: float

    :returns: dict of the form {MAC_AddressSTR : :class:`SignalNode`\ }
    """
    import time
    allSurroundingNodes = dict() 

    for i in range(samples):
        res = getSignalNodeDict()
        for nodeIdentifier in res:
            if nodeIdentifier in allSurroundingNodes:
                allSurroundingNodes[nodeIdentifier].signalStrength += res[nodeIdentifier].signalStrength
            else:
                allSurroundingNodes[nodeIdentifier] = res[nodeIdentifier]
        time.sleep(tsleep)
    

    #TODO: Figure out what to in terms of division if the else statement above is triggered.

    # And divide each by sample count
    for node in allSurroundingNodes.values():
        node.signalStrength /= float(samples)

    return allSurroundingNodes

def getSignalNodeDict():
    '''
    Scans (or gets cached versions, on some systems) of wireless signal strengths around the computer,
    using platform-dependent methods.
    Returns a dict mapping SignalNode identifiers to SignalNodes
    '''
    
    # WINDOWS
    if sys.platform.startswith('win'):        
        # Should work on Windows > XP SP3
        return __getSignalNodesWin()
    # LINUX
    elif sys.platform.startswith('linux'):
        # This should work on most recent versions of Linux, according to Riley - Julian
        # TODO: Fall back to old method for systems without nm-tool
        # In that case, users will need to run the application as root, however
        return __getSignalNodesNetworkManager()
    # MAC OS X
    elif sys.platform.startswith('darwin'):
        return __getSignalNodesMac()
    
def __interpretDB(signalString):
    '''
    Most platforms (nm-tool doesn't for some reason) return the Received Signal Strength Indication (RSSI) in dBm units (http://en.wikipedia.org/wiki/DBm)
    The following is a convenient way to indicate, for example, that -85 is weaker than -10
    '''
    return 100 + int(signalString)
    
def __getExePath():
    return '.\\windowsGetWirelessStrength\\Get Wireless Strengths\\bin\\Release\\'

def __getSignalNodesWin():
    signalNodesDict = dict()
    # Should work on Windows > XP SP3
    o = subprocess.Popen(os.path.join(__getExePath(), 'Get Wireless Strengths.exe'), stderr=subprocess.PIPE, stdout=subprocess.PIPE,shell=True).stdout#shell=true hides shell
    res = o.read()
    o.close()
    data = json.loads(res)
    for row in data:
        RSSI,SSID,BSSID = row['RSSI'], row['SSID'],row['BSSID']
        if 'OLIN' in SSID and 'GUEST' not in SSID: #Only take into account OLIN wifi and non-guest WIFI
            currNode = SignalNode(BSSID, SSID, __interpretDB(RSSI))
            signalNodesDict[currNode.identifier] = currNode
    return signalNodesDict

def __getSignalNodesMac():
    import plistlib
    # '/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport -s -x'
    # This is an undocumented system utility available on Mac OS X
    # From the included help:
    # -s[<arg>] --scan=[<arg>]       Perform a wireless broadcast scan.
    #           Will perform a directed scan if the optional <arg> is provided
    # -x        --xml                Print info as XML
    signalNodesDict = dict()
    
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
            currNode = SignalNode(':'.join(bssid), network['SSID_STR'], __interpretDB(network['RSSI']))
            signalNodesDict[currNode.identifier] = currNode
    return signalNodesDict

def __getSignalNodesNetworkManager():
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
    signalNodesDict = dict()

    for line in result:
        # Format is now
        # ['OLIN_GUEST:      Infra', ' 00:26:3E:30:2B:82', ' Freq 2442 MHz', ' Rate 54 Mb/s', ' Strength 25 WPA']
        accessPtInfo = line.split(',')
        sepLoc = accessPtInfo[0].find(':')
        if sepLoc <= 0: #fail gracefully if we are parsing a line we shouldn't be...
            continue
        ssid = accessPtInfo[0][:sepLoc]
        bssid = accessPtInfo[1].strip()
        strength = int(accessPtInfo[4].strip().split(' ')[1]) - 10 # As far as I can tell, this is the relationship to __interpretDB's output - Julian
        currNode = SignalNode(bssid, ssid, strength)
        signalNodesDict[currNode.identifier] = currNode
    return signalNodesDict

if __name__ == '__main__':
    # test code
    print ";".join([str(node) for node in getAvgSignalNodes(samples=3, tsleep=0.15)])
