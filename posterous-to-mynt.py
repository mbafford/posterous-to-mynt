import sys
from BeautifulSoup import BeautifulStoneSoup as Soup
import html2text
from dateutil.parser import parse
import re
import fnmatch
import os
import shutil
import urllib

global fileMappings
global mappedFiles
global infolder
global outfolder

def findImages(root):
	matches = {}

	for root, dirnames, filenames in os.walk(os.path.join(root, 'image/')):
		for filename in filenames:
			match = re.match("[0-9]+-(.*)", filename)
			if match: 
				shortname = match.group(1)
			else:
				shortname = filename

			matches[shortname] = os.path.join(root, filename)

	return matches

def rewriteURLs(content, postDate, postID):
	urlpat = re.compile('"(http://getfile\d*.posterous.com/getfile/[^"]+/([^"]*[.][^"]*))"')
	urls = urlpat.findall(content)

	for match in urls:
		fullURL  = match[0]
		filename = match[1]

		# strip off the .scaled.###.jpg on filenames
		# currently this ignores the resize field
		# it'd be better if this actually resized
		if ".scaled" in filename:
			filename = filename[:filename.index(".scaled")]

		if not filename in fileMappings:
			print "Image not found: " + filename + " trying fetching"

			fetchFile = os.path.join(infolder, 'image', 'fetched', filename)

			if not os.path.exists( os.path.dirname(fetchFile) ):
				os.makedirs( os.path.dirname(fetchFile) )

			urllib.urlretrieve(fullURL, fetchFile)
			fileMappings[filename] = fetchFile

		mappedFile = postDate.strftime("%Y/%m/%d/") + postID + "/" + filename;
		assetLink  = "{{ get_asset('images/" + mappedFile + "') }}"

		print "Replacing " + fullURL + " with " + mappedFile;

		content = content.replace(fullURL, assetLink)

		mappedFiles.append([fileMappings[filename], mappedFile])

	return content
	
def processFile(filename):
	print "Processing: " + filename 

	soup = Soup(open(filename))

	for item in soup.findAll('item'):
		title   = item.find('title').text;
		link    = item.find('link').text;
		pubDate = item.find('wp:post_date').text;
		content = item.find('content:encoded').text;
		postID  = item.find('wp:post_id').text;

		tagarr = []
		for cat in soup.findAll('category', domain='tag'):
			tag = html2text.html2text(cat.text)
			tag = tag.strip()
			tagarr.append(tag)
		tags = ' '.join(tagarr)

		date = parse(pubDate)

		content = rewriteURLs(content, date, postID)

		title   = html2text.html2text(title)
		content = content.replace("&nbsp;", " ")
		content = html2text.html2text(content)

		outname = outfolder + "/_posts/" + date.strftime("%Y-%m-%d-%H-%M-") + postID + "-" + link[link.rfind('/')+1:] + '.md'
		outfile = open(outname, 'w')

		print "Writing to: " + outname

		outfile.write("---\n")
		outfile.write("layout: post.html\n")
		outfile.write("title: " + title.encode('utf-8') + "\n")
		outfile.write("tags: [" + tags + "]\n")
	#	outfile.write("pubDate: " + pubDate + "\n")
		outfile.write("---\n")
		outfile.write("\n")
		outfile.write(content.encode('utf-8'))

if len(sys.argv) == 1:
	print "Usage: " + sys.argv[0] + " <posterous export folder> <mynt output folder>"
	sys.exit(0)

# it's unfortunate this has to be module level, but using the instance level
# "body_width" parameter didn't work for me
html2text.BODY_WIDTH=1000

infolder = sys.argv[1]
outfolder = sys.argv[2]

fileMappings = findImages(infolder)
mappedFiles  = []

for root, dirnames, filenames in os.walk(os.path.join(infolder, "posts/")):
	for filename in filenames:
		if filename.endswith(".xml"):
			print os.path.join(root, filename)
			processFile(os.path.join(root, filename))

for file in mappedFiles:
	oldfile = file[0]
	newfile = os.path.join(outfolder, '_assets/', 'images/', file[1])

	print "Copying " + oldfile + " to " + newfile
	if not os.path.exists(os.path.dirname(newfile)):
		os.makedirs(os.path.dirname(newfile))
	shutil.copyfile(oldfile, newfile)
