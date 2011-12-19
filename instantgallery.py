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

def makegallery(options):
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
			
	# Picture creation
	htmldir = options.output
	thumbdir = options.output+"thumbs/"
	picdir = options.output+"pictures/"
	pagedir = options.output+"picpages/"
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
	d.sort()
	i = 1
	for f in d:
		fname = options.input+f
		sys.stdout.write("[1] Processing file %04d of %04d (%02d%%)       \r" % (i, len(d), i*100/len(d)))
		sys.stdout.flush()
		if fname.endswith(("png", "PNG", "jpg", "JPG", "bmp", "BMP", "jpeg", "JPEG", "tif", "TIF", "tiff", "TIFF")):
			fnames.append(fname)
			if options.s:
				i += 1
				continue #debug
			
			#subprocess.Popen(["convert", fname, "-thumbnail", "1920x", "%s%08d.jpg" % (picdir, i)]).wait()
			subprocess.Popen(["convert", fname, "-thumbnail", "100x100^", "-gravity", "center", "-extent", "100x100", "%s%08d.jpg" % (thumbdir, i)]).wait()
			
			im = Image.open(fname)
			im.thumbnail((1920,1080), Image.ANTIALIAS)
			im.save("%s%08d.jpg" % (picdir, i))
			
			"""im.thumbnail((100,100), Image.ANTIALIAS)
			im.save("%s%08d.jpg" % (thumbdir, i))"""
				
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
						<link rel="stylesheet" href="../single.css" type="text/css" />
					</head>

					<body>
						""" % (options.title)
		if j > 1:
			html += '<a href="%08d.html"><img src="../thumbs/%08d.jpg" alt="" id="prev" /></a> ' % (j-1, j-1)
		html += '<img src="../pictures/%08d.jpg" alt="" id="main" />' % j
		if j < i-1:
			html += ' <a href="%08d.html"><img src="../thumbs/%08d.jpg" alt="" id="next" /></a>' % (j+1, j+1)
			
		html += "<br /><a href='../index.html'>zurück zur Übersicht</a>"
		fname = fnames[j]
		if fname.endswith(("jpeg", "JPEG", "jpg", "JPG")):
			html += "<div class='exif'>"
			tags = EXIF.process_file(open(fname), details=False)
			taghtml = []
			
			if 'EXIF DateTimeOriginal' in tags:
				dt = time.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
				taghtml.append('Aufgenommen: %s' % time.strftime("%d.%m.%Y %H:%M:%S", dt))
			if 'EXIF ExposureTime' in tags:
				taghtml.append('Belichtungszeit: %ss' % tags['EXIF ExposureTime'])
			if 'EXIF FNumber' in tags:
				taghtml.append('Blendenzahl: F%s' % tags['EXIF FNumber'])
			if 'EXIF Flash' in tags:
				if str(tags['EXIF Flash']) == 'Off' or str(tags['EXIF Flash']) == 'No':
					taghtml.append('ohne Blitz')
				else:
					taghtml.append('Blitz: %s' % tags['EXIF Flash'])
			if 'EXIF ISOSpeedRatings' in tags:
				taghtml.append('ISO-Zahl: %s' % tags['EXIF ISOSpeedRatings'])
			if 'EXIF FocalLength' in tags:
				taghtml.append('Brennweite: %smm' % tags['EXIF FocalLength'])
			if 'EXIF MeteringMode' in tags:
				taghtml.append('Belichtungsmessung: %s' % tags['EXIF MeteringMode'])
			if 'EXIF ExifImageLength' in tags:
				mp = int(str(tags['EXIF ExifImageLength']))*int(str(tags['EXIF ExifImageWidth']))/1000000
				taghtml.append('Originalauflösung: %dM' % mp)
			if 'Image Make' in tags and 'Image Model' in tags:
				taghtml.append('Kamera: %s %s' % (tags['Image Make'], tags['Image Model']))
				
			html += " &middot; ".join(taghtml)
			html += "</div>"
		html += "</body></html>"
		f = open("%s%08d.html" % (pagedir, j), "w")
		f.write(html)
		f.close()
	
	# index page
	sys.stdout.write("[3] Generating index                       \r")
	sys.stdout.flush()
	html = """<!DOCTYPE html>
				<html>
				<head>
					<title>%s</title>
					<meta http-equiv="content-type" content="text/html;charset=utf-8" />
					<link rel="stylesheet" href="./index.css" type="text/css" />
				</head>

				<body><h1>%s <small>%d Bilder &middot; generiert am %s</small></h1>""" % (options.title,options.title,i,datetime.date.today().strftime("%d.%m.%Y"))
	for j in xrange(1, i):
		html += '<a href="picpages/%08d.html"><img src="thumbs/%08d.jpg" alt="" id="main" /></a> ' % (j,j)
	html += "</body></html>"
	f = open("%sindex.html" % (htmldir), "w")
	f.write(html)
	f.close()
		
		
parser = argparse.ArgumentParser(description='Make a gallery. Now.')
parser.add_argument('input', metavar='INPUT', type=str,
                   help='directory with pictures')
parser.add_argument('output', metavar='OUTPUT', type=str,
                   help='where the gallery should be created')
parser.add_argument('-t', metavar='TITLE', type=str, default='Image Gallery',
                   help='title of the gallery')
parser.add_argument('-s', action="store_true",
                   help='DO NOT USE THIS')
args = parser.parse_args()
args.title = args.t

makegallery(args)
