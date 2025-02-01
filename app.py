from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app