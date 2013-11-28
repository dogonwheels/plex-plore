from flask import Flask, make_response, render_template, Response
import requests
import time
import xml4h

app = Flask(__name__)

def format_seconds(total_seconds):
    hours = int(total_seconds / (60 * 60))
    minutes = int(total_seconds / 60) - (hours * 60)
    seconds = total_seconds - (minutes * 60) - (hours * 60 * 60)
    return "%.2d:%.2d:%.2d" % (hours, minutes, seconds)


def pretty_print(xml_node):
    links = ["key", "parentKey"]
    images = ["art", "thumb", "parentThumb", "banner"]
    durations = ["duration"]
    dates = ["updatedAt", "addedAt"]

    def make_attribute(key, value):
        link = info = None
        preview = False
        if key in links:
            link = value
        elif key in images:
            link = value
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
    children = [pretty_print(child) for child in xml_node.children()]

    return { "name": name, "attributes": attributes, "children": children }


@app.route('/')
@app.route('/<path:url>')
def pretty_plex(url=''):
    plex = requests.get("http://127.0.0.1:32400/" + url)

    if 'text/xml' in plex.headers['content-type']:
        document = xml4h.parse(plex.text.encode('utf-8'))

        # Parse document into pretty printed node and attributes
        return make_response(render_template('api.html', document=pretty_print(document.children[0])), plex.status_code)
    else:
        return Response(plex.content, mimetype=plex.headers["content-type"])

if __name__ == '__main__':
    app.run(debug=True)
