# Send position / username. Retrieve guesses.

import binutils
import data_connections

def do_update(username, currentplace = None, status=None):
	currentCoords = binutils.getavgcoords()
	if not currentCoords:
		print 'Error: No Intel proset wireless'
		return False, 'Getting wireless failed.', currentCoords
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

def _getplatform():
	import sys
	if sys.platform=='darwin':
		return 'mac'
	elif sys.platform=='win32':
		return 'win'
	elif sys.platform.startswith('linux'):
		return 'linux'
	return ''

def do_train(username, placename, mapx, mapy, mapw, data):
	strCoords = data_connections.serializeMACData(data)
	dictSend = {'username':username, 'placename':placename,'mapx':mapx,'mapy':mapy, 'mapw':mapw, 'data':strCoords}
	dictSend['platform'] = _getplatform()
		
	flag, result = data_connections.sendToServer('train.php', dictSend)
	print dictSend
	if not flag:
		print 'Error:', result
		return flag, result
		
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
	print do_datapointexistance('AC30,out,rm308')
	print do_datapointexistance('AC30,,out,rm308')
