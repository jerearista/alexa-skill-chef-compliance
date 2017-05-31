"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import os
from botocore.vendored import requests
from pprint import pformat

API_URL = None
USER = None
HEADERS = None

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session, card_output=None):
    if card_output == None:
        card_output = output

    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - \n" + card_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def api_get(path, data=None):
    """ Do a GET to Chef Compliance and return the data.
    """

    card_title = "RESTful API Failure"
    card_output = None
    should_end_session = False

    ret = requests.get(API_URL + path, headers=HEADERS, verify=False)

    if ret.status_code == 200:
        return ret.json()
    else:
        speech_output = "I'm having trouble contacting your Chef Compliance " \
                        "server. Error {}".format(ret.status_code)
        card_output = "Compliance server returned status code {}".format(ret.status_code)
        reprompt_text = "Please verify your API_URL and AUTH_TOKEN."
        card_output = ret.status_code
        return build_response({}, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session, card_output))


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Chef Compliance sample. " \
                    "How may I assist you with your compliance validation?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me how I can help with your compliance testing. " \
    "You can ask 'what version am I running?' or 'How many users do I have?'"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using the Chef Compliance Alexa Skill. "\
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def count_users(intent, session):
    """ Counts how many users are defined in the Chef Compliance server.
    """

    card_title = intent['name']
    card_output = None
    session_attributes = {}
    should_end_session = False

    result = api_get('/users')
    count = len(result)
    card_output = pformat(result)
    if count == 0:
        speech_output = "There are no users configured"
        reprompt_text = "How else may I help you?"
    else:
        verb = "is" if count == 1 else "are"
        pl = "" if count == 1 else "s"
        speech_output = "There {} {} user{}.".format(verb, count, pl)
        reprompt_text = "How else may I help you? Or tell me to exit."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, card_output))


def check_version(intent, session):
    """ Get the Chef Compliance version.
    """

    card_title = intent['name']
    card_output = None
    session_attributes = {}
    should_end_session = False

    result = api_get('/version')

    version = result['version']
    card_output = pformat(result)
    speech_output = "The compliance server is running version {}.".format(version.replace('.', ' dot '))
    reprompt_text = "How else may I help you? Or tell me to exit."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, card_output))


def get_summary(intent, session):
    """ Get the Chef Compliance user's summary.

    {
      "nodeCount": 28,
      "envCount": 6
    }
    """

    card_title = intent['name']
    card_output = None
    session_attributes = {}
    should_end_session = False

    result = api_get('/owners/{}/summary'.format(USER))

    nodes = result['nodeCount']
    envs = result['envCount']
    card_output = pformat(result)
    speech_output = "You have {} nodes and {} environments.".format(nodes, envs)
    reprompt_text = "How else may I help you? Or tell me to exit."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, card_output))


def get_scans(intent, session):
    """ Get the Chef Compliance user's scan reports.

    [
      {
        "id": "a74566b9-b527-437f-480f-e56c5b8a1791",
        "owner": "7ae9dd7d-5201-4ae3-4949-60eb4b902e77",
        "start": "2015-05-22T01:10:37.133367688Z",
        "end": "2015-05-22T01:10:42.491573741Z",
        "nodeCount": 1,
        "complianceProfiles": 1,
        "patchlevelProfiles": 1,
        "complianceStatus": 0,
        "patchlevelStatus": 0,
        "unknownStatus": 0,
        "failedCount": 0
      }
    ]
    """

    card_title = intent['name']
    card_output = None
    session_attributes = {}
    should_end_session = False

    result = api_get('/owners/{}/sscans'.format(USER))

    count = len(result)
    report = result[-1]
    profiles = report['complianceProfiles']
    failed = report['failedCount']
    nodes = report['nodeCount']
    status = report['complianceStatus']
    """
    {u'complianceProfiles': 1,\n  u'complianceStatus': 0.5,\n  u'end': u'2017-05-24T03:08:24.421499Z',\n  u'failedCount': 0
    """
    card_output = pformat(report)
    speech_output = "You have {} reports. " \
    "The latest report scanned {} profiles on {} devices. {} failed. Status is {}".format(count, profiles, nodes, failed, status)
    reprompt_text = "How else may I help you? Or tell me to exit."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, card_output))


def get_report_detail(intent, session):
    """ Get the details of the user's last report.

    [
      {
        "id": "a74566b9-b527-437f-480f-e56c5b8a1791",
        "owner": "7ae9dd7d-5201-4ae3-4949-60eb4b902e77",
        "start": "2015-05-22T01:10:37.133367688Z",
        "end": "2015-05-22T01:10:42.491573741Z",
        "nodeCount": 1,
        "complianceProfiles": 1,
        "patchlevelProfiles": 1,
        "complianceStatus": 0,
        "patchlevelStatus": 0,
        "unknownStatus": 0,
        "failedCount": 0
      }
    ]
    """

    card_title = intent['name']
    card_output = None
    session_attributes = {}
    should_end_session = False

    result = api_get('/owners/{}/scans'.format(USER))
    scan_id = result[-1]['id']

    result = api_get('/owners/{}/scans/{}'.format(USER, scan_id))

    summary = result['complianceSummary']
    """
      "complianceSummary": {
          "success": 0,
          "minor": 0,
          "major": 43,
          "critical": 2,
          "skipped": 0,
          "total": 45
      }
    """
    speech_output = " Checked {} items. {} succeded.".format(summary['total'], summary['success'])
    # Update above to loop through keys > 0 then only report on values > 0.
    for key, value in summary.items():
        if value == 0:
            continue
        if key == "total" or key == "success":
            continue
        speech_output += " {} {} items.".format(value, key)

    card_output = pformat(summary)
    reprompt_text = "How else may I help you? Or tell me to exit."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, card_output))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    # For hackday, get server and credentials from the Lambda ENV.
    global API_URL
    global HEADERS
    global USER
    USER = os.environ.get("USER", None)
    API_URL = os.environ.get("API_URL", None)
    auth_token = os.environ.get("AUTH_TOKEN", None)

    HEADERS = {"Accept": "applicaiton/json",
               "Content-type": "application/json",
               "Authorization": "Bearer " + auth_token}

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "CountUsers":
        return count_users(intent, session)
    elif intent_name == "getVersion":
        return check_version(intent, session)
    elif intent_name == "ownerSummary":
        return get_summary(intent, session)
    elif intent_name == "getOwnerScans":
        return get_scans(intent, session)
    elif intent_name == "reportDetail":
        return get_report_detail(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """ Uncomment this if statement and populate with your skill's application
    ID to prevent someone else from configuring a skill that sends requests to
    this function.
    """
    # if (event['session']['application']['applicationId'] !=
    # "amzn1.ask.skill.some_id"): raise
    # ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
