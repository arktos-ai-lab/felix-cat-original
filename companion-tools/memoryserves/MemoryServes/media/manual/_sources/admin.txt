The Admin Interface
=======================

As of version 1.3, Memory Serves has an admin interface. Use it to manage and create user accounts, view logs, and view and set preferences.

To access the Admin page, click on the <strong>Admin</strong> link on the bottom of the page, to the right of the copyright notice.

Users
---------

The Users page shows a list of user accounts. If you're logged in as an administrator, you'll see three links next to each account: View, Edit, and Delete.

If you're not logged in, or you're logged in as a non-administrator, then there will only be a "View" link next to each account. If you're logged in as a non-administrator, you can edit your own user account (e.g. setting a new password), but nobody else's. You also can't change your account type from "user" to "admin" -- an administrator account is needed to do that.

On the :ref:`preferences` page, you can configure the preferences for each user type: admin, user, guest, and "anon" (users who are not logged in are treated as "anon").

Logs
---------

There are three types of log: the Memory Serves log, the server error log, and the server access log. If you run into an error using Memory Serves, the Memory Serves log and the server error log can provide details about what went wrong.

If you're logged in as an administrator, you can clear the Memory Serves log. The server logs are cleared each time Memory Serves is started.

.. index:: preferences

.. _preferences:

Set Preferences
----------------

**One translation per source**

	Select this option to only allow one translation per source segment. A restart of Memory Serves is required for this to take effect.

**Normalize**
	You can set three types of preferences for determining how Memory Serves calculates translation and glossary matches.

	Normalize case
		Treat upper and lower-case letters as being identical for matching purposes (case-insensitive matching).

	Normalize hiragana/katakana
		Treat Hiragana and Katakana characters as being identical for matching purposes.

	Normalize width
		Treat single-byte and double-byte characters as being identical for matching purposes.

**System Tray**
	You can also choose whether to show a Memory Serves icon in the task (system) tray.

	Show system tray
		Show the system tray icon when Memory Serves is running.

**Data Folder**

	Data folder
		Specify the folder in which to store the Memory Serves TMs and glossaries (the default is the local app data folder or program data folder, depending on your installation preferences).
