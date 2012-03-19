# playground branch

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
* Conform existing code to PEP8 wherever possible (QT uses ``mixedCase``, we are using ``lower_case_with_underscores``)
* Write unittests for everything
* Make the threading system in the UI utilize some kind of queue to avoid periodic lockups
* Switch to the client-side api from the server repository
* Make ``Go Offline`` work properly
* Load/Save the preferences from/to a file in an appropriate location (will vary by OS)
* Make it possible to set the full user name in general preferences
* Make it possible to configure the update frequency in advanced preferences
* Make it possible to configure the server location in advanced preferneces
* Make it possible to define custom locations (this will involve a web ui launched using a specific call to the server)

