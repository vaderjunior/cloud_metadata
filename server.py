from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
import os
import db as d
from PIL import Image
from PIL.ExifTags import TAGS
from flask_pymongo import PyMongo
import server as s

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'mydb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/upload', methods=['GET'])
def upload_file():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, 'images/')  # folder path
    if not os.path.isdir(target):
        os.mkdir(target)     # create folder if not exits
    db_table = d.mongo.db.mydb  # database table name
    if request.method == 'POST':
        # multiple image handel
        for upload in request.files.getlist("image"):
            filename = secure_filename(upload.filename)
            destination = "/".join([target, filename])
            upload.save(destination)
            # insert into database mongo db
            db_table.insert({'image': filename})

        return 'Image Upload Successfully'


mongo = PyMongo(app)

if __name__ == '__main__':
    app.run(debug=True)



@app.route('/file/<filename>')
def file(filename):

    #im = mongo.send_file(filename)
    fs = gridfs.GridFS(mongo.db)
    im = fs.get_last_version(filename).read()
    print(type(im))
    try:
        image2 = Image.open(im)
    except IOError:
        print("Error")
        pass

    for tag, value in image2._getexif().items():

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