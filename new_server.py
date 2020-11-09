from flask import Flask, request, url_for, render_template
from flask_pymongo import PyMongo
from PIL import Image
from PIL.ExifTags import TAGS
import gridfs
import json
import binascii
from PIL.TiffImagePlugin import IFDRational
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/testdb'
mongo = PyMongo(app)


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, IFDRational):
            try:
                return float(o)
            except ZeroDivisionError:
                return None
        if isinstance(o, bytes):
            hex_data = binascii.hexlify(o)
            str_data = hex_data.decode('utf-8')
            return str_data
        return o


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/upload')
def index():
    return '''
        <form method="POST" action="/create" enctype="multipart/form-data">
            <label for="uname">User name</label>
            <input type="text" id="uname" name="username"><br><br>
            <input type="file" name="image"><br><br>
            <input type="submit">
        </form>
    '''


@app.route('/create', methods=['POST'])
def create():
    if 'image' in request.files:
        image = request.files['image']
        mongo.save_file(image.filename, image)
        ####

        # im=mongo.send_file(image.filename)
        #fs = gridfs.GridFS(mongo.db)
        #im = fs.get_last_version(image.filename).read()

        # print(type(im))
        try:
            image2 = Image.open(image)
        except IOError:
            print("Error")
            pass
        exif = {}
        for tag, value in image2._getexif().items():

            if tag in TAGS:
                exif[TAGS[tag]] = value

        print()
        print("Displaying all the metadatas of the image: \n")
        print(type(exif))

        mongo.db.users.insert({'username': request.form.get(
            'username'), 'image_name': image.filename})
        mongo.db.metadata.insert({'username': request.form.get(
            'username'), 'image_name': image.filename, 'metadata': json.loads(json.dumps(exif, cls=CustomEncoder))})

        return 'Done!'


if __name__ == '__main__':
    app.run(debug=True)
