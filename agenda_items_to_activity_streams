#!/usr/bin/env python3

import json
import pdb
import sys
import time
import uuid

import requests


AGENDA_ITEM_URL = 'http://dev.hel.fi/paatokset/v1/agenda_item/'
# FIXME: Where is the parameter meeting__policymaker__origin_id documented?
CITY_COUNCIL_ID = '02900'
PAYLOAD = {'format': 'json', 'order_by': '-meeting__date',
           'meeting__policymaker__origin_id': CITY_COUNCIL_ID}

ACTIVITY_STREAMS_API_URL = 'http://localhost:8080/'
ACTIVITY_STREAMS_USERS_URL = ACTIVITY_STREAMS_API_URL + 'users/'
USERNAME = 'Helsinki Decisions'


# FIXME: Create a class for agenda items. The class should do correctness checking.


# FIXME: Log erroneous data but don't crash.
def transform_agenda_item_to_activity_stream(agenda_item):
    # FIXME: Should we have less hardcoding and more reading of APIs here?
    ACTOR = {
        'objectType': 'decisionmaker',
        'id': 'urn:hel.fi:decisionmaker:02900',
        'displayName': {
            'fi': 'Kaupunginvaltuusto',
            'sv': 'Kommunfullmäktige',
            'en': 'City Council'
        },
        'url': 'http://dev.hel.fi/paatokset/paattaja/kvsto/'
    }

    issue = agenda_item['issue']
    display_name = issue['subject']
    summary = issue['summary']
    slug = issue['slug']
    # FIXME: Check that you picked the right timestamp.
    # FIXME: Check datetime for correctness.
    last_modified = agenda_item['last_modified_time']
    permalink = agenda_item['permalink']
    # FIXME: Check that the id is correct. It has one digit less than the example.
    agenda_item_id = str(agenda_item['id'])

    activity_stream = {
        'verb': 'add',
        'published': last_modified,
        'actor': ACTOR,
        'object': {
            'objectType': 'issue',
            'id': ''.join(['urn:hel.fi:issue:', slug]),
            'displayName': {
                'fi': display_name
            },
            'content': summary,
            'url': permalink
        },
        'target': {
            'objectType': 'meeting'
            ## FIXME: where is the meeting id? It is available from the url in agenda_item['meeting']['policymaker'] http://dev.hel.fi/paatokset/v1/policymaker/5/
            ## FIXME: Collect all policymaker urls, unique them, request them
            #'id': ''.join(['urn:hel.fi:meeting:', CITY_COUNCIL_ID, '-', 'FOOBAR'])
            ## FIXME: How to construct the url? The time is unclear.
            ## The following is just an example:
            #'url': 'http://dev.hel.fi/paatokset/paattaja/kvsto/2014/11/'
        },
        'result': {
            'objectType': 'agenda_item',
            'id': ''.join(['urn:hel.fi:agenda_item:', agenda_item_id]),
            # FIXME: url needs to be constructed, it might be permalink + missing target_url part
            'url': permalink,
            'displayName': {
                'fi': display_name
            }
        }
    }
    return activity_stream

def poll_decisions(last_modified=None):
    # FIXME: Use last_modified.
    # FIXME: Read all pages.
    r = requests.get(AGENDA_ITEM_URL, params=PAYLOAD)
    try:
        response = r.json()
    except ValueError as e:
        print(e, file=sys.stderr)
    return response

def get_last_modification_time(activity_streams):
    #[foo for stream in activity_streams]
    pass

def push_activity_streams(username, activity_streams):
    pass

def create_user(username):
    r = requests.get(ACTIVITY_STREAMS_USERS_URL)
    res = r.json()
    names = (item['name'] for item in res['items'])
    if not username in names:
        userId = str(uuid.uuid4())
        post_r = requests.post(ACTIVITY_STREAMS_USERS_URL + '/' + userId,
                               data={'user': username})
        # FIXME: Check response

def update_activity_streams():
    last_modified = None
    interval_in_seconds = 30
    username = USERNAME

    create_user(username)

    # FIXME: Make python wake up every n seconds instead of sleeping for n.
    while True:
        response = poll_decisions(last_modified)
        activity_streams = [transform_agenda_item_to_activity_stream(agenda_item)
                            for agenda_item in response['objects']]
        last_modified = get_last_modification_time(activity_streams)
        push_activity_streams(username, activity_streams)
        time.sleep(interval_in_seconds)


def main(argv = None):
    if argv is None:
        argv = sys.argv
    update_activity_streams()


if __name__ == "__main__":
        sys.exit(main())
