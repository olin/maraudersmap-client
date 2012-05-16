all: main.app

# Some kind of switching needs to go here to configure behavior on different OSes
#develop: main.py qt.conf setup.py Info.plist
#	python setup.py py2app -A

# Mac OS X
main.app: src/mapclient.py data/qt.conf data/Info.plist setup.py
	python setup.py py2app

# Removing
clean:
	rm -rf build/
	rm -rf dist/
	rm altgraph*
	rm macholib*
	rm modulegraph*
	rm -rf py2app*
