# Send position / username. Retrieve guesses.

import coordinates
import data_connections

def do_update(username, currentplace = None, status=None):
    signalStrengthDict = coordinates.getAvgSignalStrengthDict()
    if not currCoords:
        pass # Failed to get coordinates
    else:
        strCoords = data_connections.serializeMACData( currentCoords )
        
        dictSend = {'username':username, 'data':strCoords}
        dictSend['platform'] = _getplatform()
        if currentplace != None:
            dictSend['placename'] = currentplace
            
        if status != None:
            dictSend['status'] = status
        
        flag, result = data_connections.sendToServer('update.php', dictSend)
        if not flag:
            print 'Error:', result
            return flag, result, currentCoords
        
        l = data_connections.unserializeMACData(result)
        return True, l, currentCoords

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
    flag, result = data_connections.sendToServer('query.php', {'username':username})
    if not flag:
        print 'Error:', result
        return flag, result
    
    result = data_connections.unserializePersonData(result)
    return True, result

def do_datapointexistence(placename):
    flag, result = data_connections.sendToServer('pointexistence.php', {'placename':placename})
    if not flag:
        print 'Error:', result
        return flag, result
        
    if result=='true': return True, True
    else: return True, False

def do_cloak(username):
    flag, result = data_connections.sendToServer('cloak.php', {'username':username})
    if not flag:
        print 'Error:', result
        return flag, result
    
    return flag, result

if __name__=='__main__':
    #~ do_update('bfisher','righthere')
    print do_datapointexistence('AC30,out,rm308')
    print do_datapointexistence('AC30,,out,rm308')