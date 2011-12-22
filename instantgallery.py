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

VERSION = '11/12/22'
LNGLIST = ['en', 'de']
langstrings = {
	'de': {
		'stats': '%d Bilder &middot; generiert am %s',
		'back': 'zurück zur Übersicht',
		'powered': "generiert mit <a href='https://github.com/raphaelm/instantgallery'>instantgallery</a> von Raphael Michel (Version %s)" % VERSION,
		'details': 'Bilddetails',
		'camera': '<td>Kamera:</td><td>%s %s</td>',
		'res': '<td>Original-Auflösung:</td><td>%dM</td>',
		'metering': '<td>Belichtungsmessung:</td><td>%s</td>',
		'focallength': '<td>Brennweite:</td><td>%smm</td>',
		'iso': '<td>ISO-Zahl:</td><td>%s</td>',
		'flash': '<td>Blitz:</td><td>%s</td>',
		'noflash': '<td>Blitz:</td><td>ohne Blitz</td>',
		'fnumber': '<td>Blendenzahl:</td><td>F%s</td>',
		'exptime': '<td>Belichtungszeit:</td><td>%ss</td>',
		'taken': '<td>Aufgenommen:</td><td>%s</td>',
		'datetime': "%d.%m.%Y %H:%M:%S",
		'2ldatetime': "%d.%m.%Y<br />%H:%M:%S",
		'next': 'nächstes',
		'prev': 'vorheriges'
	},
	'en': {
		'stats': '%d pictures &middot; generated %s',
		'back': 'back to main page',
		'powered': "generated using <a href='https://github.com/raphaelm/instantgallery'>instantgallery</a> by Raphael Michel (version %s)" % VERSION,
		'details': 'Picture details',
		'camera': '<td>Camera:</td><td>%s %s</td>',
		'res': '<td>Original resolution:</td><td>%dM</td>',
		'metering': '<td>Metering mode:</td><td>%s</td>',
		'focallength': '<td>Focal length:</td><td>%smm</td>',
		'iso': '<td>ISO:</td><td>%s</td>',
		'flash': '<td>Flash:</td><td>%s</td>',
		'noflash': '<td>Flash:</td><td>No flash</td>',
		'fnumber': '<td>F number:</td><td>F%s</td>',
		'exptime': '<td>Exposure time:</td><td>%ss</td>',
		'taken': '<td>Taken: </td><td>%s</td>',
		'datetime': "%m/%d/%Y %H:%M:%S",
		'2ldatetime': "%m/%d/%Y<br />%H:%M:%S",
		'next': 'next',
		'prev': 'previous'
	}
}
FORMATS = ("png", "PNG", "jpg", "JPG", "bmp", "BMP", "jpeg", "JPEG", "tif", "TIF", "tiff", "TIFF")

def makegallery(options):
	global langstrings, FORMATS
	lang = langstrings[options.lang]
	
	# Argument validation
	if not options.input.endswith("/"):
		options.input += "/"
	if not options.output.endswith("/"):
		options.output += "/"
	if not os.path.exists(options.input):
		raise ValueError("%s does not exist" % options.input)
			
	if not os.path.exists(options.output):
		try:
			os.mkdir(options.output)
		except:
			raise ValueError("We were unable to create %s" % options.output)
			
	if not os.path.exists(LIBDIR+'/single.css'):
		raise ValueError("%s does not exist" % LIBDIR)
			
	shutil.copy(LIBDIR+'/single.css', options.output+'single.css')
	shutil.copy(LIBDIR+'/index.css', options.output+'index.css')
	shutil.copy(LIBDIR+'/jquery.js', options.output+'jquery.js')
	shutil.copy(LIBDIR+'/single.js', options.output+'single.js')
			
	# Picture creation
	htmldir = options.output
	thumbdir = options.output+"thumbs/"
	picdir = options.output+"pictures/"
	pagedir = options.output+"picpages/"
	
	if os.path.exists(thumbdir) or os.path.exists(picdir) or os.path.exists(pagedir):
		print "Content of the following directories will be deleted:"
		print thumbdir
		print picdir
		print pagedir
		print "Do you want to continue? [y/N]",
		if options.yes:
			print "y"
		else:
			c = raw_input()
			
		if (options.yes or c.startswith(("y", "j", "Y", "J"))) and (not options.s):
			shutil.rmtree(thumbdir)
			shutil.rmtree(picdir)
			shutil.rmtree(pagedir)
		elif not options.s:
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
			
	# picture generation
	fnames = [None]
	d = os.listdir(options.input)
	dwithtimes = []
	if options.sort:
		for f in d:
			fname = options.input+f
			if fname.endswith(FORMATS):
				try:
					if fname.endswith(("jpeg", "JPEG", "jpg", "JPG")):
						e = open(fname)
						tags = EXIF.process_file(e, details=False)
						e.close()
						ts = time.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
						o = str(tags['Image Orientation'])
					else:
						ts = os.path.getmtime(fname)
						o = False
				except:
					ts = os.path.getmtime(fname)
					o = False
				dwithtimes.append((f, ts, o))
		d = sorted(dwithtimes, key=lambda f: f[1])
	else:
		d.sort()
			
	i = 1
	for f in d:
		fname = options.input+f[0]
		sys.stdout.write("[1] Processing file %04d of %04d (%02d%%)       \r" % (i, len(d), i*100/len(d)))
		sys.stdout.flush()
		if fname.endswith(FORMATS):
			fnames.append(fname)
			if options.s:
				i += 1
				continue #debug
						
			im = Image.open(fname)			
			cmdline = ["convert", fname, "-thumbnail", "100x100^", "-gravity", "center", "-extent", "100x100"]
			if options.autorotate and f[2] == 'Rotated 90 CW' and im.size[0] > im.size[1]:
				im = im.rotate(-90)
				cmdline.append("-rotate")
				cmdline.append("90")
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
						<script type="text/javascript" src="../jquery.js"></script>
						<script type="text/javascript" src="../single.js"></script>
						<link rel="stylesheet" href="../single.css" type="text/css" />
					</head>

					<body>
						""" % (options.title)
		if j > 1:
			html += ('<a href="%08d.html" class="thumb" id="prev"><img src="../thumbs/%08d.jpg" alt="" /><span>'+lang['prev']+'</span></a> ') % (j-1, j-1)
		html += '<img src="../pictures/%08d.jpg" alt="" id="main" />' % j
		if j < i-1:
			html += (' <a href="%08d.html" class="thumb" id="next"><img src="../thumbs/%08d.jpg" alt="" /><span>'+lang['next']+'</span></a>') % (j+1, j+1)
			
		html += "<br /><a href='../index.html' id='back'>"+lang["back"]+"</a>"
		fname = fnames[j]
		if fname.endswith(("jpeg", "JPEG", "jpg", "JPG")) and options.exif:
			html += "<div class='exif'><table><tr><th colspan='2'>"+lang["details"]+"</th></tr><tr>"
			e = open(fname)
			tags = EXIF.process_file(e, details=False)
			e.close()
			taghtml = []
			
			if 'EXIF DateTimeOriginal' in tags:
				dt = time.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
				taghtml.append(lang['taken'] % time.strftime(lang['datetime'], dt))
			if 'EXIF ExposureTime' in tags:
				taghtml.append(lang['exptime'] % tags['EXIF ExposureTime'])
			if 'EXIF FNumber' in tags:
				taghtml.append(lang['fnumber'] % tags['EXIF FNumber'])
			if 'EXIF Flash' in tags:
				if str(tags['EXIF Flash']) == 'Off' or str(tags['EXIF Flash']) == 'No':
					taghtml.append(lang['noflash'])
				else:
					taghtml.append(lang['flash'] % tags['EXIF Flash'])
			if 'EXIF ISOSpeedRatings' in tags:
				taghtml.append(lang['iso'] % tags['EXIF ISOSpeedRatings'])
			if 'EXIF FocalLength' in tags:
				taghtml.append(lang['focallength'] % tags['EXIF FocalLength'])
			if 'EXIF MeteringMode' in tags:
				taghtml.append(lang['metering'] % tags['EXIF MeteringMode'])
			if 'EXIF ExifImageLength' in tags:
				mp = int(str(tags['EXIF ExifImageLength']))*int(str(tags['EXIF ExifImageWidth']))/1000000
				taghtml.append(lang['res'] % mp)
			if 'Image Make' in tags and 'Image Model' in tags:
				taghtml.append(lang['camera'] % (tags['Image Make'], tags['Image Model']))
				
			html += "</tr><tr>".join(taghtml)
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
					<link rel="stylesheet" href="./index.css" type="text/css" />
					<script type="text/javascript" src="./jquery.js"></script>
					<script type="text/javascript">
					$(document).ready(function(){
						$(".thumb").bind("mouseenter", function(){
							if($(this).children("span").css("opacity") == 0){
								$(this).children("span").animate({opacity: 0.7}, 100);
							}
						});
						$(".thumb").bind("mouseleave", function(){
							$(this).children("span").animate({opacity: 0}, 100);
						});
					});
					</script>
				</head>

				<body><h1>%s <small>"""+lang['stats']+"""</small></h1>""") % (options.title,options.title,i,datetime.date.today().strftime("%d.%m.%Y"))
	for j in xrange(1, i):
		html += '<a href="picpages/%08d.html" class="thumb"><img src="thumbs/%08d.jpg" alt="" />' % (j,j)
		if options.displaydate:
			html += '<span>'+time.strftime(lang['2ldatetime'], d[j-1][1])+'</span>'
		html += '</a> '
	html += "<div class='poweredby'>"+lang['powered']+"</div>"
	html += "</body></html>"
	f = open("%sindex.html" % (htmldir), "w")
	f.write(html)
	f.close()
		
		
parser = argparse.ArgumentParser(description='Makes a gallery. Now.')
parser.add_argument('input', metavar='INPUT', type=str,
                   help='This is directory with pictures for the gallery. Attention: no subdirectories will be used!')
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
parser.add_argument('--sort', '-c', action='store_true', dest='sort',
                   help='Try to sort the pictures chronologically. We try first to use EXIF as source for the timestamps, then mtime().')
parser.add_argument('--no-date', '-d', action="store_false", dest='displaydate',
                   help='Prevents instantgallery.py from showing the date and time of the picutres on the index page.')
parser.add_argument('-y', action="store_true", dest='yes',
                   help='Say yes to everything.')
parser.add_argument('-s', action="store_true",
                   help='Skips the generation of thumbnails and similar things. Use this only if you\'re aware of what you\'re doing.')
args = parser.parse_args()

makegallery(args)
