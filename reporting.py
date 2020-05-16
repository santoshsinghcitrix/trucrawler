from flask import render_template
import flask
app = flask.Flask('my app')
def reporting(data, title, file_name):
    with app.app_context():
        rendered = render_template(file_name, \
            title = title, \
            people = data)
        print(rendered)

# data = [{"name": "images/picture.jpg"}, {"name": "images/picture.jpg"}]
# title = "True Crawler Result"
# file_name = 'format.html'
# reporting(data, title, file_name)
