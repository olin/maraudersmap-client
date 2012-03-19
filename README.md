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
