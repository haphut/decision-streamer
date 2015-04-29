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
HACKPAD_PAD_UPDATE_URL = HACKPAD_BASE_URL + '/api/1.0/pad/{}/content'
# Test pad.
HACKPAD_PAD_ID = '8PrU6rJdOj7'

# Test hackpad site.
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


def create_hackpad_heading(string, heading_level=1):
    arr = None
    if heading_level == 1:
        arr = ['<h2>', string, '</h2>']
    elif heading_level == 2:
        arr = ['<b>', string, '</b>']
    elif heading_level == 3:
        arr = ['<undefined><li><b>', string, '</b></li></undefined>']
    else:
        raise ValueError('heading_level must be an integer on the interval '
                         '[1,3].')
    return ''.join(arr)


def transform_document_to_pad(document):
    # The title is sent on the first line as plaintext, separate from the html
    # content.
    subject = document['subject']
    arr = [subject]
    arr.append('<html><body>')
    arr.append('<h1>' + subject + '</h1>')
    # Workaround for a bug in Hackpad. "</h1><h2>" does not work as expected.
    arr.append('<p></p>')
    for content_item in document['content']:
        in_english = content_item['type']
        header = in_english
        try:
            header = CONTENT_TYPES[in_english]
        except KeyError:
            print(in_english, 'in document', document['id'],
                  'is not a recognized content type.', file=sys.stderr)
        arr.append(create_hackpad_heading(header, heading_level=2))
        arr.append(content_item['text'].replace('</p>', '</p><br/>'))
    arr.append('</body></html>')
    pad = '\n'.join(arr)
    return encode_utf8(pad)


def post_to_hackpad(pad):
    hackpad = OAuth1Session(HACKPAD_CLIENT_ID,
                            client_secret=HACKPAD_CLIENT_SECRET)
    # url = HACKPAD_PAD_CREATE_URL
    url = HACKPAD_PAD_UPDATE_URL.format(HACKPAD_PAD_ID)
    r = hackpad.post(url, data=pad, headers=HACKPAD_HEADERS)
    r.raise_for_status()


def main(argv=None):
    if argv is None:
        argv = sys.argv

    document = read_openahjo()
    pad = transform_document_to_pad(document)
    post_to_hackpad(pad)


if __name__ == "__main__":
    sys.exit(main())
