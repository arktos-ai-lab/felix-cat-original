
Search and Replace
======================

As of version 1.3, Memory Serves has a new search and replace interface. You can use it to conduct fine-grained searches, replace within search results, and perform batch replace operations for all transaltion records (entries) matching
your criteria.

.. index:: search

Search
--------

To perform a search on a memory or glossary, click on the "Search" link next to that memory/glossary on the index page, or on its detailed view page.

Searching in Memory Serves works using the concept of "query filters" (see :ref:`query-filters`, below for details). Enter a filter and click **Search**; all matching records will appear, in a paginated view. You can keep adding filters until you have refined your search to the desired entries.

The current query filters are shown in a list to the right of the search box. Click on the "Remove" link next to a filter to delete it. If your query filters yield no matching entries, try deleting a filter to expand your search.

Once you've refined your search to your satisfaction, you can click the "Replace in Results" link to perform replacements. For example, after finding all the translations created by the user "Ryan Ginstrom," you can perform a replace operation to change all the "validated" flags for those translations to "true."

.. index:: replace

Replace
----------

There are three types of replace operations:

- :ref:`find`: Find the next translation record matching your criteria
- :ref:`replace`: Peform the replacement on the current match, and search for the next one.
- :ref:`replace-all`: Perform the replacement on all records matching your criteria.

Each translation record (entry) consists of several "fields": the source text, the translation, context, the date the translation was created, and so on. By default, replacements are made for matching source and translation fields. You can also specify which field you want to perform the replacement in.

Enter a term to search for that term anywhere in a source or translation. Use the tags below in the format ``tag:term`` to make fine-grained searches.

============   =============
Tag            Description
============   =============
source:        Replace in the source field
trans:         Replace in the translation field
context:       Replace in the context field
created-by:    Replace the creator field
created:       Replace the date created
modified-by:   Replace the modified-by field
modified:      Replace the date modified
reliability:   Replace the reliability
validated:     Mark the record as validated ("true") or not validated ("false")
refcount:      Change the reference count of the record
============   =============

Examples
^^^^^^^^^^^

Replace 'aaa' in source and translation segments with 'bbb'::

    From       aaa
    To         bbb

Replace 'xxx' in source segments with 'yyy'::

    From       source:xxx
    To         yyy


Follow a tag by an asterisk (\*) to replace the entire field. For example, to change the "created-by" field of all matching records to "Ryan"::

    From       created-by:*
    To         Ryan


Change the record's date created to 2009-10-01::

    From       created:
    To         2009-10-01


Make the reliability of the record 5::

    From       reliability:
    To         5


Validate the record::

    From       validated:
    To         true


.. _find:

Find
^^^^^^^^^

Enter a value in the "From" field and the "To" field, and click **Find**. Memory Serves will find the next record matching your criteria, and display a table with two columns: "Found" and "Will become." The second column is how the entry will look after you perform the replace. Click **Replace** to replace this entry and find the next matching one, or **Replace All** to replace all matching entries.

.. _replace:

Replace
^^^^^^^^^^^^^^

After you click **Find** and there is a matching translation entry, click **Replace** to perform the specified replacement on this entry, and find the next one. You can continue doing this until there are no more matching entries. Click **Find** to skip the replacement for this entry, and find the next matching one.

This feature is handy when you want to confirm each replacement before performing it.

.. _replace-all:

Replace All
^^^^^^^^^^^^^^

When you click **Replace All**, the specified replacement is performed on all translation entries matching your criteria. This is handy when you want to perform a lot of replacements at once.


.. _query-filters:

Query Filters
--------------------

Searching in Memory Serves uses the concept of "filters." A filter is a query that restricts the set of records that are shown. Examples of query filters are "all translations with the word 'spam' in the source," "all translations with a reliability score of 5 or higher," or "all translations created after 5 March 2009."

Enter a term to search for that term anywhere in a source or translation. Use the tags below in the format ``tag:term`` to make fine-grained searches.

================= ================
Tag               Description
================= ================
source:           Search in source field
trans:            Search in translation field
context:          Search in context field
Created
----------------------------------
created-by:       Search in creator field
created-before:   Search for records created before date (YYYY-MM-DD format)
created-after:    Search for records created after date (YYYY-MM-DD format)
Modified
----------------------------------
modified-by:      Search in modifier field
modified-before:  Search for records modified before date (YYYY-MM-DD format)
modified-after:   Search for records modified after date (YYYY-MM-DD format)
Reliability
----------------------------------
reliability:      Search for records with the specified reliability
reliability-gt:   Search for records with greater than the specified reliability
reliability-gte:  Search for records with at least the specified reliability
reliability-lt:   Search for records with less than the specified reliability
reliability-lte:  Search for records with no more than than the specified reliability
Validated
----------------------------------
validated:        Search for records that are validated ("true") or not validated ("false")
Reference Count
----------------------------------
refcount:         Search for records with the specified reference count
refcount-gt:      Search for records with greater than the specified reference count
refcount-gte:     Search for records with at least the specified reference count
refcount-lt:      Search for records with less than the specified reference count
refcount-lte:     Search for records with no more than than the specified reference count
================= ================

Examples
^^^^^^^^^^^^

Search for records created before 2009-10-01
    ``created-before:2009-10-01``

Search for records with a reliability of at least 5
    ``reliability-gte:5``

Search for records that have been validated
    ``validated:true``
