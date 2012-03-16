Overview
********
The Marauder's Map client currently consists of 4 files:

mapclient.py
------------
The master file, which sets up the graphical user interface and makes calls to the 
api as appropriate.

configuration.py
----------------
Defines global settings for the client api, such as which server to use and the
web address of the map.

api.py
------
The client api that makes calls to the server and obtains signal strength data.

signalStrength.py
-----------------
Defines operating system independent calls to get signal strength data.


