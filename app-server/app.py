import os
import string
import random

import requests
from requests.exceptions import MissingSchema, HTTPError

from flask import Flask, render_template, request, redirect

from postgres import PostgresDBase
from postgres import InvalidShortId


SYMBOLS = string.ascii_lowercase + string.digits + string.ascii_uppercase
MAIN_URL = 'http://46.30.41.247'


def generate_short_id(size=7):
    return ''.join(random.choice(SYMBOLS) for _ in range(size))


def is_valid_link(link: str) -> bool:
    try:
        response = requests.get(link, timeout=5)
    except MissingSchema:
        return False

    try:
        response.raise_for_status()
    except HTTPError:
        return False
    return response.ok


app = Flask(__name__)
db = PostgresDBase(host=os.getenv('POSTGRES_HOST'),
                   port=int(os.getenv('POSTGRES_PORT')),
                   user=os.getenv('POSTGRES_USER'),
                   password=os.getenv('POSTGRES_PASSWORD'),
                   dbase_name=os.getenv('DB_NAME'))


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/<short_id>')
def open_page(short_id: str):
    origin_link = db.get_origin_link_by_short_id(short_id)
    if not origin_link:
        return render_template('404.html')
    return redirect(origin_link)


@app.route('/ping', methods=['GET'])
def ping():
    return {'is-success': True, 'message': 'Is alive'}


@app.route('/add-link', methods=['POST'])
def add_link():
    json_info = request.json
    link = json_info['origin-link']
    days_count = json_info['days-count']

    messages = []
    if not is_valid_link(link):
        messages.append('Invalid link')
    if not 0 <= days_count < 31:
        messages.append('Invalid days count - limit is 0-30 days')

    if messages:
        return {
            'is-success': False,
            'message': '\n'.join(messages),
            'short-link': ''
        }

    while True:
        short_id = generate_short_id()
        try:
            short_id = db.add_link(link, days_count, short_id)
            break
        except InvalidShortId:
            continue

    url = f'{MAIN_URL}/{short_id}'
    return {
        'is-success': True,
        'message': 'Success',
        'short-link': url
    }
