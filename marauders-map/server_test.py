import client_api
import signal_strength
from getpass import getuser
from configuration import Settings

Settings.init()
user = client_api.User(username=getuser(), alias='Julian Ceipek')
user.put()

#place = client_api.Place(floor='EH4', name='lounge', alias='SLAC Palace')
#place.post()

np = client_api.get_places(name='lounge', floor='EH4')[0]
print np
np.alias = 'SLAC Realm'
np.put()

b = client_api.Bind(username=getuser(), signals=signal_strength.get_avg_signals_dict(), x=2550.0/3000.0, y=1629.0/2100.0, place=np)
b.post()
