Overview
********
The Marauder's Map client currently consists of 4 files:

    * :doc:`mapclient.py </mapclient>`
        The master file, which sets up the graphical user interface and makes calls to the 
        api as appropriate.

    * :doc:`configuration.py </configuration>`
        Defines global settings for the client api, such as which server to use and the
        web address of the map.

    * :doc:`api.py </api>`
        The client api that makes calls to the server and obtains signal strength data.

    * :doc:`signalStrength.py </signal_strength>`
        Defines operating system independent calls to get signal strength data.


