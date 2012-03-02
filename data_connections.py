# Ties together Python with PHP
import urllib

from configuration import Settings

def sendToServer(strPHPScript, dictParams):
    '''
    Uses urllib to send a dictionary to a PHP script on the server specified in configuration.py 

    Returns a tuple (successBOOL, responseSTR/explanation_of_failureSTR)
    '''

    strUrl = Settings.SERVER_ADDRESS + '/' + strPHPScript + '?'

    # Construct url with the parameters specified in the dictionary
    for param in dictParams:
        strUrl += param + '=' + str(dictParams[param]).replace(' ','%20') + '&'
    strUrl = strUrl.rstrip('&')
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

def serializeMACData(signalStrengthDict):
    '''
    Convert signalStrengthDict to a string 
    '''
    s = ''
    for mac in signalStrengthDict:
        s += mac + ',' + str(signalStrengthDict[mac][0]) + ';'
        # 00:11:22:33:44:55,45;
    return s.rstrip(';')

def unserializePersonData(s):
    '''
    Takes in a pipe-separated string (from a server response?) and 
    outputs a dictionary with the keys
    'username', 'placename', 'status', and 'lastupdate'
    '''
    personData = dict()
    if s == 'nobody': 
        return 'nobody'
    s = s.split('|')
    personData['username'] = s[0]
    personData['placename'] = s[1]
    personData['status'] = s[2]
    personData['lastupdate'] = s[3]
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

if __name__=='__main__':
    ret = sendToServer('update.php',{})
    print ret
