from urlparse import urlparse
from subprocess import call
import urllib2
import lxml.html
import os
import sys
import datetime
import eyeD3

class Usage(Exception):
  def __init__(self, msg):
    self.msg = msg

# takes as arguments the destination path of the file to download and the url to
# download. It does so, and as a side effect, displays the progress
def download_file(dest, url):
  name  = url.split('/')[-1]
  u     = urllib2.urlopen(url)
  path  = dest + '/' + name
  mp3_f = open(path, 'wb')
  meta  = u.info()
  size  = int(meta.getheaders("Content-Length")[0])
  print "Downloading: %s Bytes: %s" % (name, size)
  dl_size = 0
  block_sz = 8192
  while True:
    buffer = u.read(block_sz)
    if not buffer:
      break
    dl_size += len(buffer)
    mp3_f.write(buffer)
    status = r"%10d  [%3.2f%%]" % (dl_size, dl_size * 100. / size)
    status = status + chr(8)*(len(status)+1)
    print status,
  mp3_f.close()
  return path

# recursively gets other songs downloaded in the path
def get_previously_downloaded(blog_path):
  files = []
  for dirname, dirnames, filenames in os.walk(blog_path):
    for subdirname in dirnames:
      files.append(get_previously_downloaded(os.path.join(dirname, subdirname)))
    for filename in filenames:
      files.append((filename, os.path.join(dirname,filename)))
  return files

# creates a simple m3u playlist. takes as input the name of the site and the
# list of songs that have been downloaded
def create_playlist(site_name, songs):
  today       = datetime.date.today()
  folder_date = today + datetime.timedelta(days=-today.weekday(), weeks=1)
  playlist_name = site_name + '_' + str(folder_date) + '.m3u'
  p_f = open(playlist_name , 'wf')
  p_f.write("#EXTM3U\n")
  for song, path in songs:
    tag = eyeD3.Tag()
    tag.link(path)
    song_data   = eyeD3.Tag()
    song_data.link(path)
    p_f.write('#EXTINFO: 0 ,' + song_data.getArtist() + ' - '
              + song_data.getTitle() + "\n")
    p_f.write(path + "\n")
  p_f.close()
  return playlist_name

def main():
  if len(sys.argv) != 3:
    print("Error. Usage is " + sys.argv[0] +
          " /full/path/to/music/directory http://download_from_here.com")
    return 1
  else:
    music_dir_path = sys.argv[1]

    # check if there is a trailing '/' and remove it
    if music_dir_path[len(music_dir_path)-1] is '/':
      music_dir_path = music_dir_path[:-1]

    for i in range(2,len(sys.argv)):
      f        = urllib2.urlopen(sys.argv[i])
      htmlcode = f.read()

      site_name   = urlparse(sys.argv[i]).netloc.rsplit('.')[0]
      today       = datetime.date.today()
      folder_date = today + datetime.timedelta(days=-today.weekday(), weeks=1)
      dir_name    = str(site_name) + '/' + str(folder_date)
      full_path   = music_dir_path + '/' + dir_name

      # create the directory to put the downloaded songs into
      try:
        os.makedirs(full_path)
      except:
        print("Directory already existed, moving along")


      # download all files that aren't duplicates
      downloaded_files = []
      previous_files   = get_previously_downloaded(full_path+'/../')
      tree = lxml.html.fromstring(htmlcode)

      # get all mp3 urls within the html source and download them
      for link in tree.findall(".//a"):
        url       = link.get("href")
        file_name = url.split('/')[-1]
        if url.endswith(".mp3") and file_name not in previous_files:
          path = download_file(full_path, url)
          downloaded_files.append([file_name,path])
      f.close()

      # create a playlist
      playlist_name = create_playlist(site_name, downloaded_files)
      os.system("open /Applications/iTunes.app/ "+playlist_name)
      os.system("osascript -e 'tell application \"iTunes\" to pause'");

  return 0

if __name__ == "__main__":
  sys.exit(main())
