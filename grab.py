from urlparse import urlparse
import urllib2
import lxml.html
import os
import sys
import datetime

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def download_file(dest, url):
    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    mp3_f = open(dest+'/'+file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)
    file_size_dl = 0
    block_sz = 8192

    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        mp3_f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    mp3_f.close()

def get_previously_downloaded(blog_path):
    print(blog_path)
    files = []
    for dirname, dirnames, filenames in os.walk(blog_path):
        for subdirname in dirnames:
            files.append(get_previously_downloaded(os.path.join(dirname, subdirname)))
        for filename in filenames:
            files.append(filename)
    return files

def main():
    if len(sys.argv) != 2:
        print("Error. Usage is " + sys.argv[0] + " http://download_from_here.com")
        return 1
    else:
        f = urllib2.urlopen(sys.argv[1])
        htmlcode = f.read()

        today = datetime.date.today()
        today += datetime.timedelta(days=-today.weekday(), weeks=1)
        dir_name = urlparse(sys.argv[1]).netloc.rsplit('.')[0]
        full_path = '/Users/mmoutenot/Music/blog_music/' + str(dir_name) + '/' + str(today)
        os.mkdir(full_path)

        previous_files = get_previously_downloaded(full_path+'/../')

        tree = lxml.html.fromstring(htmlcode)
        for link in tree.findall(".//a"):
            url = link.get("href")
            if url.endswith(".mp3"):
                file_name = url.split('/')[-1]
                if file_name not in previous_files:
                    download_file(full_path, url)
                    f.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
