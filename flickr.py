import requests
import json
import os
import urllib.request
import shutil

class Album:
    
    def __init__(self, id, title):
        self.title = title 
        self.id = id
        self.photos = {}

    def fetch_album_photos(self):
        url = "https://api.flickr.com/services/rest//?method=flickr.photosets.getPhotos&api_key=caa9a480d0f3c465d17226b281fe2d51&photoset_id=" + self.id + "&format=json&nojsoncallback=1&user_id=54027415@N03"

        payload={}
        headers = {
          'Cookie': 'ccc=%7B%22needsConsent%22%3Atrue%2C%22managed%22%3A0%2C%22changed%22%3A0%2C%22info%22%3A%7B%22cookieBlock%22%3A%7B%22level%22%3A0%2C%22blockRan%22%3A1%7D%7D%7D'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        json = response.json()
        photos = json["photoset"]["photo"]
        
        for photo in photos:
            url, is_video = self.fetch_image_url(photo["id"])
            self.photos[photo["id"]] = Photo(photo["id"], photo["title"], url, is_video)
            
            # self.photos[photo["id"]].download_image()

        self.manage_album_download()
        
    
    def fetch_image_url(self, photo_id):
        url = "https://api.flickr.com/services/rest//?method=flickr.photos.getSizes&api_key=caa9a480d0f3c465d17226b281fe2d51&photo_id=" + photo_id + "&format=json&nojsoncallback=1"

        payload={}
        headers = {
          'Cookie': 'ccc=%7B%22needsConsent%22%3Atrue%2C%22managed%22%3A0%2C%22changed%22%3A0%2C%22info%22%3A%7B%22cookieBlock%22%3A%7B%22level%22%3A0%2C%22blockRan%22%3A1%7D%7D%7D'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        json = response.json()

        all_urls = json["sizes"]["size"]

        original_url = [x["source"] for x in all_urls if x["label"] == "Original"][0]
        video_url = [x["source"] for x in all_urls if x["label"] == "1080p" or "720p"]

        is_video = False

        if len(video_url) != 0:
            video_url_1080 = [x for x in video_url if "play/1080" in x][0]
            video_url_720 = [x for x in video_url if "play/1080" in x][0]
            
            if video_url_1080 and video_url_720:
                original_url = video_url_1080
            else:
                original_url = video_url_720
                
            print("vid found")
            # print(original_url)
            is_video = True

        return original_url, is_video

    def manage_album_download(self):
        print("creating directory for: " + self.title)
        os.makedirs(self.title)
        
        self.create_upload_dir()
        
        for v in self.photos.values():
            v.download(self.title)

            v.upload(self.title)
            
        self.remove_dir()


    def create_upload_dir(self):
        url = "https://boardsportverenigingdrop.stack.storage/api/v2/directories"

        payload = json.dumps({
          "parentID": 8080,
          "name": self.title 
        })
        headers = {
          'X-AppToken': 'KUTSfu8kJKWwzq4Z_CUG5fuHCmQ',
          'Content-Type': 'application/json'
        }

        print("creating directory: " + self.title)
        response = requests.request("POST", url, headers=headers, data=payload)

    def remove_dir(self):
        shutil.rmtree(self.title)

if __name__ == "__main__":
    pass


class Photo:
    def __init__(self, id, title, url, is_video):
        self.id = id
        self.title = title
        self.url = url
        self.is_video = is_video
    
    def download(self, directory):
        data = requests.get(self.url).content
        if self.is_video:
            r = requests.get(self.url, stream = True) 

            # download started 
            with open(directory+ "/" + self.title + ".mp4", 'wb') as f: 
                print("downloading: " + self.title + ".mp4")
                for chunk in r.iter_content(chunk_size = 1024*1024): 
                    if chunk: 
                        f.write(chunk)            
        else:
            with open(directory + "/" + self.title + '.jpg', 'wb') as handler:
                handler.write(data)
                print("saved img: " + self.title)

    def upload(self, directory):
        if self.is_video:
            filename = directory + "/" + self.title + ".mp4"
        else:
            filename = directory + "/" + self.title + ".jpg"
            
        

class Global:
    def __init__(self):
        self.album_ids = []
        self.albums = {} 
        self.read_file()
        self.add_albums()
    
    def read_file(self):
        with open('output.txt') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                self.album_ids.append(line.strip())
                
    def add_albums(self):
        for album_id in self.album_ids:
            self.albums[album_id] = self.fetch_album_info(album_id)

            self.albums[album_id].fetch_album_photos()

    def fetch_album_info(self, album_id):
        url = "https://api.flickr.com/services/rest//?method=flickr.photosets.getInfo&api_key=caa9a480d0f3c465d17226b281fe2d51&photoset_id=" + album_id + "&format=json&nojsoncallback=1&user_id=54027415@N03"

        payload={}
        headers = {
          'Cookie': 'ccc=%7B%22needsConsent%22%3Atrue%2C%22managed%22%3A0%2C%22changed%22%3A0%2C%22info%22%3A%7B%22cookieBlock%22%3A%7B%22level%22%3A0%2C%22blockRan%22%3A1%7D%7D%7D'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        json = response.json()
        title = json["photoset"]["title"]["_content"]

        # print("fetching album: " + title)
        
        return Album(album_id, title)


        # return Album("",1,[1,2])


Global()
