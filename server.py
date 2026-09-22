#get
#get/https:api.github.com/username/samthegoat/contents/path/to/file

#https://api.github.com/users/samthemogul 

from urllib.request import urlopen

response = urlopen("https://api.github.com/users/samthemogul")
print(response)

import urllib.request
import json

response = urllib.request.urlopen("https://api.github.com/users/samthemogul")
raw_data = response.read()
data = json.loads(raw_data)
print(data["name"], data["location"], data["bio"], data["public_repos"], data["followers"], data["following"])