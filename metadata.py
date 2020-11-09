import os
from PIL import Image
from PIL.ExifTags import TAGS

image_file = 'image.jpg'


try:
    image = Image.open(image_file)
except IOError:
    pass

exif = {}

for tag, value in image._getexif().items():

    if tag in TAGS:
        exif[TAGS[tag]] = value

try:
    if 'Copyright' in exif:
        print("Image is Copyrighted, by ", exif['Copyright'])
except KeyError:
    pass

print()
print("Displaying all the metadatas of the image: \n")
print(exif)
