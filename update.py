# Send position / username. Retrieve guesses.

import coordinates
import data_connections

def do_update(username, currPlaceName = None, status=None):
    '''
    Allows user to be drawn on map by sending location to server.

    Sends the following stuff to the server:
    username -> string representing user
    data -> signalStrengthDict
    platform -> string: 'linux'/'win'/'darwin'
    placename -> string of curr place
    status -> never used ?!?!?!
    '''
    signalStrengthDict = coordinates.getAvgSignalStrengthDict()
    if not signalStrengthDict:
        return False, "Failed to get coordinates"
    else:
        signalStrengthStr = data_connections.serializeMACData( signalStrengthDict )
        
        dictSend = dict()
        dictSend['username'] = username
        dictSend['data'] = signalStrengthStr
        dictSend['platform'] = __getPlatform()
        if currPlaceName != None:
            dictSend['placename'] = currPlaceName  
            
        if status != None:
            dictSend['status'] = status
        
        flag, result = data_connections.sendToServer('update.php', dictSend)
        if not flag:
            print 'Error:', result
            return flag, result, signalStrengthStr
        
        l = data_connections.unserializeMACData(result)
        return True, l, signalStrengthStr

def __getPlatform():
    '''
    Return a standard readable string based on the operating system.
    '''
    import sys
    if sys.platform.startswith('darwin'):
        return 'mac'
    elif sys.platform.startswith('win'):
        return 'win'
    elif sys.platform.startswith('linux'):
        return 'linux'
    return sys.platform # non-standard platform

def do_train(username, placename, mapx, mapy, mapw, data):
    '''
    Tell server that a location in x,y,w space maps to a certain signal strength dictionary (data)
    '''
    strCoords = data_connections.serializeMACData(data)
    dictSend = {'username':username, 'placename':placename,'mapx':mapx,'mapy':mapy, 'mapw':mapw, 'data':strCoords}
    dictSend['platform'] = __getPlatform()
        
    retStatus, result = data_connections.sendToServer('train.php', dictSend)
    print dictSend
    if not retStatus:
        print 'Error:', result
        return retStatus, result
        
    return True, result

def do_query(username):
    '''
    Get the name of the place at which a user with a specific username is located
    '''
    flag, result = data_connections.sendToServer('query.php', {'username':username})
    if not flag:
        print 'Error:', result
        return flag, result
    
    result = data_connections.unserializePersonData(result)
    return True, result

def do_datapointexistence(placename):
    '''
    Check if a point with a specific place name exists
    '''
    flag, result = data_connections.sendToServer('pointexistence.php', {'placename':placename})
    if not flag:
        print 'Error:', result
        return flag, result
        
    if result=='true': return True, True
    else: return True, False

def do_cloak(username):
    '''
    Tell the server to stop displaying a user with username on the map
    '''
    flag, result = data_connections.sendToServer('cloak.php', {'username':username})
    if not flag:
        print 'Error:', result
        return flag, result
    
    return flag, result

if __name__=='__main__':
    #~ do_update('bfisher','righthere')
    print do_datapointexistence('AC30,out,rm308')
    print do_datapointexistence('AC30,,out,rm308')
