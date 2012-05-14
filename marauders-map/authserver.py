# http://islascruz.org/html/index.php/blog/show/Python%3A-Simple-HTTP-Server-on-python..html

import os
import cgi
import sys
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
 
class customHTTPServer(BaseHTTPRequestHandler):
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
		print(postvars.get('browserid', ''))
		print(postvars.get('session', ''))

		self.send_response(303)
		self.send_header('Location', 'http://map.fwol.in/')
		self.end_headers()
		self.wfile.write('User authenticated. Redirecting to the map.')

def main():
	try:
		server = HTTPServer(('', 0),customHTTPServer)
		print 'server started: http://localhost:' + str(server.server_port) + '/'
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close() 

if __name__=='__main__':
	main()