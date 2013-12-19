#!usr/bin/python2.7

from flask import Flask, render_template, request, escape

application = app = Flask(__name__) # AWS mod_wgsi looks for "application"
# app.debug=True # only in dev

@app.route('/')
def hello_world():
    return render_template("_base.html")

if __name__ == '__main__':
    app.run()