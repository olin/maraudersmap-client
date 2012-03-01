import os
import sys
import subprocess
import json

def getavgcoords(n=3, tsleep=0.15):
    ''' 
    Get the average signal strength from n samples, at intervals of tsleep seconds
    (although it will take a bit longer since getcoordinates() takes a while to execute)
    '''
    import time
    totals = dict()
    for i in range(n):
        print i
        res = getcoordinates()
        for spot in res:
            if spot in totals:
                totals[spot][0] += res[spot][0]
            else:
                totals[spot] = res[spot]
        time.sleep(tsleep)
        
    # And divide each by n
    for spot in totals:
        totals[spot][0] = totals[spot][0] / (float(n))

    return totals
    

def getcoordinates():
    binutilspath = getpath()
    coord = Coordinate()

    ret = dict()
    # Dictionary with key : value pairs of the form
    # MAC_Address : [Signal_Strength, Network_Name]
    # Example:
    # {
    #   '00:20:D8:2D:2C:C1': [14, 'OLIN_CC'],
    #   '00:20:D8:2D:B3:C0': [12, 'OLIN_CC'],
    #   '00:20:D8:2D:65:02': [12, 'OLIN_WH'],
    #   '00:20:D8:2D:85:40': [38, 'OLIN_CC']
    # }
    
    # WINDOWS
    if sys.platform.startswith('win'):        
        #should work on Windows > XP SP3
        o = subprocess.Popen(os.path.join(binutilspath, 'Get Wireless Strengths.exe'), stderr=subprocess.PIPE, stdout=subprocess.PIPE,shell=True).stdout#shell=true hides shell
        res = o.read()
        o.close()
        data = json.loads(res)
        for row in data:
            RSSI,SSID,BSSID = row['RSSI'], row['SSID'],row['BSSID']
            if 'OLIN' in SSID and 'GUEST' not in SSID: #Only take into account OLIN wifi and non-guest WIFI
                ret[BSSID] = [int(RSSI),SSID]
                print SSID,RSSI,BSSID
        # for line in res:
        #   # if line=='': continue
        #    # linepts = line.split(',')
        #   # if 'OLIN' in linepts[2] and 'GUEST' not in linepts[2]: #don't allow other wifi hotspots!
        #        # coord.strength = interpretDB(linepts[0])
        #       # coord.mac = linepts[1]
        #        # coord.name = linepts[2]
        #        
        #        # ret[coord.mac] = [coord.strength, coord.name]
    # LINUX
    elif sys.platform.startswith('linux'):
        # This should work on most recent versions of Linux, according to Riley - Julian
        # TODO: Fall back to old method for systems without nm-tool
        # In that case, users will need to run the application as root, however
        ret = __getNetworkManagerSignalStrength()
    # MAC OS X
    elif sys.platform.startswith('darwin'):
        import plistlib
        # '/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport -s -x'
        # This is an undocumented system utility available on Mac OS X
        # From the included help:
        # -s[<arg>] --scan=[<arg>]       Perform a wireless broadcast scan.
        #           Will perform a directed scan if the optional <arg> is provided
        # -x        --xml                Print info as XML
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
                ret[':'.join(bssid)] = [interpretDB(network['RSSI']), network['SSID_STR']]
    return ret
    
class Coordinate:
    # XXX: The way this class is used is really silly. It should probably die. - Julian
    name = ''
    strength = ''
    mac = ''

def interpretDB(string):
    # All platforms return the Received Signal Strength Indication (RSSI) in dBm units (http://en.wikipedia.org/wiki/DBm)
    # The following is a convenient way to indicate, for example, that -85 is weaker than -10
    return 100 + int(string)
    
def getpath():
    # XXX: Only works on Windows and Linux. This should be made private unless it is used in another file - Julian
    if sys.platform.startswith('linux') and os.path.exists('/usr/bin/olinmm.py') and os.path.exists('/usr/share/olinmm'):
        return '/usr/share/olinmm/binutils/'
    elif sys.platform.startswith('linux'):
        return 'binutils/'
    else:
        return '.\\windowsGetWirelessStrength\\Get Wireless Strengths\\bin\\Release\\'
        #~ pathname = os.path.split( os.path.abspath(sys.argv[0]))[0]
        #~ return os.path.join(pathname, 'binutils')

def __getNetworkManagerSignalStrength():
    # Uses nm-tool on Linux to get the signal strength
    # Note: I couldn't find out the signal strength units. Hopefully they are compatible.
    p1 = subprocess.Popen("nm-tool", stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', '-E', "(\*|\s)OLIN_"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['grep', '-Eo', "OLIN_.*"], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p2.stdout.close()
    result = p3.communicate()[0].strip().split('\n')
    p1.wait()
    p2.wait()
    signalStrengthDict = dict()
    for line in result:
        # Format is now
        # ['OLIN_GUEST:      Infra', ' 00:26:3E:30:2B:82', ' Freq 2442 MHz', ' Rate 54 Mb/s', ' Strength 25 WPA']
        accessPtInfo = line.split(',')
        sepLoc = accessPtInfo[0].find(':')
        if sepLoc <= 0: #fail gracefully if we are parsing a line we shouldn't be...
            continue
        ssid = accessPtInfo[0][:sepLoc]
        bssid = accessPtInfo[1].strip()
        strength = int(accessPtInfo[4].strip().split(' ')[1]) - 10 # As far as I can tell, this is the relationship to interpretDB's output - Julian
        signalStrengthDict[bssid] = [strength, ssid]
    return signalStrengthDict

if __name__ == '__main__':
    # test code
    print getavgcoords(3, 0.15)
