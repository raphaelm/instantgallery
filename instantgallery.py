#!/usr/bin/env python
# -*- coding: utf-8 -*-
LIBDIR = '/daten/proj/instantgallery'
STATICDIR = LIBDIR+'/static'
import os
import sys
import copy
import argparse # Python 2.7!!
import shutil
import subprocess
import datetime, time
import zipfile
import hashlib
import json
from multiprocessing import Pool

# external imports 
from PIL import Image

import EXIF

if not os.path.exists(LIBDIR):
	print "Please adjust the setting LIBDIR in line 3 of instantgallery.py"
	print "It is currently set to: %s" % LIBDIR

VERSION = '2.0.5'

# Language strings
LNGLIST = ['en', 'de']
langstrings = {
	'de': {
		'back': u'zurück zur Übersicht',
		'powered': "generiert am %s mit <a href='https://github.com/raphaelm/instantgallery'>instantgallery</a> (Version %s)",
		'details': u'Bilddetails',
		'camera': u'<td>Kamera:</td><td>%s %s</td>',
		'res': u'<td>Original-Auflösung:</td><td>%dM</td>',
		'metering': u'<td>Belichtungsmessung:</td><td>%s</td>',
		'focallength': u'<td>Brennweite:</td><td>%smm</td>',
		'iso': u'<td>ISO-Zahl:</td><td>%s</td>',
		'flashfield': u'<td>Blitz:</td><td>%s</td>',
		'fnumber': u'<td>Blendenzahl:</td><td>F%s</td>',
		'exptime': u'<td>Belichtungszeit:</td><td>%ss</td>',
		'taken': u'<td>Aufgenommen:</td><td>%s</td>',
		'filename': u'<td>Dateiname:</td><td>%s</td>',
		'datetime': "%d.%m.%Y %H:%M:%S",
		'2ldatetime': "%d.%m.%Y<br />%H:%M:%S",
		'next': u'nächstes',
		'prev': u'vorheriges',
		'flash': {
			'No' : u'kein Blitz',
			'Fired' : u'ausgelöst',
			'Fired (?)': u'ausgelöst (?)',
			'Fired (!)': u'ausgelöst (!)',
			'Fill Fired': u'Fill Fired',
			'Fill Fired (?)': u'Fill Fired (?)',
			'Fill Fired (!)': u'Fill Fired (!)',
			'Off': u'aus',
			'Auto Off': u'automatisch, aus',
			'Auto Fired': u'automatisch, ausgelöst',
			'Auto Fired (?)': u'automatisch, ausgelöst (?)',
			'Auto Fired (!)': u'automatisch, ausgelöst (!)',
			'Not Available': u'nicht verfügbar'
		},
		'up': u'eine Ebene zurück',
		'top': u'oberste Ebene',
		'number': u'%d Bilder',
		'download': u'Diesen Ordner herunterladen',
		'maplnk': u'Gr&ouml;&szlig;ere Karte anzeigen',
		'OK': u'j',
	},
	'en': {
		'stats': '%d pictures &middot; generated %s',
		'back': 'back to main page',
		'powered': "generated %s using <a href='https://github.com/raphaelm/instantgallery'>instantgallery</a> Raphael Michel (Version %s)",
		'details': 'Picture details',
		'camera': '<td>Camera:</td><td>%s %s</td>',
		'res': '<td>Original resolution:</td><td>%dM</td>',
		'metering': '<td>Metering mode:</td><td>%s</td>',
		'focallength': '<td>Focal length:</td><td>%smm</td>',
		'iso': '<td>ISO:</td><td>%s</td>',
		'flashfield': '<td>Flash:</td><td>%s</td>',
		'noflash': '<td>Flash:</td><td>No flash</td>',
		'fnumber': '<td>F number:</td><td>F%s</td>',
		'exptime': '<td>Exposure time:</td><td>%ss</td>',
		'taken': '<td>Taken: </td><td>%s</td>',
		'filename': '<td>File name:</td><td>%s</td>',
		'datetime': "%m/%d/%Y %H:%M:%S",
		'2ldatetime': "%m/%d/%Y<br />%H:%M:%S",
		'next': 'next',
		'prev': 'previous',
		'flash': {
			'No' : 'No',
			'Fired' : 'Fired',
			'Fired (?)': 'Fired (?)',
			'Fired (!)': 'Fired (!)',
			'Fill Fired': 'Fill Fired',
			'Fill Fired (?)': 'Fill Fired (?)',
			'Fill Fired (!)': 'Fill Fired (!)',
			'Off': 'Off',
			'Auto Off': 'Auto Off',
			'Auto Fired': 'Auto Fired',
			'Auto Fired (?)': 'Auto Fired (?)',
			'Auto Fired (!)': 'Auto Fired (!)',
			'Not Available': 'Not Available'
		},
		'up': 'go up',
		'top': 'go to the top',
		'number': '%d pictures',
		'download': 'Download this folder',
		'maplnk': 'See larger map',
		'OK': 'y',
	}
}

# Supported formats
FORMATS = ("png", "jpg", "bmp", "jpeg", "tif", "tiff")

# Optional modules
HTMLMIN = False
try:
	from htmlmin.minify import html_minify
	HTMLMIN = True
except:
	HTMLMIN = False

def excluded(fname):
	"""True if this path should be excluded."""
	if '/.AppleDouble/' in fname:
		return True


class ImageProcessor:
	"""Callable class performing stage two image processing."""
	
	def __init__(self, options, inputd, thumbdir, picdir):
		self.options = options
		self.inputd = inputd
		self.thumbdir = thumbdir
		self.picdir = picdir
	
	def __call__(self, *args):
		try:
			self.process_image(*args)
		except KeyboardInterrupt:
			return None
	
	def process_image(self, f):
		options = self.options
		inputd = self.inputd
		thumbdir = self.thumbdir
		picdir = self.picdir
		
		fname = inputd+f[0]
		
		# Use the Python imaging library for the big images, because we
		# need to open them anyways and it is faster if we use the PIL
		# also for scaling			
		im = Image.open(fname)		
		
		# Use imagemagick's convert for creating the thumbnails because
		# it would be a pain in the ass to implement thumbnails in PIL
		# which are cropped to a square.
		cmdline = ["convert", fname, "-thumbnail", "100x100^", "-gravity", "center", "-extent", "100x100", "-quality", "80"]
		
		# Do we need to rotate the image? We do it only if the rotation
		# is noted in EXIF and the width is higher than the height (this
		# prevents from rotating a picture wich is already rotated by
		# another software without having the EXIF data changed).	
		if options.autorotate and f[2] == 'Rotated 90 CW' and im.size[0] > im.size[1]:
			im = im.rotate(-90)
			cmdline.append("-rotate")
			cmdline.append("90")
		elif options.autorotate and f[2] == 'Rotated 90 CCW' and im.size[0] > im.size[1]:
			im = im.rotate(90)
			cmdline.append("-rotate")
			cmdline.append("-90")
		
		# Save the new pictures in the corresponding directories with
		# their hashes as filename.
		cmdline.append("%s%s.jpg" % (thumbdir, f[3]))
		subprocess.Popen(cmdline).wait()
			
		webr = options.webres
		im.thumbnail((int(webr[0]), int(webr[1])), Image.ANTIALIAS)
		im.save("%s%s.jpg" % (picdir, f[3]))
		# del im # Free some RAM

def makegallery(options, sub = 0, inputd = False, outputd = False):
	# main procedure, used recursively for subdirectories
	
	global langstrings, FORMATS
	lang = langstrings[options.lang]
	
	if not outputd: outputd = options.output
	if not inputd: inputd = options.input
	
	# Argument validation
	if not inputd.endswith("/"):
		inputd += "/"
	if not outputd.endswith("/"):
		outputd += "/"
	if not os.path.exists(inputd):
		raise ValueError("%s does not exist" % inputd)
			
	if not os.path.exists(outputd):
		try:
			os.mkdir(outputd)
		except:
			raise ValueError("We were unable to create %s" % outputd)
			
	if not os.path.exists(STATICDIR+'/single.css'):
		raise ValueError("%s/single.css does not exist" % STATICDIR)
			
	if sub == 0: # Copy static files
		if os.path.exists(outputd+'static'):
			shutil.rmtree(outputd+'static')
		shutil.copytree(STATICDIR, outputd+'static')
		# Compile JavaScript files (we want only one per HTTP request!)
		singlejs = open(outputd+'static/single.comb.js', 'w')
		indexjs = open(outputd+'static/index.comb.js', 'w')
		jqueryminified = open(outputd+'static/jquery.js', 'r').read()
		singlejs.write(jqueryminified+'\n\n')
		indexjs.write(jqueryminified+'\n\n')
		singlejs.write(open(outputd+'static/jquery.ba-hashchange.min.js', 'r').read()+'\n\n')
		try: # Minify JavaScript
			from slimit import minify
			singlejs.write(minify(open(outputd+'static/jquery.hotkeys.js', 'r').read())+'\n\n')
			singlejs.write(minify(open(outputd+'static/single.js', 'r').read())+'\n\n')
			indexjs.write(minify(open(outputd+'static/index.js', 'r').read())+'\n\n')
		except:
			singlejs.write(open(outputd+'static/jquery.hotkeys.js', 'r').read()+'\n\n')
			singlejs.write(open(outputd+'static/single.js', 'r').read()+'\n\n')
			indexjs.write(open(outputd+'static/index.js', 'r').read()+'\n\n')
		singlejs.close()
		indexjs.close()
		
		try: # Minify CSS
			import cssmin
			minified = cssmin.cssmin(open(outputd+'static/index.css').read())
			indexcss = open(outputd+'static/index.css', 'w')
			indexcss.write(minified)
			indexcss.close()
			minified = cssmin.cssmin(open(outputd+'static/single.css').read())
			singlecss = open(outputd+'static/single.css', 'w')
			singlecss.write(minified)
			singlecss.close()
		except:
			pass
		
		# Yes. we copied them useless. That's life. I don't want to blacklist
		# them from rmtree nor I want to have a whitelist.
		os.remove(outputd+'static/jquery.js')
		os.remove(outputd+'static/jquery.ba-hashchange.min.js')
		os.remove(outputd+'static/single.js')
		os.remove(outputd+'static/index.js')
		
	wayback = "../"*sub
			
	# Directory creation
	htmldir = outputd
	thumbdir = outputd+"thumbs/"
	picdir = outputd+"pictures/"
	pagedir = outputd+"picpages/"
	
	title = options.title
	htmltitle = title
	
 	if sub > 0: # Set the hierarchical title for subdirectories
		n = outputd.replace(options.output, "")
		if n.endswith("/"): n = n[:-1]
		title += " "+n.replace("/", " / ")
		tparts = title.split(" / ")
		htmltitleparts = []
		ti = 0
		for f in tparts:
			fr = f.decode('utf-8').strip()
			if ti == 0:
				htmltitleparts.append(u"<a href='%sindex.html' class='back'>%s</a>" % (wayback, fr))
			elif ti == sub:
				htmltitleparts.append(fr)
			else:
				htmltitleparts.append(u"<a href='%sindex.html' class='back'>%s</a>" % (u"../"*(sub-(len(tparts)-ti-1)), fr))
			ti += 1
		htmltitle = u" / ".join(htmltitleparts)
	
	# Deleting old tuff in the selected directories
	if (os.path.exists(thumbdir) or os.path.exists(picdir) or os.path.exists(pagedir)) and not options.s:
		print "Content of the following directories will be deleted:"
		print thumbdir
		print picdir
		print pagedir
		print "Do you want to continue? [%s/N]"%lang["OK"],
		if options.yes:
			print lang["OK"]
		else:
			c = raw_input()
			
		if (options.yes or c.lower().startswith(lang["OK"])):
			shutil.rmtree(thumbdir)
			shutil.rmtree(picdir)
			shutil.rmtree(pagedir)
		else:
			print "Abort"
			sys.exit(0)
		
	# Create the directories we need if they do not exist
	if not os.path.exists(thumbdir):
		os.mkdir(thumbdir)
	if not os.path.exists(picdir):
		os.mkdir(picdir)
	if not os.path.exists(pagedir):
		os.mkdir(pagedir)
	
	# Picture scanning and resizing
	new = 0
	fnames = []
	d = os.listdir(inputd)
	dwithtimes = []
	dirs = []
	i = 0

	for f in d: # First round: All files in the input directory
		i += 1
		fname = inputd+f
		sys.stdout.write("[0] Reading file %04d of %04d (%02d%%)	\r" % (i, len(d), i*100/len(d)))
		sys.stdout.flush()

		if os.path.isdir(fname) and sub < options.sub:
			# handle a subdirectory
			print "Entering directory %s" % fname
			subdir = makegallery(options, sub+1, fname, outputd+f)
			if (subdir[1]+subdir[2]) > 0:
				dirs.append((f, subdir[0], subdir[1], subdir[3]))
		
		elif fname.lower().endswith(FORMATS) and not excluded(fname):
			# handle a picture
			try:
				if fname.lower().endswith(("jpeg", "jpg")): # supporting EXIF?
					# try to get EXIF orientation and EXIF date
					e = open(fname)
					tags = EXIF.process_file(e, details=False)
					e.close()
					ts = time.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
					o = str(tags['Image Orientation'])
				else:
					# not a jpeg: set date to files mtime and the orientation to unknown
					ts = time.localtime(os.path.getmtime(fname))
					o = False
			except:
				# fallback: set date to files mtime and the orientation to unknown
				ts = time.localtime(os.path.getmtime(fname))
				o = False
			
			if ts > new: new = ts
			
			# Use a hash of the image for the final filename
			e = open(fname)
			m = hashlib.md5()
			m.update(e.read(4096))
			# Try first 4096 bytes first. In case of two pictures with the
			# same first 4096 bytes, use the full file.
			if m.hexdigest() in [x[3] for x in dwithtimes]:
				m.update(e.read())
			ha = m.hexdigest()
			e.close()
			dwithtimes.append((f, ts, o, ha))


	if options.sort:
		d = sorted(dwithtimes, key=lambda f: f[1]) # Sort by date
	else:
		d = sorted(dwithtimes, key=lambda f: f[0]) # Sort by filename
		
	i = 0
	images = []
	for f in d: # Second round. Again all files but only handling images.
		i += 1
		fname = inputd+f[0]
		if fname.lower().endswith(FORMATS) and not excluded(fname):
			fnames.append(fname)
			if options.s:
				continue
			images += [f]

	# and do the processing.
	pool = Pool(processes=args.workers)
	for im in images:
		# TODO: skip if exists and do-not-overwite.
		pool.apply_async( ImageProcessor(options, inputd, thumbdir, picdir), (im,))
	pool.close()
	pool.join()
			
	# html generation
	for j in xrange(1, i+1): # Third round, this time images only!
		sys.stdout.write("[2] Processing picture %04d of %04d (%02d%%)	 \r" % (j, i, j*100/i))
		sys.stdout.flush()
			
		# We also build a JSON file to make AJAX possible
		helper = {}
		
		# HTML heder
		html = u"""<!DOCTYPE html>
					<html>
					<head>
						<title>%s</title>
						<meta http-equiv="content-type" content="text/html;charset=utf-8" />
						<meta name="generator" content="instantgallery.py %s" />
						<script type="text/javascript" src="../%sstatic/single.comb.js"></script>
						<link rel="stylesheet" href="../%sstatic/single.css" type="text/css" />
					</head>

					<body>
						""" % (title.decode('utf-8'), VERSION, wayback, wayback)

		if j > 1: # "previous" link
			html += (u'<a href="%s.html" class="thumb" id="prev"><img src="../thumbs/%s.jpg" alt="" /><span>'+lang['prev']+'</span></a> ') % (d[j-2][3], d[j-2][3])
			helper['prev'] = d[j-2][3]
		else: # ajax stuff
			html += u'<a class="thumb" id="prev" style="display: none;"><img /><span>'+lang['prev']+'</span></a>'
			helper['prev'] = False
			
		html += u'<div id="loading"></div>'
		html += u'<img src="../pictures/%s.jpg" alt="" id="main" />' % d[j-1][3] # the picture itself
		html += u'<img id="shift" /><img id="shift2" />' # ajax stuff
		helper['current'] = d[j-1][3]
		
		if j < i: # "next" link
			html += (u' <a href="%s.html" class="thumb" id="next"><img src="../thumbs/%s.jpg" alt="" /><span>'+lang['next']+'</span></a>') % (d[j][3], d[j][3])
			helper['next'] = d[j][3]
		else: # ajax stuff
			html += u'<a class="thumb" id="next" style="display: none;"><img /><span>'+lang['next']+'</span></a>'
			helper['next'] = False
			
		html += u"<br /><a href='../index.html' id='back'>"+lang["back"]+"</a>" # the link back to the index
		
		exifhtmlsnipp = u"<div id='exifarea'></div>"
		helper['exifhtml'] = False
		
		fname = fnames[j-1]
		if fname.endswith(("jpeg", "JPEG", "jpg", "JPG")) and options.exif:
			# We wanna display some EXIF data because that rocks!
			
			# We could use the data parsed already but we do not want to
			# keep all the tags of all photos in RAM when using the script
			# for large galleries
			e = open(fname)
			tags = EXIF.process_file(e, details=False)
			e.close()
			taghtml = []
			if len(tags) > 2: # do we HAVE tags?
				# Check if we want to parse GPS and if we have GPS data
				gps = (options.gps and ('GPS GPSLatitude' in tags))
				if gps:
					exifhtml = u"<div class='exif'>"
				else:
					exifhtml = u"<div class='exif exifsmall'>"
					
				exifhtml += u"<table><tr><th colspan='2'>"+lang["details"]+"</th></tr><tr>"
				
				if options.filenames:
					exifhtml += (lang['filename']+"</tr><tr>") % os.path.basename(fname)
				
				# Parse the EXIF tags
				if 'EXIF DateTimeOriginal' in tags:
					# Date. We want it in the prefered notation of our locale.
					try:
						tv = str(tags['EXIF DateTimeOriginal'])
						if tv != '0000:00:00 00:00:00':
							dt = time.strptime(tv, "%Y:%m:%d %H:%M:%S")
							taghtml.append(lang['taken'] % time.strftime(lang['datetime'], dt))
					except ValueError, e: # invalid date stored in photo:
						sys.stderr.write("%s: skipped invalid date (%s)\n" % (fname, e))
				if 'EXIF ExposureTime' in tags:
					tv = tags['EXIF ExposureTime']
					if tv.values[0].den == 2 or tv.values[0].den == 5 or tv.values[0].den == 10:
						# We want 3.5 instead of 7/2 but 1/60 instead of 0,0167
						tv = float(tv.values[0].num)/float(tv.values[0].den)
					taghtml.append(lang['exptime'] % tv)
				if 'EXIF FNumber' in tags:
					tv = tags['EXIF FNumber']
					if tv.values[0].den == 2 or tv.values[0].den == 5 or tv.values[0].den == 10:
						tv = float(tv.values[0].num)/float(tv.values[0].den)
					taghtml.append(lang['fnumber'] % tv)
				if 'EXIF Flash' in tags:
					fl = str(tags['EXIF Flash'])
					if fl in lang['flash']:
						# We translate the values :-)
						taghtml.append(lang['flashfield'] % lang['flash'][fl])
				if 'EXIF ISOSpeedRatings' in tags:
					taghtml.append(lang['iso'] % tags['EXIF ISOSpeedRatings'])
				if 'EXIF FocalLength' in tags:
					tv = tags['EXIF FocalLength']
					if tv.values[0].den == 2 or tv.values[0].den == 5 or tv.values[0].den == 10:
						tv = float(tv.values[0].num)/float(tv.values[0].den)
					taghtml.append(lang['focallength'] % tv)
				if 'EXIF MeteringMode' in tags:
					taghtml.append(lang['metering'] % tags['EXIF MeteringMode'])
				if 'EXIF ExifImageLength' in tags:
					# We want to show the number of megapixels instead of the exact width and height
					mp = int(str(tags['EXIF ExifImageLength']))*int(str(tags['EXIF ExifImageWidth']))/1000000
					taghtml.append(lang['res'] % mp)
				if 'Image Make' in tags and 'Image Model' in tags:
					taghtml.append(lang['camera'] % (tags['Image Make'], tags['Image Model']))
									
				exifhtml += u"</tr><tr>".join(taghtml)
					
				if gps:
					# Now parse the GPS stuff
					lat = [float(x.num/x.den) for x in tags['GPS GPSLatitude'].values]
					latr = str(tags['GPS GPSLatitudeRef'].values)
					lon = [float(x.num/x.den) for x in tags['GPS GPSLongitude'].values]
					lonr = str(tags['GPS GPSLongitudeRef'].values)
					
					lat = (lat[2]/60.0 + lat[1])/60.0 + lat[0]
					lon = (lon[2]/60.0 + lon[1])/60.0 + lon[0]
					if latr == 'S': lat = lat * (-1)
					if lonr == 'W': lon = lon * (-1)
					
					# Display openstreetmap map
					ex = 0.01 # degrees we want to show around in each direction
					exifhtml += u'</tr><tr><td colspan="2" style="text-align: center">'
					exifhtml += u'<iframe frameborder="0" height="350" marginheight="0" marginwidth="0" scrolling="no" src="http://www.openstreetmap.org/export/embed.html?bbox=%s,%s,%s,%s&amp;layer=mapnik&amp;marker=%s,%s" style="border: 1px solid black" width="440" id="map"></iframe><br />' % (lon-ex, lat-ex, lon+ex, lat+ex, lat, lon)
					exifhtml += u'<small><a href="http://www.openstreetmap.org/?lat=%s&amp;lon=%s&amp;zoom=15" target="_blank">%s</a></small></td>' % (lat, lon, lang['maplnk'])
				
				exifhtml += u"</tr></table></div>"
				exifhtmlsnipp = u"<div id='exifarea'>%s</div>" % exifhtml
				helper['exifhtml'] = exifhtml
				
		elif options.filenames:
			exifhtml = u"<div class='exif exifsmall'>"
			exifhtml += u"<table><tr><th colspan='2'>"+lang["details"]+"</th></tr><tr>"
			exifhtml += lang['filename'] % os.path.basename(fname)
			exifhtml += u"</tr></table></div>"
			exifhtmlsnipp = u"<div id='exifarea'>%s</div>" % exifhtml
			helper['exifhtml'] = exifhtml
				
		html += exifhtmlsnipp
		
		helperjson = json.dumps(helper)
		helperfile = open("%s%s.json" % (pagedir, d[j-1][3]), "w")
		helperfile.write(helperjson)
		helperfile.close()
		
		html += u"<script type='text/javascript'>\nvar current = %s; var original = current;\n</script>" % helperjson
		html += u"</body></html>"
		
		if HTMLMIN:
			html = html_minify(html.encode('utf-8'))
		
		# save the HTML file
		f = open("%s%s.html" % (pagedir.decode('utf-8'), d[j-1][3]), "w")
		f.write(html.encode('utf-8'))
		f.close()
		
	# Generate a zip file
	if options.zip:
		sys.stdout.write("[4] Generating ZIP file			\r")
		z = zipfile.ZipFile("%sphotos.zip" % (picdir,), "w")
		for j in xrange(1, i+1):
			if options.zipnames:
				z.write("%s%s.jpg" % (picdir, d[j-1][3]), "%04d-%s.jpg" % (j, options.zipnames))
			else:
				z.write("%s%s.jpg" % (picdir, d[j-1][3]), "%04d-%s.jpg" % (j, d[j-1][3]))

		z.close()
		
	# Generate the index page
	sys.stdout.write("[3] Generating index			\r")
	sys.stdout.flush()
		
	# HTML head
	html = u"""<!DOCTYPE html>
				<html>
				<head>
					<title>%s</title>
					<meta http-equiv="content-type" content="text/html;charset=utf-8" />
					<meta name="generator" content="instantgallery.py %s" />
					<link rel="stylesheet" href="%sstatic/index.css" type="text/css" />
					<script type="text/javascript" src="%sstatic/index.comb.js"></script>
				</head>

				<body><h1>%s""" % (title.decode('utf-8'), VERSION, wayback, wayback, htmltitle)

	#""" # we don't need to display the link "one directory up" since we linked the headline
	#if sub == 1:
	#	html += "   <small><a href='../index.html'>"+lang['up']+"</a>"
	#	if options.zip:
	#		html += " &middot; "
	#elif sub > 1:
	#	html += "   <small><a href='../index.html'>"+lang['up']+"</a> &middot; <a href='"+wayback+"index.html'>"+lang['top']+'</a>'
	#	if options.zip:
	#		html += " &middot; "
	#elif options.zip:
	#	html += "   <small>" """
		
	# display zip download links
	if options.zip and i > 0:
		html += u"   <small><a href='pictures/photos.zip'>"+lang['download']+'</a></small>'
	html += u"</h1>"
	
	# if -i is specified and there is a file INTRO in the photo directory
	# we want to show it! :-)
	if options.intro:
		introfile = inputd+"/INTRO"
		if os.path.exists(introfile) and os.path.isfile(introfile):
			introf = open(introfile)
			intro = introf.read()
			introf.close()
			html += u"<p>%s</p>" % intro.replace("\n\n", "</p><p>").replace("\n", "<br />")
		
	if len(dirs) > 0:
		if options.sort:
			dirs = sorted(dirs, key=lambda f: f[1]) # by date
		else:
			dirs = sorted(dirs, key=lambda f: f[0]) # by directory name
			
		for directory in dirs: # output ALL the directories
			directory = [ ( _d.decode('utf-8') if type(_d) in (str, unicode) else _d ) for _d in directory ]
			html += '<a href="%s/index.html" class="thumb dir' % directory[0]
			if directory[3]:
				thumbpath = "%s/thumbs/%s.jpg"%(directory[0],directory[3])
			else:
				thumbpath="static/blank.png"
			html += '" rel="%s"><img rel="%s" src="%s" alt="" />' % (directory[3],directory[0],thumbpath)
			html += '<span>%s<br/>%s</span>'%( directory[0], (lang["number"]%directory[2]) )
			html += '</a>'
	
	for j in xrange(1, i+1): # output ALL the files
		html += u'<a href="picpages/%s.html" class="thumb"><img src="thumbs/%s.jpg" alt="" />' % (d[j-1][3],d[j-1][3])
		if options.displaydate:
			html += u'<span>'+time.strftime(lang['2ldatetime'], d[j-1][1])+u'</span>'
		html += u'</a> '
		
	# promote this software
	if options.promote:
		html += (u"<div class='poweredby'>"+lang['powered']+"</div>") % (datetime.date.today().strftime("%d.%m.%Y"), VERSION)
	html += u"</body></html>"
	if HTMLMIN:
		html = html_minify(html.encode('utf-8'))
	f = open(u"%sindex.html" % (htmldir.decode('utf-8')), "w")
	f.write(html.encode('utf-8'))
	f.close() # have fun
	
	if len(d) > 0:
		first = d[0][3]
	else:
		first = None
	return (new, i, len(dirs), first)
	
# parse arguments	
def resolution(string):
	try:
		vals = string.lower().split("x")
		val1 = int(vals[0])
		val2 = int(vals[1])
	except:
		val1 = 0
		val2 = 0
		
	if val1 < 1 or val2 < 1:
		raise argparse.ArgumentTypeError("Please specify two integers, connected by 'x'")
	else:
		return (val1, val2)
	
parser = argparse.ArgumentParser(description='Builds a beautiful web gallery. Now.')
group1 = parser.add_argument_group('Basic settings')
group1.add_argument('input', metavar='INPUT', type=str,
                   help='This is directory with pictures for the gallery.')
group1.add_argument('output', metavar='OUTPUT', type=str,
                   help='This is where the gallery should be created.')
group1.add_argument('--title', '-t', metavar='TITLE', type=str, default='Image Gallery',
                   help='Name the gallery')
group1.add_argument('--language', '-l', metavar='LNG', type=str, default='en',
                   help='Sets the language to be used in output files. Available languages:\n'+' '.join(LNGLIST), dest='lang', choices=LNGLIST)
group2 = parser.add_argument_group('Image processing')
group2.add_argument('--no-date', '-d', action="store_false", dest='displaydate',
                   help='Prevents instantgallery.py from showing the date and time of the picutres on the index page.')
group2.add_argument('--no-sort', '-c', action='store_false', dest='sort',
                   help='Do not try to sort the pictures chronologically. (We try first to use EXIF as source for the timestamps, then mtime().)')
group2.add_argument('--no-rotate', '-r', action='store_false', dest='autorotate',
                   help='Don\'t try to automatically rotate pictures.')
group2.add_argument('--no-exif', '-e', action='store_false', dest='exif',
                   help='Don\'t output details from EXIF data')
group2.add_argument('--no-gps', '-g', action="store_false", dest='gps',
                   help='Don\'t display GPS data (does only make sense if EXIF is displayed).')
group2.add_argument('--web-resolution', '-w', dest='webres', type=resolution, metavar='WxH', default=(1920,1080),
                   help='Specify maximal resolution for pictures shown online (default: 1920x1080)')
group3 = parser.add_argument_group('Additional settings')
group3.add_argument('--zip', '-z', action="store_true", dest='zip',
                   help='Create a zip file with all the images and make it available for download.')
group3.add_argument('--sub', '-S', type=int, dest='sub', default=63, metavar='N',
                   help='Subdirectory entering depth (0 for staying in the original directory).')
group3.add_argument('--filenames', '-f', dest='filenames', action="store_true",
                   help='Display filenames in image details.')
group3.add_argument('--intro', '-i', dest='intro', action='store_true',
                   help='Use text file INTRO in the picture directories to display on the index page.')
group3.add_argument('--no-promoting', dest='promote', action='store_false',
                   help='Do not include a link to instantgallery.py\'s website in the footer of the gallery\'s overview.')
group3.add_argument('--zipnames', dest='zipnames', type=str, default=False, metavar='SCHEMA',
                   help='Gallery name for the filenames in the zip file')
group4 = parser.add_argument_group('Runtime options')
group4.add_argument('--workers', '-W', metavar="WORKERS", type=int, default='4',
                   help='Number of parallel image processing workers to spawn.')
group4.add_argument('-y', action="store_true", dest='yes',
                   help='Say yes to everything.')
group4.add_argument('-s', action="store_true", dest='s',
                   help='Skips the generation of thumbnails and similar things. THIS EXISTS FOR DEBUGGING. Use this only if you\'re aware of what you\'re doing.')
parser.add_argument('--version', '-v', action='version', version='%(prog)s '+VERSION)
args = parser.parse_args()
	
if args.title == 'Image Gallery':
	print 'Warning! You\'re creating a gallery without a title. We will use "Image Gallery" as default title!'
	print 'Specify a title with --title/-t and run this command again, if you\'re not good with this.'
	print 'If you don\'t want to interrupt this command, let it finish and run the command with -t and -s the next time to save time.'


makegallery(args)
