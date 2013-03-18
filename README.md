posterous-to-mynt
=================

In order to get my exported Posterous blog into a usable format I needed to parse their XML output.
I didn't find anything other than Wordpress that would read their exports already, so I set to write a quick
something of my own to do the job.

This was an exercise in learning Python as well, so don't expect 100% ideal Python.

The output of this program is a set of files in the format that mynt (http://mynt.mirroredwhite.com/) expects. 

XML files under the Posterous export posts/ folder are converted to _posts/file.md files for mynt to read. Images
directly linking to Posterous's servers (e.g. http://getfile\d*.posterous.com) are searched for in the backup archive
and if not found fetched directly from the servers. These are then copied into the mynt folder under _asset/images/.

I didn't have a super involved blog to convert over, so there may be scaling issues I'm unaware of.

As always, patches or suggestions are welcome. This project is not heavily maintained.

== Usage ==

python posterous-to-mynt.py <root of folder containing Posterous backup> <root of folder containing mynt blog>

== Caveats ==

* Some images aren't recognized by this program even though they are in the backup. It fetches them instead.

* Some HTML to Markdown conversion doesn't work quite correctly. It does fairly well for my blog, though.

* This *could* overwrite existing blog or asset files in your mynt folder. I recommend not outputing to an existing blog's folder.
