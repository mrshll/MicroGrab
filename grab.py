from urlparse import urlparse
import urllib2
import lxml.html
import os
import sys
import datetime
import eyeD3

class Usage(Exception):
  def __init__(self, msg):
    self.msg = msg

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

def get_previously_downloaded(blog_path):
  print(blog_path)
  files = []
  for dirname, dirnames, filenames in os.walk(blog_path):
    for subdirname in dirnames:
      files.append(get_previously_downloaded(os.path.join(dirname, subdirname)))
    for filename in filenames:
      files.append((filename, os.path.join(dirname,filename)))
  return files

def create_playlist(site_name, songs):
  print ('songs',songs)
  # create new playlist for downloaded songs
  today       = datetime.date.today()
  folder_date = today + datetime.timedelta(days=-today.weekday(), weeks=1)
  p_f = open(site_name + '_' + str(folder_date) + '.m3u', 'wf')
  p_f.write("#EXTM3U\n")
  for song, path in songs:
    tag = eyeD3.Tag()
    tag.link(path)
    song_length = 0
    song_data   = eyeD3.Tag()
    song_data.link(path)
    p_f.write('#EXTINFO:' + str(song_length)+ ',' + song_data.getArtist() +
              ' - ' + song_data.getTitle() + "\n")
    p_f.write(path + "\n")
  p_f.close()

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

      for link in tree.findall(".//a"):
        url       = link.get("href")
        file_name = url.split('/')[-1]
        if url.endswith(".mp3") and file_name not in previous_files:
          path = download_file(full_path, url)
          downloaded_files.append([file_name,path])
      f.close()
      create_playlist(site_name, downloaded_files)

  return 0

if __name__ == "__main__":
  sys.exit(main())
