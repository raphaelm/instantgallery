instantgallery.py
=================

instantgallery.py takes a directory containing photos and turns it into a 
shiny photo gallery made for the web. ALl you have to do is to enter a single
command line. To publish the gallery, just upload the output directory to 
any webserver. It's plain HTML, CSS and Javascript and it thus works regardless 
of your webserver.

instantgallery.py can handle and display EXIF information and is able to try
rotating portrait format photos automatically (by using their EXIF rotate
information combined with their aspect ratio).

By default the photos are ordered by their timestamp but you can specify a flag to 
have them sorted alphabetically. In the first case the script tries to read 
their EXIF "OriginalDate" field first and uses Unix' mtime() if this failes.

For an example of a gallery created with this software see below.

instantgallery.py supports EXIF information including GPS (shown using 
OpenStreetMap), subdirectories, intro texts and generating a ZIP archive
of the pictures for download.

instantgallery.py is able to generate galleries in other languages than
English, but currently only German is supported. If you add another language
I would be glad to get an [email](<raphael@geeksfactory.de>) or just fork
the project on [GitHub](<https://github.com/raphaelm/instantgallery>) and
send me a pull request.

Bugs
----

Please create an issue at [GitHub](<https://github.com/raphaelm/instantgallery>).
If you don't have and don't want to have a GitHub account, send me an [email](<raphael@geeksfactory.de>).

Example
-------

    $ tree /tmp/demo
        /tmp/demo
        ├── GPS demo
        │   ├── Paris1.JPG
        │   ├── Paris2.JPG
        │   ├── Paris3.JPG
        │   ├── Paris4.JPG
        │   └── Paris5.JPG
        ├── INTRO
        ├── London1.JPG
        ├── London2.JPG
        ├── London3.JPG
        ├── London4.JPG
        ├── London5.JPG
        ├── Oslo1.JPG
        ├── Oslo2.JPG
        ├── Oslo3.JPG
        ├── Oslo4.JPG
        ├── Oslo5.JPG
        ├── Rom1.JPG
        ├── Rom2.JPG
        ├── Rom3.JPG
        ├── Rom4.JPG
        └── Rom5.JPG

     1 directory, 21 files

    $ ./instantgallery.py /tmp/demo /tmp/capitals --title "Capitals" -i -z
    
Result: http://www.raphaelmichel.de/bilder/demo/

Authors
-------
* Raphael Michel
* Graham ([github.com/4gra](https://github.com/4gra/instantgallery))

License
-------

The software is free and open source software and published unter the terms
of the MIT license.

Copyright (c) 2011-2013 Raphael Michel and contributors

> Permission is hereby granted, free of charge, to any person obtaining a copy of 
> this software and associated documentation files (the "Software"), to deal in the 
> Software without restriction, including without limitation the rights to use, copy, 
> modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
> and to permit persons to whom the Software is furnished to do so, subject to the 
> following conditions:
> The above copyright notice and this permission notice shall be included in 
> all copies or substantial portions of the Software.
> 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
> FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
> DEALINGS IN THE SOFTWARE.

The default font is 'Ubuntu' which is Copyright 2010, 2011 Canonical Ltd.
To remove it, just remove the first 6 lines from both .css files and
remove the file 'static/Ubuntu.woff'.
The font is licensed under the Ubuntu Font Licence, Version 1.0. 
https://launchpad.net/ubuntu-font-licence

Requirements
------------

* [Python 2.7](http://python.org/) (Debian/Ubuntu: `python2.7`)
* [Python Imaging Library (PIL)](http://www.pythonware.com/products/pil/) (Debian/Ubuntu: `python-imaging`)
* [ImageMagick's convert](http://imagemagick.org/) (Debian/Ubuntu: `imagemagick`)
        
Optional, for more cool features:

* SlimIt (`$ [sudo] easy_install-2.7 slimit`)
* CSSmin (`$ [sudo] easy_install-2.7 cssmin`)
* Django-HTMLmin (`$ [sudo] easy_install-2.7 django-htmlmin`)

Usage
-----
    usage: instantgallery.py [-h] [--title TITLE] [--language LNG] [--no-date]
                             [--no-sort] [--no-rotate] [--no-exif] [--no-gps]
                             [--web-resolution WxH] [--zip] [--sub N]
                             [--filenames] [--intro] [--no-promoting] 
                             [--zipnames SCHEMA] [--workers WORKERS] [-y] [-s]
                             [--version]
                             INPUT OUTPUT

    Builds a beautiful web gallery. Now.

    optional arguments:
      -h, --help            show this help message and exit
      --version, -v         show program's version number and exit

    Basic settings:
      INPUT                 This is directory with pictures for the gallery.
      OUTPUT                This is where the gallery should be created.
      --title TITLE, -t TITLE
                            Name the gallery
      --language LNG, -l LNG
                            Sets the language to be used in output files.
                            Available languages: en de

    Image processing:
      --no-date, -d         Prevents instantgallery.py from showing the date and
                            time of the picutres on the index page.
      --no-sort, -c         Do not try to sort the pictures chronologically. (We
                            try first to use EXIF as source for the timestamps,
                            then mtime().)
      --no-rotate, -r       Don't try to automatically rotate pictures.
      --no-exif, -e         Don't output details from EXIF data
      --no-gps, -g          Don't display GPS data (does only make sense if EXIF
                            is displayed).
      --web-resolution WxH, -w WxH
                            Specify maximal resolution for pictures shown online
                            (default: 1920x1080)

    Additional settings:
      --zip, -z             Create a zip file with all the images and make it
                            available for download.
      --sub N, -S N         Subdirectory entering depth (0 for staying in the
                            original directory).
      --filenames, -f       Display filenames in image details.
      --intro, -i           Use text file INTRO in the picture directories to
                            display on the index page.
      --no-promoting        Do not include a link to instantgallery.py's website
                            in the footer of the gallery's overview.
      --zipnames SCHEMA     Gallery name for the filenames in the zip file

    Runtime options:
      --workers WORKERS, -W WORKERS
                            Number of parallel image processing workers to spawn.
      -y                    Say yes to everything.
      -s                    Skips the generation of thumbnails and similar things.
                            THIS EXISTS FOR DEBUGGING. Use this only if you're
                            aware of what you're doing.
