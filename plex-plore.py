from flask import Flask, make_response, render_template, Response, redirect
import requests
import time
import xml4h
import argparse

app = Flask(__name__)
server_addr = ''

def format_seconds(total_seconds):
    hours = int(total_seconds / (60 * 60))
    minutes = int(total_seconds / 60) - (hours * 60)
    seconds = total_seconds - (minutes * 60) - (hours * 60 * 60)
    return "%.2d:%.2d:%.2d" % (hours, minutes, seconds)


def pretty_print(server, location, xml_node):
    links = ["key", "parentKey"]
    images = ["art", "thumb", "parentThumb", "banner"]
    durations = ["duration"]
    dates = ["updatedAt", "addedAt"]

    def make_attribute(key, value):
        link = info = None
        preview = False
        # Resolve the relative or absolute URL to our server prefixed version
        if key in links:
            if value.startswith("/"):
                link = server + value + "/"
            else:
                link = server + "/" + location + value + "/"
        elif key in images:
            link = server + value
            preview = True

        if key in durations:
            info = format_seconds(int(value) / 1000)
        elif key in dates:
            info = time.ctime(int(value))

        return { "key": key, "value": value, "link": link, "preview": preview, "info": info}

    try:
        name = xml_node.name
    except AttributeError:
        name = "Document"

    if xml_node.attributes:
        node_attributes = xml_node.attrs.items()
    else:
        node_attributes = []

    attributes = [ make_attribute(key, value) for (key, value) in node_attributes]
    children = [pretty_print(server, location, child) for child in xml_node.children()]

    return { "name": name, "attributes": attributes, "children": children }


@app.route('/')
def index():
    return redirect('/api/')

@app.route('/api/')
@app.route('/api/<path:url>')
def pretty_plex(url=''):
    plex = requests.get("http://" + server_addr + "/" + url)
    server = "/api"

    if 'text/xml' in plex.headers['content-type']:
        document = xml4h.parse(plex.text.encode('utf-8'))

        # Parse document into pretty printed node and attributes
        return make_response(render_template('api.html', document=pretty_print(server, url, document.children[0])), plex.status_code)
    else:
        return Response(plex.content, mimetype=plex.headers["content-type"])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plex API broswser')

    parser.add_argument('--port', metavar='PORT', type=int,
                        default=5000,
                        help='Port to run webserver, default to 5000')

    parser.add_argument('--debug', action='store_true',
                        help='Print stacktraces')

    parser.add_argument('server', metavar='SERVER', nargs='?',
                        default='127.0.0.1:32400',
                        help='Plex Media Server address')

    args = parser.parse_args()

    server_addr = args.server

    app.run(debug=args.debug, port=args.port)
