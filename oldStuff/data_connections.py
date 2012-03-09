# Ties together Python with PHP
import urllib

from configuration import Settings

def sendToServer(strPHPScript, dictParams):
    '''
    Uses urllib to send a dictionary to a PHP script on the server specified in configuration.py 

    Returns a tuple (successBOOL, responseSTR/explanation_of_failureSTR)
    '''

    # Construct url with the parameters specified in the dictionary
    strUrl = "%s/%s?%s" % (Settings.SERVER_ADDRESS, strPHPScript, urllib.urlencode(dictParams))
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

def serializeMACData(signalNodeArray):
    '''
    Convert signalNodeArray to a string 
    '''
    return ";".join([node for node in signalNodeArray])
    # 00:11:22:33:44:55,45;

def unserializePersonData(serverResponseString):
    '''
    Takes in a pipe-separated string and 
    outputs a dictionary with the keys
    'username', 'placename', 'status', and 'lastupdate'
    '''
    personData = dict()
    if serverResponseString == 'nobody': 
        return 'nobody'
    serverResponseArray = serverResponseString.split('|')
    personData['username'] = serverResponseArray[0]
    personData['placename'] = serverResponseArray[1]
    personData['status'] = serverResponseArray[2]
    personData['lastupdate'] = serverResponseArray[3]
    return personData

def unserializeMACData(s):
    '''
    Takes in a string from the server and returns an array of arrays
    where each subarray is in the sequence 'placename', 'distance','mapx','mapy','mapw'
    '''
    # XXX: Is not the opposite of serializeMACData! - Julian
    ret = []
    for point in s.split(';'):
        if len(point)==0: continue
        pointpts = point.split('|')
        # placename , distance , mapx, mapy, mapw
        ret.append([ pointpts[0], float(pointpts[1]), int(pointpts[2]), int(pointpts[3]), int(pointpts[4])])
    #name and distance pairs
    return ret

def parseServerResponse(responseStr):
    #XXX: This Doesn't work properly; from original code
    #TODO: Rewrite!


    # location strings look like WH,in,rm309
    locationList = unserializeMACData(responseStr)

    def parseLocationString(theString):
        location = theString.replace("OC", "MH")
 
        try:
            building, inside, description = location.split(",")
        except:
            return None

        floor = building[2]
        building = building[0:2]

        if (inside == "in"):
            inside = "inside"
        elif (inside == "out"):
            inside = "outside of"
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

            location = inside + " " + building + description
        else:
            if (floor != "LL"):
                location = inside + " " + building + " " + floor + " floor " + description
            else:
                location = inside + " " + building + " (" + floor + ") " + description
        
        return location
    
    return [parseLocationString(loc[0]) for loc in locationList]


if __name__=='__main__':
    ret = sendToServer('update.php',{})
    print ret
