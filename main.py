import os
from flask import Flask, Response, request, abort, render_template, send_from_directory, send_file
from io import BytesIO
from PIL import Image

app = Flask(__name__)

WIDTH = 700
HEIGHT = 600


@app.route('/cards/<path:filename>')
def image(filename):
    try:
        w = int(request.args['w'])
        h = int(request.args['h'])
    except (KeyError, ValueError):
        print(os.path.dirname(__file__) + '/cards/'+ filename)
        return send_from_directory(os.path.dirname(__file__) + '/cards', filename)

    try:
        path = os.path.join(os.path.dirname(__file__) + '/cards', filename)
        im = Image.open(path)
        im.thumbnail((w, h), Image.ANTIALIAS)
        io = BytesIO()
        im.save(io, format='PNG')
        io.seek(0)
        return send_file(io, mimetype='image/png')

    except IOError as e:
        print(e)
        abort(404)

    return send_from_directory(os.path.dirname(__file__) + '/cards', filename)


@app.route('/')
def index():
    images = []
    for root, dirs, files in os.walk('./cards/'):
        for filename in [os.path.join(root, name) for name in files]:
            if not filename.endswith('.jpg'):
                continue
            im = Image.open(filename+"-upper.png")
            w, h = im.size
            aspect = 1.0*w/h
            if aspect > 1.0*WIDTH/HEIGHT:
                width = min(w, WIDTH)
                height = width/aspect
            else:
                height = min(h, HEIGHT)
                width = height*aspect
            images.append({
                'width': int(width),
                'height': int(height),
                'src': filename
            })

    return render_template('main.html', **{
        'images': images
    })


if __name__ == '__main__':
    app.run()