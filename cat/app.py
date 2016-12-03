from flask import Flask, render_template, redirect, abort, request, url_for, Response
catapp = Flask(__name__)

@catapp.route("/search")
def main():
    return "Hello Code And Talk"
