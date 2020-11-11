from flask import Flask, request, url_for, render_template
from flask_pymongo import PyMongo
from pymongo import MongoClient
from PIL import Image
from PIL.ExifTags import TAGS
#import gridfs
import json
import binascii
from PIL.TiffImagePlugin import IFDRational
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://db:27017/testdb'
mongo = PyMongo(app)
client = MongoClient("db", 27017, maxPoolSize=50)
db2 = client["testdb"]
collection = db2['metadata']


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


@app.route('/', methods=['POST', 'GET'])
def hello():
    return '''
    <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Allerta+Stencil">
        <style>
        .w3-allerta {
             font-family: "Allerta Stencil", Sans-serif;
            }
        </style>
        <body>

        <div class="w3-container w3-cyan w3-center w3-allerta">
          <p class="w3-xlarge" style="font-size:50px;">WELCOME</p>

        </div>

    <div align ="center">

        <p>Enter <strong>username</strong> and <strong>password</strong> to login as admin or choose guest</p>

        <form method="POST" action="/login" enctype="multipart/form-data">
            <label for="uname">User Name:</label><br>
            <input type="text" id="uname" name="uname"><br>
            <label for="pass">Password:</label><br>
            <input type="text" id="pass" name="pass"><br><br>
            <input type="submit" value="Submit">
        </form>
        <button
            onclick="location.href='/home_guest'"
            type="button"
          >
          Login as Guest</button>
          </div>

    </body>
'''


@app.route('/login', methods=['POST', 'GET'])
def login():
    if(request.form.get('uname') == "admin" and request.form.get('pass') == "admin"):
        return render_template('admin_redirect.html')
    return render_template("admin_error.html")


@app.route('/home_admin')
def home_admin():
    return render_template('index.html')


@app.route('/home_guest')
def home_guest():
    return render_template('index2.html')


@app.route('/upload')
def index():
    return '''
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Allerta+Stencil">
        <style>
        .w3-allerta {
             font-family: "Allerta Stencil", Sans-serif;
            }
        </style>
        <body>

        <div class="w3-container w3-black w3-center w3-allerta">
          <p class="w3-xlarge" style="font-size:50px;">Upload Images</p>

        </div>
        <div align="center">
        <form method="POST" action="/create" enctype="multipart/form-data">
            <br></br>
            <label for="uname">User name</label>
            <input type="text" id="uname" name="username"><br><br>
            <input type="file" name="image"><br><br>
            <input type="submit">
        </form>
        </div>
    '''


@app.route('/create', methods=['POST'])
def create():
    if 'image' in request.files:
        image = request.files['image']
        mongo.save_file(image.filename, image)
        ####

        # im=mongo.send_file(image.filename)
        # fs = gridfs.GridFS(mongo.db)
        # im = fs.get_last_version(image.filename).read()

        # print(type(im))
        try:
            image2 = Image.open(image)
        except IOError:
            print("Error")
            pass
        exif = {}
        for tag, value in dict(image2.getexif()).items():

            if tag in TAGS:
                exif[TAGS[tag]] = value

        print()
        print("Displaying all the metadatas of the image: \n")
        print(type(exif))

        mongo.db.users.insert({'username': request.form.get(
            'username'), 'image_name': image.filename})
        mongo.db.metadata.insert({'username': request.form.get(
            'username'), 'image_name': image.filename, 'metadata': json.loads(json.dumps(exif, cls=CustomEncoder))})

        return render_template('admin_redirect.html')


# @app.route('/file/<filename>')
# def file(filename):
#    return mongo.send_file(filename)

@app.route('/search')
def index2():

    return '''
        <title></title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Allerta+Stencil">
        <style>
        .w3-allerta {
             font-family: "Allerta Stencil", Sans-serif;
            }
        </style>
        <body>

        <div class="w3-container w3-teal w3-center w3-allerta">
          <p class="w3-xlarge" style="font-size:50px;">Enter value of any of the fields to Search</p>

        </div>

        </body>
        <div align="center">
        <br><br>
        <form method="GET" action="/view" enctype="multipart/form-data">

            <label for="image_name">Image name</label>
            <input type="text" id="image_name" name="image_name"><br><br>

            <label for="ISOSpeedRatings">ISO value</label>
            <input type="number" id="ISOSpeedRatings" name="ISOSpeedRatings"><br><br>

            <label for="Flash">Flash value</label>
            <input type="text" id="Flash" name="Flash"><br><br>

            <label for="ImageLength">Image Length</label>
            <input type="text" id="ImageLength" name="ImageLength"><br><br>

            <label for="ImageWidth">Image Width</label>
            <input type="text" id="ImageWidth" name="ImageWidth"><br><br>

            <label for="FocalLength">Focal Length</label>
            <input type="text" id="FocalLength" name="FocalLength"><br><br>

            <input type="submit">
        </form>
        <button
      onclick="location.href='/home_admin'"
    >
      Home
    </button>
        </div>
    '''


@app.route('/del')
def fun():
    return render_template('delete.html')


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    image_name1 = request.args.get('image_name')
    dic1 = collection.find_one({"image_name": image_name1})
    if dic1 == None:
        return render_template('404_del.html')
    collection.delete_one({'image_name': image_name1})
    return '''
    <div align="center">
    <h1><b>Image Deleted</b></h1><br><br>
    <button
            onclick="location.href='/home_admin'"
            type="button"
          >
            Go back to Home Page
          </button>

    </div>
    '''


@app.route('/view', methods=['POST', 'GET'])
def show():
    image_name = request.args.get('image_name')

    ISO = request.args.get('ISOSpeedRatings')
    flash = request.args.get('Flash')
    ImageLength = request.args.get('ImageLength')
    ImageWidth = request.args.get('ImageWidth')
    FocalLength = request.args.get('FocalLength')
    if image_name != '':
        dic = collection.find_one({"image_name": image_name})
        print(dic)
        if dic == None:
            return render_template('404.html')
        else:
            return mongo.send_file(request.args.get('image_name'))
    if ISO != '':
        ISO = int(ISO)
        dic = collection.find_one({"metadata.ISOSpeedRatings": ISO})
        if(dic == None):
            return render_template('404.html')
        else:
            im_name = dic["image_name"]
            return mongo.send_file(im_name)

    if flash != '':
        flash = int(flash)
        dic = collection.find_one({"metadata.Flash": flash})
        if(dic == None):
            return render_template('404.html')
        else:
            im_name = dic["image_name"]
            return mongo.send_file(im_name)

    if ImageLength != '':
        ImageLength = int(ImageLength)
        dic = collection.find_one({"metadata.ImageLength": ImageLength})
        if(dic == None):
            return render_template('404.html')
        else:
            im_name = dic["image_name"]
            return mongo.send_file(im_name)

    if ImageWidth != '':
        ImageWidth = int(ImageWidth)
        dic = collection.find_one({"metadata.ImageWidth": ImageWidth})
        if(dic == None):
            return render_template('404.html')
        else:
            im_name = dic["image_name"]
            return mongo.send_file(im_name)

    if FocalLength != '':
        FocalLength = float(FocalLength)
        dic = collection.find_one({"metadata.FocalLength": FocalLength})
        if(dic == None):
            return render_template('404.html')
        else:
            im_name = dic["image_name"]
            return mongo.send_file(im_name)

    return render_template("404.html")


if __name__ == '__main__':

    app.run(debug=True,host="0.0.0.0",port=5000)
