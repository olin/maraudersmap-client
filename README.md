<<<<<<< HEAD
# development branch

Welcome to the development branch. This is where *real* stuff happens. It may be a bit unstable, but that is no
excuse for writing sloppy code; if you want a place to mess around without worrying about style, you should work in
the *playground* branch.

## Rules and Guidelines
* Try to document your code as often as possible, and **never** modify code without changing the docstrings
associated with it to match those changes; **"Comments that contradict the code are worse than no comments"** - 
[PEP8](http://www.python.org/dev/peps/pep-0008/)
* Use XXX and TODO in the comments to explain what needs to be implemented/fixed
* Take the appropriate TODO item off the following list when it is implemented

## TODO (in no particular order)
* Conform existing code to PEP8 wherever possible (QT uses ``mixedCase``, we are using ``lower_case_with_underscores``) - **in progress**
* Write unittests for everything
* Make the threading system in the UI utilize some kind of queue to avoid periodic lockups
* Switch to the client-side api from the server repository
* Make ``Go Offline`` work properly
* Make it possible to set the full user name in general preferences
* Make it possible to configure the update frequency in advanced preferences - **in progress**
* Make it possible to configure the server location in advanced preferneces
* Make it possible to define custom locations (this will involve a web ui launched using a specific call to the server)

## Done
* Load/Save the preferences from/to a file in an appropriate location (will vary by OS) - works for now; may need to be ported to ConfigObj
=======
# Marauder's map

Marauder's map helps students see where other students are on Olin's campus.

This is the start of an attempt to modernize **The Marauder's Map @ Olin**, 
an application written between 2008 and 2010 by Andrew Barry and Ben Fischer.
It used wxPython, PHP, and MySQL.

This repository is for *client* development. For server development, see 
[https://github.com/ohack/maraudersmap-server/](Marauder's Map Server Repository).

The original client used wxPython. We are attempting to improve it and port it to QT using pyside.
![Mac Screenshot](https://github.com/ohack/maraudersmap-client/raw/master/Screenshots/ScreenshotOSX.png)

In addressing some of the issues of the previous version of *Marauder's Map @ Olin*, we will strive for the following:

### Maintainability

* Code will be legibile and compliant with [PEP8](http://www.python.org/dev/peps/pep-0008/)
and commented (using the [Sphinx .rst markup syntax](sphinx.pocoo.org))
* Code will have tests to document its status 
(using the [Python unittesting framework](http://docs.python.org/library/unittest.html))
* The actual project will be documented in a way such that it can be extended, replicated,
and/or restarted relatively easily

### Educational value:

* Standards and standard libraries will be leveraged where available, i.e. JSON for communication general good practices
* Made open and involve as many students as possible; perhaps it can be leveraged in future applications?

## Branches
* **master** -- This is stable but very outdated. Don't use it for now.
* **development** -- This is where active development is happening. Stuff here generally works, but is in flux.
* **playground** -- This is where we try out crazy new ideas, don't follow standards, and write unstable code.
* **gh-pages** -- This is the documentation branch. Never edit files in this branch manually; use 
                  ``make html`` in ``docs`` to generate updated documentation.

## Documentation
[HTML docs](http://ohack.github.com/maraudersmap-client/)
>>>>>>> ab810ca2e57eb2d78f3d32db7e19b84900098a45
