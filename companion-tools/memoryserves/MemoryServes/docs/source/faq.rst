.. index:: FAQ

Memory Serves FAQ
==========================

What if I forget my admin password?
-------------------------------------

If you forget your admin password, you can clear the users from the database and create a new admin account using the **Clear Users** utility. On Windows XP, this utility will be found from the **Start** menu, under
**All Programs** >> **Memory Serves** >> **Clear Users**.

The next time you start **Memory Serves**, it will take you to the welcome page, and you'll be able to create a new admin account. Don't forget it this time!

Note that Memory Serves must not be running when you clear the user names, because doing so modifies the database on disk. If you try clearing the user accounts while Memory Serves is running, an error message will appear, and the program will quit immediately.


How does the server work?
---------------------------

When you run Memory Serves, it starts a small HTTP Web server on your computer. Memory Serves uses the open-source `cherrypy <http://www.cherrypy.org/>`_ Web server to do this.

The server can only be seen by other computers on your LAN or VPN, and not the Internet as a whole.

All data sent to and from Memory Serves -- e.g. from Felix, or from a Web browser -- uses the HTTP protocol.


The server times out if I upload a large memory. Is my memory uploaded correctly?
-------------------------------------------------------------------------------------

If you upload a very large memory to Memory Serves, the upload page might time out before the upload is complete. If this happens, you'll get an error, but the file should be uploaded correctly. You can check this by viewing the memory, and making sure that it has the expected number of entries (records).

If you're uploading a very large memory or glossary file, you might consider using the :doc:`memory-importer` program that comes with Memory Serves.

Are there any limitations to Memory Serves?
--------------------------------------------------

There are no limitations on the number of connections, memories, glossaries, or anything else about Memory Serves. The only limitations to Memory Serves are those of your computer's processing speed, and the process memory limit.
