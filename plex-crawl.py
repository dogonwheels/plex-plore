from flask import Flask, make_response, render_template, Response
import requests
import xml4h

app = Flask(__name__)


@app.route('/')
@app.route('/<path:url>')
def pretty_plex(url=''):
    plex = requests.get("http://127.0.0.1:32400/" + url)

    if 'text/xml' in plex.headers['content-type']:
        document = xml4h.parse(plex.text)
        return make_response(render_template('api.html', document=document), plex.status_code)
    else:
        return Response(plex.content, mimetype=plex.headers["content-type"])

if __name__ == '__main__':
    app.run(debug=True)
