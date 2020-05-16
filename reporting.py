from flask import render_template
import flask
app = flask.Flask('my app')
def reporting(data, title, file_name):
    Html_file= open(file_name,"w")
    with app.app_context():
        rendered = render_template("format.html", \
            title = title, \
            people = data)
        Html_file.write(rendered)
    Html_file.close()

# data = [{"name": "images/picture.jpg"}, {"name": "images/picture.jpg"}]
# title = "True Crawler Result"
# file_name = 'format.html'
# reporting(data, title, file_name)
