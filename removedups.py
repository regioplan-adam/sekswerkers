import requests
from io import BytesIO
import PIL.Image
import PIL.ExifTags
from PIL import Image

url = 'https://photos.redlights.nl/photos/1600/1200/rnl/127283/sweetcandy-20190218165750.jpg'
def getImageUrl(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    
    return image

img = getImageUrl(url)

exif_data = img._getexif()

exif = {
    PIL.ExifTags.TAGS[k]: v
    for k, v in img._getexif().items()
    if k in PIL.ExifTags.TAGS
}

print(exif)

