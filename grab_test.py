from urlparse import urlparse
import urllib2
import lxml.html
import os
import sys
import datetime
import eyeD3

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

def get_songs(blog_path):
  print(blog_path)
  files = []
  for dirname, dirnames, filenames in os.walk(blog_path):
    for subdirname in dirnames:
      files.append(get_songs(path))
    for filename in filenames:
      files.append((filename,os.path.join(dirname,filename)))
  return files

files = get_songs("/home/marshall/Music/musigh/2012-03-26")
create_playlist("musigh", files)

