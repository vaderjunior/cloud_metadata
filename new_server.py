from flask import Flask, request, url_for, render_template
from flask_pymongo import PyMongo
from PIL import Image
from PIL.ExifTags import TAGS
#import gridfs
import json
import binascii
from PIL.TiffImagePlugin import IFDRational
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://db:27017/testdb'
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


@app.route('/', methods=['POST', 'GET'])
def hello():
    return '''
    <body>
        <h2>Welcome </h2>
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
        

    </body>
'''


@app.route('/login', methods=['POST', 'GET'])
def login():
    if(request.form.get('uname') == "admin" and request.form.get('pass') == "admin"):
        return render_template('admin_redirect.html')
    return render_template("404.html")


@app.route('/home_admin')
def home_admin():
    return render_template('index.html')


@app.route('/home_guest')
def home_guest():
    return render_template('index2.html')


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
        <form method="GET" action="/view" enctype="multipart/form-data">
            <label for="image_name">Image name</label>
            <input type="text" id="image_name" name="image_name"><br><br>
            <label for="ISOSpeedRating">Enter ISO Speed Rating</label>
            <input type="text" id="ISOSpeedRating" name="ISOSpeedRating"><br><br>
            <input type="submit">
        </form>
    '''


@app.route('/view', methods=['POST', 'GET'])
def show():
    image_name = request.args.get('image_name')
    ISO = request.args.get('ISOSpeedRating')
    if image_name != '':
        return mongo.send_file(request.args.get('image_name'))
    if ISO != '':
        return mongo.send_file(request.args.get('metadata.ISOSpeedRating' == ISO))

    return render_template("404.html")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
