"""
IGN Game Scoop Podcast Downloader Script v1.0
by Jacob Kenin

DESCRIPTION
Uses the Kimono API creation bookmarklet to generate a JSON file listing all
the IGN Game Scoop Episodes archived on
http://www.ign.com/blogs/gamescooparchives/2011/12/10/game-scoop-archives-the-full-libraryand
This page only has up to 253. The second half gets the rest off
http://feeds.ign.com/ignfeeds/podcasts/gamescoop/. This is horribly
unsafe in a number of ways, most notably since all the field names are hardcoded. I
don't know if that is bad practice or not, but it seems bad to me. But whatever, I just
want my podcasts.

This will download ALL GameScoop Podcasts, including Event Coverage, Knockin Boot, and
8 Bit Radio.

You will notice that not all of the podcast names are uniform. I hate this, but the standouts can be
found pretty easily and corrected.

BUGS / MISSING FEATURES
    * Currently does not do any pretty reformatting of title to make them all uniform
    * No progress bar for downloads
      (see http://stackoverflow.com/questions/51212/how-to-write-a-download-progress-indicator-in-python)
    * Because episodes 235 to 260 decided to be special and not do URL encoding correctly,
      there are just 20s where spaces should be. I have a pretty ghetto solution. I don't
      know if there is a better way, but I am listing it as a bug because it doesn't get
      episode 255 or the Mass Effect podcast, but I think it is acceptable
    * No count of how long the downloads are taking
"""
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import requests

DOWNLOAD_DIR = 'E:\\Music\\Podcasts\\IGN GameScoop\\'    # Change this to the directory you want
links = []  # Instantiate the empty list that will hold the MP3 links

# Get a list of the MP3 download links from the archive page
kimonoAPILink = "https://www.kimonolabs.com/api/77dzsutq?apikey=0efa894048affdfdb8424ab377c64ce1"
responseJSON = requests.get(kimonoAPILink)  # Grab the JSON file for parsing
data = responseJSON.json()  # Gives a dictionary of the JSON
collection = data['results']['collection1'] # Grabs the collection1 field from results

# Make a list of just the download links
for link in collection:
    links.append(link['MP3 Link']['href'])

# Get a list of download links from the feedburner page
feedburnerLink = "http://feeds.ign.com/ignfeeds/podcasts/gamescoop?format=xml"
responseXML = requests.get(feedburnerLink)  # Response object of the XML file for parsing
root = ET.fromstring(responseXML.content)  # Creates an XML root Element object for an ETree from the Response content

# Add each download link to links
# Each podcast is stored in a 'item' child
# In each 'item' there is a 'enclosure' element, which holds the mp3 link
mp3s = root.findall("./channel/item/enclosure")
for mp3 in mp3s:
    links.append(mp3.attrib['url'])

# Download all the mp3s, and decode their URL encoded names
position = 1
downloadCount = 0
errorCount = 0
totalPodcasts = len(links)
print("There are %d podcasts" % totalPodcasts)
for file in links:
    # General formatting for pretty file names
    name = file.split('/')[-1]  # Get the last element of the URL, which is the file name
    name = urllib.parse.unquote(name)  # Fixes the archived file names
    name = name.replace('_', ' ')  # Fixes some of the newer feedburner titles
    if len(name.split('20')) == 4:  # If it is one of the incorrectly encoded eps, when split it should have 4 parts
        name = name.replace('20', ' ')  # We can then safely replace the 20s

    # Save the file
    print("Downloading {0} ({1}/{2})...".format(name, position, totalPodcasts), end='')
    try:
        # Check if its already downloaded
        if not os.path.exists(DOWNLOAD_DIR + name):
            urllib.request.urlretrieve(file, DOWNLOAD_DIR + name)
            print()
            downloadCount += 1
        else:
            print(" File already exists")
    except:
        print(" AN ERROR WAS ENCOUNTERED, SKIPPING DOWNLOAD")
        errorCount += 1
    position += 1

print("\nDownload complete: {0} of {1} podcasts downloaded to {2}".format(downloadCount, totalPodcasts, DOWNLOAD_DIR))
print("A total of {0} errors were encountered".format(errorCount))