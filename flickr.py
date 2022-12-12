import requests
import json
import os

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
            url = self.fetch_image_url(photo["id"])
            self.photos[photo["id"]] = Photo(photo["id"], photo["title"], url)
            
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
        return original_url

    def manage_album_download(self):
        print("creating directory for: " + self.title)
        os.makedirs(self.title)
        for v in self.photos.values():
            v.download_image(self.title)
        



        

if __name__ == "__main__":
    pass

class Photo:
    def __init__(self, id, photo_title, url):
        self.id = id
        self.photo_title = photo_title
        self.url = url
    
    def download_image(self, directory):
        img_data = requests.get(self.url).content
        with open(directory + "/" + self.photo_title + '.jpg', 'wb') as handler:
            handler.write(img_data)
            print("saved img: " + self.photo_title)

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
        
        return Album(album_id, title)


        # return Album("",1,[1,2])


Global()
