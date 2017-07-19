import sys, urllib2, requests
from urlparse import urljoin
from bs4 import BeautifulSoup

#Avoid unicode errors
reload(sys)
sys.setdefaultencoding("utf-8")

maxnumberurl = int(sys.argv[2])
seedfile = open(sys.argv[1], 'r')

#Pipe print statements to a file named crawler.output
sys.stdout = open("crawler.output",'w')

def htmlpagecheck(url):
    """Returns true if url is an html page and false if not"""
    #More than two slashes would indicate that there is a relative path
    #Some links had a / at the end, since I deleted it, more than two slashes = relative path exists
    if url.count("/") > 2:
        lastpart = url[url.rfind("/") + 1:]
        if "." in lastpart:
            if ".html" not in lastpart or ".htm" not in lastpart:
                return False
    #If there is no period, then we can assume it's an html page
    return True
    
queue = []
startingurl = seedfile.readlines()[0]
nowwwstartingurl = startingurl[:7] + startingurl[11:]
queue.append(nowwwstartingurl)
visited = []
sourcecurrentpairs = []
while len(visited) < maxnumberurl:
    currenturl = queue.pop(0)
    try:
        requested = urllib2.urlopen(currenturl)
        if currenturl not in visited:
            visited.append(currenturl)
        rhtml = requested.read()
        soup = BeautifulSoup(rhtml, "html.parser", from_encoding="iso-8859-1")
        for link in soup.find_all("a"):
            discoveredurl = link.get('href')
            #Ignore a tags with no href, empty href links,
            #/'s and #'s which indicate the current url, #'s
            #and mailto/other emails with the @ symbol
            if discoveredurl != "" and discoveredurl != None and discoveredurl != "/" and "#" not in discoveredurl and "@" not in discoveredurl:
                begin = discoveredurl
                #Delete trailing and leading whitespace
                discoveredurl = discoveredurl.strip()
                #Ignore #'s in url's. Example: eecs.umich.edu#hello and eecs.umich.edu. Treat them as the same
                if "#" in discoveredurl:
                    #Example: eecs.umich.edu#CSE. That's still the same page as eecs.umich.edu, so just ignore
                    if discoveredurl[0] == "#":
                        continue
                    discoveredurl = discoveredurl[:discoveredurl.find("#")]
                #Remove index.php
                if "/index.php" in discoveredurl:
                    discoveredurl = discoveredurl[:discoveredurl.find("/index.php")]
                #For standardization's sake, remove / at the end if it exists
                if discoveredurl[-1] == "/":
                    discoveredurl = discoveredurl[:len(discoveredurl) - 1]
                #Standardize https to http
                if "https" in discoveredurl:
                    discoveredurl = discoveredurl[:4] + discoveredurl[5:]
                if discoveredurl[0] == "/":
                    discoveredurl = urljoin(currenturl, discoveredurl)
                if "http://www." in discoveredurl:
                    discoveredurl = "http://" + discoveredurl[11:]
                if discoveredurl not in queue:
                    #Check for eecs.umich.edu vs other websites
                    firstpart = discoveredurl[discoveredurl.find("//") + 2:]
                    #If there is a relative path, remove it to get the base url
                    if "/" in firstpart:
                        firstpart = firstpart[:firstpart.find("/")]
                    if "eecs.umich.edu" in firstpart and htmlpagecheck(discoveredurl):
                        queue.append(discoveredurl)
                        if currenturl[-1] == "/":
                            currenturl = currenturl[:len(currenturl) - 1]
                        sourcecurrentpairs.append([currenturl, discoveredurl])
    #Account for non-200 response code
    except urllib2.HTTPError:
        continue
    except urllib2.URLError:
        continue
    
for url in visited:
    print url

    
        
