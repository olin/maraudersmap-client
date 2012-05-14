# http://islascruz.org/html/index.php/blog/show/Python%3A-Simple-HTTP-Server-on-python..html

import os
import cgi
import sys
import webbrowser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from configuration import Settings

def auth_callback(cookies_dict):
    Settings.COOKIES = cookies_dict
    print Settings.COOKIES

class MapAuthHTTPServer(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write('''
<html><body>
<h1>Map auth debug</h1>
<form method="post">
<button type=submit name="browserid" value="SOME_INVALID_DATA">SUBMIT</button>
</form>
</body></html>
''')

	def do_POST(self):
		length = int(self.headers.getheader('content-length'))
		postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)


		self.send_response(303)
		self.send_header('Location', Settings.WEB_ADDRESS)
		self.end_headers()
		self.wfile.write('User authenticated. Redirecting to the map.')

		auth_callback({
			"browserid": postvars.get('browserid', '')[0],
			"session": postvars.get('session', '')[0]
		})

def authenticate():
    Settings.init()

    server = HTTPServer(('', 0), MapAuthHTTPServer)

    port = server.server_port

    print "%s/?port=%s" % (Settings.AUTH_ADDRESS, port)

    webbrowser.open("%s/?port=%s" %
        (Settings.AUTH_ADDRESS, port))

    print 'server started: http://localhost:' + str(port) + '/'
    server.serve_forever()

if __name__=='__main__':
	main()
