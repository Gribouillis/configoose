Introduction
============

``configoose`` is a module allowing Python programs and
libraries to use configuration files while
leaving users free to store these configuration files
to the location that suits them in their file system and
even in other locations.

Motivation
**********

As a regular writer of programs that use configuration files,
I have always found restrictive to impose on users the locations
where to store these files. As a user, I like to be able to organize
my storage space as I see fit. ``configoose`` is designed to respond
to this need.

Principle
*********

How can a program find its configuration file
if it can be anywhere on the file system,
in a place that the user chooses as he wants?

``configoose`` answers this question as follows:
the program uses an "abstract address" to designate its
configuration file, and it asks a third party where
is the configuration file that has been registered for this
abstract address. This third party is the ``configoose``
module. It
maintains a database connecting abstract addresses
to configuration file locations and therefore enables
Python programs or modules to access these files.
