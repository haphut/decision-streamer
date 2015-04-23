#!/usr/bin/env python3

import sys

import requests
from requests_oauthlib import OAuth1Session


DECISIONS_BASE_URL = 'http://dev.hel.fi'
DECISIONS_AGENDA_ITEM_URL = DECISIONS_BASE_URL + '/paatokset/v1/agenda_item/'
DECISIONS_AGENDA_ITEM_ID = 2420

DECISIONS_HEADERS = {
    'Accept': 'application/json',
    'Accept-Charset': 'utf-8'
}

HACKPAD_BASE_URL = 'https://tomaatti.hackpad.com'
HACKPAD_PAD_CREATE_URL = HACKPAD_BASE_URL + '/api/1.0/pad/create'

HACKPAD_CLIENT_ID = 'CpcCZ5uwAkw'
HACKPAD_CLIENT_SECRET = '1460Qt5KF9Up6cVqy6q7uL1z4sqOiRE6'

HACKPAD_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'text/html'
}

# Read on 2015-04-17:
# https://github.com/City-of-Helsinki/openahjo/blob/2ffd3871e77d0373fbb62f8bf7f9ac68d7d0750a/ahjodoc/doc.py#L123
CONTENT_TYPES = {
    'draft proposal': 'Esitysehdotus',
    'draft resolution': 'Päätösehdotus',
    'draft statement': 'Lausuntoehdotus',
    'hearing': 'Käsittely',
    'presenter': 'Esittelijä',
    'proposal': 'Esitys',
    'reasons for resolution': 'Päätöksen perustelut',
    'resolution': 'Päätös',
    'statement': 'Lausunto',
    'summary': 'Tiivistelmä'
}


def read_openahjo():
    url = DECISIONS_AGENDA_ITEM_URL + str(DECISIONS_AGENDA_ITEM_ID)
    r = requests.get(url)
    doc = r.json()
    return doc


def encode_utf8(string):
    # Do not raise if OpenAhjo has a mistake.
    return string.encode('utf-8', 'replace')


def transform_document_to_pad(document):
    arr = [''.join(['<h1>', document['subject'], '</h1>'])]
    for content_item in document['content']:
        arr.append(''.join(['<h2>', CONTENT_TYPES[content_item['type']],
                            '</h2>']))
        arr.append(content_item['text'])
    pad = '\n'.join(arr)
    return encode_utf8(pad)


def post_to_hackpad(pad):
    hackpad = OAuth1Session(HACKPAD_CLIENT_ID,
                            client_secret=HACKPAD_CLIENT_SECRET)
    r = hackpad.post(HACKPAD_PAD_CREATE_URL, data=pad, headers=HACKPAD_HEADERS)
    r.raise_for_status()


def main(argv=None):
    if argv is None:
        argv = sys.argv
    document = read_openahjo()
    pad = transform_document_to_pad(document)
    post_to_hackpad(pad)


if __name__ == "__main__":
    sys.exit(main())
