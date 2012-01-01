#!/usr/bin/env python
# -*- coding: utf-8 -*-
LIBDIR = '/home/raphael/proj/instantgallery'

import os
import sys
import copy
import argparse # Python 2.7!!
import shutil
import subprocess
import datetime, time

from PIL import Image

import EXIF

VERSION = '1.2.0dev'
LNGLIST = ['en', 'de']
langstrings = {
	'de': {
		'back': 'zurück zur Übersicht',
		'powered': "generiert am %s mit <a href='https://github.com/raphaelm/instantgallery'>instantgallery</a> von Raphael Michel (Version %s)",
		'details': 'Bilddetails',
		'camera': '<td>Kamera:</td><td>%s %s</td>',
		'res': '<td>Original-Auflösung:</td><td>%dM</td>',
		'metering': '<td>Belichtungsmessung:</td><td>%s</td>',
		'focallength': '<td>Brennweite:</td><td>%smm</td>',
		'iso': '<td>ISO-Zahl:</td><td>%s</td>',
		'flashfield': '<td>Blitz:</td><td>%s</td>',
		'fnumber': '<td>Blendenzahl:</td><td>F%s</td>',
		'exptime': '<td>Belichtungszeit:</td><td>%ss</td>',
		'taken': '<td>Aufgenommen:</td><td>%s</td>',
		'datetime': "%d.%m.%Y %H:%M:%S",
		'2ldatetime': "%d.%m.%Y<br />%H:%M:%S",
		'next': 'nächstes',
		'prev': 'vorheriges',
		'flash': {
              'No' : 'kein Blitz',
              'Fired' : 'ausgelöst',
              'Fired (?)': 'ausgelöst (?)',
              'Fired (!)': 'ausgelöst (!)',
              'Fill Fired': 'Fill Fired',
              'Fill Fired (?)': 'Fill Fired (?)',
              'Fill Fired (!)': 'Fill Fired (!)',
              'Off': 'aus',
              'Auto Off': 'automatisch, aus',
              'Auto Fired': 'automatisch, ausgelöst',
              'Auto Fired (?)': 'automatisch, ausgelöst (?)',
              'Auto Fired (!)': 'automatisch, ausgelöst (!)',
              'Not Available': 'nicht verfügbar'
		},
		'up': 'eine Ebene zurück',
		'top': 'oberste Ebene',
		'number': '%d Bilder'
	},
	'en': {
		'stats': '%d pictures &middot; generated %s',
		'back': 'back to main page',
		'powered': "generated %s using <a href='https://github.com/raphaelm/instantgallery'>instantgallery</a> by Raphael Michel (version %s)",
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
		'up': 'up',
		'top': 'top',
		'number': '%d pictures'
	}
}
FORMATS = ("png", "PNG", "jpg", "JPG", "bmp", "BMP", "jpeg", "JPEG", "tif", "TIF", "tiff", "TIFF")

def makegallery(options, sub = 0, inputd = False, outputd = False):
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
			
	if not os.path.exists(LIBDIR+'/single.css'):
		raise ValueError("%s does not exist" % LIBDIR)
			
	if sub == 0:
		shutil.copy(LIBDIR+'/single.css', outputd+'single.css')
		shutil.copy(LIBDIR+'/index.css', outputd+'index.css')
		shutil.copy(LIBDIR+'/jquery.js', outputd+'jquery.js')
		shutil.copy(LIBDIR+'/single.js', outputd+'single.js')
		shutil.copy(LIBDIR+'/index.js', outputd+'index.js')
		shutil.copy(LIBDIR+'/loading.gif', outputd+'loading.gif')
		shutil.copy(LIBDIR+'/Ubuntu.woff', outputd+'Ubuntu.woff')
			
	wayback = "../"*sub
			
	# Directory creation
	htmldir = outputd
	thumbdir = outputd+"thumbs/"
	picdir = outputd+"pictures/"
	pagedir = outputd+"picpages/"
	
	title = options.title
	if sub > 0:
		n = outputd.replace(options.output, "")
		if n.endswith("/"): n = n[:-1]
		title += " "+n.replace("/", " / ")
	
	if (os.path.exists(thumbdir) or os.path.exists(picdir) or os.path.exists(pagedir)) and not options.s:
		print "Content of the following directories will be deleted:"
		print thumbdir
		print picdir
		print pagedir
		print "Do you want to continue? [y/N]",
		if options.yes:
			print "y"
		else:
			c = raw_input()
			
		if (options.yes or c.startswith(("y", "j", "Y", "J"))):
			shutil.rmtree(thumbdir)
			shutil.rmtree(picdir)
			shutil.rmtree(pagedir)
		else:
			print "Abort"
			sys.exit(0)
		
	if not os.path.exists(thumbdir):
		try:
			os.mkdir(thumbdir)
		except:
			raise ValueError("We were unable to write in the output directory")
	if not os.path.exists(picdir):
		try:
			os.mkdir(picdir)
		except:
			raise ValueError("We were unable to write in the output directory")
	if not os.path.exists(pagedir):
		try:
			os.mkdir(pagedir)
		except:
			raise ValueError("We were unable to write in the output directory")
			
	# Picture scanning and resizing
	new = 0
	fnames = [None]
	d = os.listdir(inputd)
	dwithtimes = []
	dirs = []
	if options.sort:
		for f in d:
			fname = inputd+f
			
			if os.path.isdir(fname) and sub < options.sub:
				# Subdirectory
				print "Entering directory %s" % fname
				subdir = makegallery(options, sub+1, fname, outputd+f)
				if (subdir[1]+subdir[2]) > 0:
					dirs.append((f, subdir[0], subdir[1]))
							
			elif fname.endswith(FORMATS):
				try:
					if fname.endswith(("jpeg", "JPEG", "jpg", "JPG")):
						e = open(fname)
						tags = EXIF.process_file(e, details=False)
						e.close()
						ts = time.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
						o = str(tags['Image Orientation'])
					else:
						ts = time.localtime(os.path.getmtime(fname))
						o = False
				except:
					ts = time.localtime(os.path.getmtime(fname))
					o = False
				if ts > 0: new = ts
				dwithtimes.append((f, ts, o))
		d = sorted(dwithtimes, key=lambda f: f[1])
	else:
		d.sort()
			
	i = 1
	for f in d:
		fname = inputd+f[0]
		sys.stdout.write("[1] Processing file %04d of %04d (%02d%%)       \r" % (i, len(d), i*100/len(d)))
		sys.stdout.flush()
		if fname.endswith(FORMATS):
			fnames.append(fname)
			if options.s:
				i += 1
				continue
						
			im = Image.open(fname)			
			cmdline = ["convert", fname, "-thumbnail", "100x100^", "-gravity", "center", "-extent", "100x100", "-quality", "80"]
			if options.autorotate and f[2] == 'Rotated 90 CW' and im.size[0] > im.size[1]:
				im = im.rotate(-90)
				cmdline.append("-rotate")
				cmdline.append("90")
			elif options.autorotate and f[2] == 'Rotated 90 CCW' and im.size[0] > im.size[1]:
				im = im.rotate(90)
				cmdline.append("-rotate")
				cmdline.append("-90")
			cmdline.append("%s%08d.jpg" % (thumbdir, i))
			subprocess.Popen(cmdline).wait()
				
			im.thumbnail((1920,1080), Image.ANTIALIAS)
			im.save("%s%08d.jpg" % (picdir, i))
			del im
			i += 1
			
	# html generation
	for j in xrange(1, i):
		sys.stdout.write("[2] Processing picture %04d of %04d (%02d%%)         \r" % (j, i, j*100/i))
		sys.stdout.flush()
		html = """<!DOCTYPE html>
					<html>
					<head>
						<title>%s</title>
						<meta http-equiv="content-type" content="text/html;charset=utf-8" />
						<script type="text/javascript" src="../%sjquery.js"></script>
						<script type="text/javascript" src="../%ssingle.js"></script>
						<script type="text/javascript">
						$(document).ready(function(){
							i = new Image();
							i.src = "../pictures/%08d.jpg";
							i = new Image();
							i.src = "../thumbs/%08d.jpg";
							i = new Image();
							i.src = "../thumbs/%08d.jpg";
						});
						</script>
						<link rel="stylesheet" href="../%ssingle.css" type="text/css" />
					</head>

					<body>
						""" % (title, wayback, wayback, j+1, j, j+2, wayback)
		if j > 1:
			html += ('<a href="%08d.html" class="thumb" id="prev"><img src="../thumbs/%08d.jpg" alt="" /><span>'+lang['prev']+'</span></a> ') % (j-1, j-1)
		html += '<img src="../pictures/%08d.jpg" alt="" id="main" />' % j
		if j < i-1:
			html += (' <a href="%08d.html" class="thumb" id="next"><img src="../thumbs/%08d.jpg" alt="" /><span>'+lang['next']+'</span></a>') % (j+1, j+1)
			
		html += "<br /><a href='../index.html' id='back'>"+lang["back"]+"</a>"
		fname = fnames[j]
		if fname.endswith(("jpeg", "JPEG", "jpg", "JPG")) and options.exif:
			e = open(fname)
			tags = EXIF.process_file(e, details=False)
			e.close()
			taghtml = []
			
			gps = (options.gps and ('GPS GPSLatitude' in tags))
			if gps:
				html += "<div class='exif'>"
			else:
				html += "<div class='exif exifsmall'>"
			html += "<table><tr><th colspan='2'>"+lang["details"]+"</th></tr><tr>"
			
			if 'EXIF DateTimeOriginal' in tags:
				tv = str(tags['EXIF DateTimeOriginal'])
				if tv != '0000:00:00 00:00:00':
					dt = time.strptime(tv, "%Y:%m:%d %H:%M:%S")
					taghtml.append(lang['taken'] % time.strftime(lang['datetime'], dt))
			if 'EXIF ExposureTime' in tags:
				tv = tags['EXIF ExposureTime']
				if tv.values[0].den == 2 or tv.values[0].den == 5:
					tv = float(tv.values[0].num)/float(tv.values[0].den)
				taghtml.append(lang['exptime'] % tv)
			if 'EXIF FNumber' in tags:
				tv = tags['EXIF FNumber']
				if tv.values[0].den == 2 or tv.values[0].den == 5:
					tv = float(tv.values[0].num)/float(tv.values[0].den)
				taghtml.append(lang['fnumber'] % tv)
			if 'EXIF Flash' in tags:
				fl = str(tags['EXIF Flash'])
				if fl in lang['flash']:
					taghtml.append(lang['flashfield'] % lang['flash'][fl])
			if 'EXIF ISOSpeedRatings' in tags:
				taghtml.append(lang['iso'] % tags['EXIF ISOSpeedRatings'])
			if 'EXIF FocalLength' in tags:
				tv = tags['EXIF FocalLength']
				if tv.values[0].den == 2 or tv.values[0].den == 5:
					tv = float(tv.values[0].num)/float(tv.values[0].den)
				taghtml.append(lang['focallength'] % tv)
			if 'EXIF MeteringMode' in tags:
				taghtml.append(lang['metering'] % tags['EXIF MeteringMode'])
			if 'EXIF ExifImageLength' in tags:
				mp = int(str(tags['EXIF ExifImageLength']))*int(str(tags['EXIF ExifImageWidth']))/1000000
				taghtml.append(lang['res'] % mp)
			if 'Image Make' in tags and 'Image Model' in tags:
				taghtml.append(lang['camera'] % (tags['Image Make'], tags['Image Model']))
								
			html += "</tr><tr>".join(taghtml)
				
			if gps:
				lat = [float(x.num/x.den) for x in tags['GPS GPSLatitude'].values]
				latr = str(tags['GPS GPSLatitudeRef'].values)
				lon = [float(x.num/x.den) for x in tags['GPS GPSLongitude'].values]
				lonr = str(tags['GPS GPSLongitudeRef'].values)
				
				lat = (lat[2]/60.0 + lat[1])/60.0 + lat[0]
				lon = (lon[2]/60.0 + lon[1])/60.0 + lon[0]
				if latr == 'S': lat = lat * (-1)
				if lonr == 'W': lon = lon * (-1)
				
				ex = 0.01
				html += '</tr><tr><td colspan="2" style="text-align: center">'
				html += '<iframe frameborder="0" height="350" marginheight="0" marginwidth="0" scrolling="no" src="http://www.openstreetmap.org/export/embed.html?bbox=%s,%s,%s,%s&amp;layer=mapnik&amp;marker=%s,%s" style="border: 1px solid black" width="440" id="map"></iframe><br />' % (lon-ex, lat-ex, lon+ex, lat+ex, lat, lon)
				html += '<small><a href="http://www.openstreetmap.org/?lat=%s&amp;lon=%s&amp;zoom=15" target="_blank">Gr&ouml;&szlig;ere Karte anzeigen</a></small></td>' % (lat, lon)
			
			html += "</tr></table></div>"
				
		html += "</body></html>"
		f = open("%s%08d.html" % (pagedir, j), "w")
		f.write(html)
		f.close()
	
	# index page
	sys.stdout.write("[3] Generating index                       \r")
	sys.stdout.flush()
	
	html = ("""<!DOCTYPE html>
				<html>
				<head>
					<title>%s</title>
					<meta http-equiv="content-type" content="text/html;charset=utf-8" />
					<link rel="stylesheet" href="%sindex.css" type="text/css" />
					<script type="text/javascript" src="%sjquery.js"></script>
					<script type="text/javascript" src="%sindex.js"></script>
				</head>

				<body><h1>%s""") % (title, wayback, wayback, wayback, title)
	if sub == 1:
		html += "   <small><a href='../index.html'>"+lang['up']+"</a></small>"
	elif sub > 1:
		html += "   <small><a href='../index.html'>"+lang['up']+"</a> &middot; <a href='"+wayback+"index.html'>"+lang['top']+'</a></small>'
	html += "</h1>"
	
	if len(dirs) > 0:
		if options.sort:
			dirs = sorted(dirs, key=lambda f: f[1])
		else:
			dirs = sorted(dirs, key=lambda f: f[0])
			
		for directory in dirs:
			html += '<a href="%s/index.html" class="thumb dir' % directory[0]
			if options.hoverscrolling:
				html += ' anim'
			html += '" rel="%d"><img rel="%s" src="%s/thumbs/00000001.jpg" alt="" />' % (directory[2],directory[0],directory[0])
			html += '<span>'+directory[0]+'<br />'+(lang["number"] % directory[2])+'</span>'
			html += '</a> '
			
	for j in xrange(1, i):
		html += '<a href="picpages/%08d.html" class="thumb"><img src="thumbs/%08d.jpg" alt="" />' % (j,j)
		if options.displaydate:
			html += '<span>'+time.strftime(lang['2ldatetime'], d[j-1][1])+'</span>'
		html += '</a> '
		
	html += ("<div class='poweredby'>"+lang['powered']+"</div>") % (datetime.date.today().strftime("%d.%m.%Y"), VERSION)
	html += "</body></html>"
	f = open("%sindex.html" % (htmldir), "w")
	f.write(html)
	f.close()
	return (new, i-1, len(dirs))
	
# parse arguments		
parser = argparse.ArgumentParser(description='Makes a gallery. Now.')
parser.add_argument('input', metavar='INPUT', type=str,
                   help='This is directory with pictures for the gallery.')
parser.add_argument('output', metavar='OUTPUT', type=str,
                   help='Sets where the gallery should be created.')
parser.add_argument('--title', '-t', metavar='TITLE', type=str, default='Image Gallery',
                   help='Sets the title of the gallery')
parser.add_argument('--language', '-l', metavar='LNG', type=str, default='en',
                   help='Sets the language to be used in output files. Available languages:\n'+' '.join(LNGLIST), dest='lang', choices=LNGLIST)
parser.add_argument('--no-exif', '-e', action='store_false', dest='exif',
                   help='don\'t output details from EXIF data')
parser.add_argument('--no-rotate', '-r', action='store_false', dest='autorotate',
                   help='Don\'t try to automatically rotate pictures.')
parser.add_argument('--no-sort', '-c', action='store_false', dest='sort',
                   help='Do not try to sort the pictures chronologically. (We try first to use EXIF as source for the timestamps, then mtime().)')
parser.add_argument('--no-date', '-d', action="store_false", dest='displaydate',
                   help='Prevents instantgallery.py from showing the date and time of the picutres on the index page.')
parser.add_argument('--no-gps', '-g', action="store_false", dest='gps',
                   help='Don\'t display GPS data (does only make sense if EXIF is displayed).')
parser.add_argument('--sub', '-S', type=int, dest='sub', default=63, metavar='N',
                   help='Subdirectory entering depth (0 for staying in the original directory).')
parser.add_argument('--hoverscrolling', dest='hoverscrolling', action='store_true',
                   help='An effect for subdirectories. Was intended to look nicer than it acutally does.')
parser.add_argument('-y', action="store_true", dest='yes',
                   help='Say yes to everything.')
parser.add_argument('-s', action="store_true",
                   help='Skips the generation of thumbnails and similar things. Use this only if you\'re aware of what you\'re doing.')
args = parser.parse_args()

makegallery(args)
