from spiders import kinky

kinky_df = kinky.loadAdvertisements()

kinky_df['id'][0]
print(kinky_df[kinky_df['id']=='590976']['scr_tag'][0])

pic = 'https://i.kinky.nl/353989/profile/3e4b8cba-b768-4f86-a4d3-c91815d6fee5_profile.jpg'

from PIL import Image
from PIL.ExifTags import TAGS
image = Image.open('C:\\Users\\AnneLeemans\\Pictures\\Anne 1.jpg')
exifdata = image.getexif()
for tag_id in exifdata:
    try:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes 
        if isinstance(data, bytes):
            data = data.decode()
        print(f"{tag:25}: {data}")
    except:
        print('slip')