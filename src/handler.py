"""
Main handling code for Amazon Lambda
"""

from __future__ import print_function

import json
import random

import networking
import private
import re

TRY_AGAIN = "Please try again."


def lc_keys(mapping):
    """Lowercase the keys of a dict"""
    return {k.lower(): v for k, v in mapping.iteritems()}


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" + event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """
    Called when the user launches the skill without specifying what they
    want like "Alexa open Ask a maester
    """

    print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
    return get_welcome_response()


def on_intent(intent_request, session):
    """Called when the user specifies an intent for this skill like Alexa ask a maester who is Jon Snow"""

    print("on_intent sessionId={}, request={}".format(session["sessionId"], json.dumps(intent_request)))

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetCharacterInfo":
        return get_character_info(intent, session)
    elif intent_name == "GetHouseWords":
        return get_house_words(intent, session)
    elif intent_name == "GetActor":
        return get_actor(intent, session)
    elif intent_name == "GetOtherRoles":
        return get_other_roles(intent, session)
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
    print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hello there. You can ask who is Jon Snow, what are the words of House Stark, who plays Arya Stark, or what else has Lena Headey starred in."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Ask about a character such as, who is Jon Snow."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Valar dohaeris"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))


_CHAR_INFO = {
    "Catelyn Stark": "Lady Catelyn Stark also called Catelyn Tully is the wife of Lord Eddard Stark and Lady of Winterfell. Together they have five children: Robb, Sansa, Arya, Bran, and Rickon. Catelyn was born into House Tully of Riverrun, the liege lords of the riverlands. She is the daughter of Lord Hoster Tully and Lady Minisa Whent, and her siblings are Lysa and Edmure.",
    "Jon Snow": "Jon Snow is the bastard son of Eddard Stark, by a mother whose identity is a source of speculation. He was raised by his father alongside his true-born half-siblings, but joins the Night's Watch when he nears adulthood. He is constantly accompanied by his albino direwolf Ghost. At the beginning of A Game of Thrones, Jon is fourteen years old. He is one of the major POV characters in the books. In the television adaptation Game of Thrones, Jon is portrayed by Kit Harington.",
    "Eddard Stark": "Eddard Stark, also called Ned, is the head of House Stark, Lord of Winterfell, and Warden of the North. He is a close friend to King Robert I Baratheon, with whom he was raised. Eddard is one of the major POV characters in the books. In the television adaptation Game of Thrones, he is played by Sean Bean in Season 1 and by Sebastian Croft and Robert Aramayo during flashbacks in Season 6.",
    "Daenerys Targaryen": "Princess Daenerys Targaryen, known as Daenerys Stormborn and Dany, is one of the last confirmed members of House Targaryen, along with her older brother Viserys, and she is one of the major POV characters in A Song of Ice and Fire. In the television adaptation Game of Thrones, Daenerys is played by Emilia Clarke.",
    "Tyrion Lannister": "Tyrion Lannister is a member of House Lannister and is the third and youngest child of Lord Tywin Lannister and the late Joanna Lannister. His older siblings are Cersei Lannister, the queen of King Robert Baratheon, and Ser Jaime Lannister, a knight of Robert's Kingsguard. Tyrion is a dwarf; because of this he is sometimes mockingly called the Imp and the Halfman. He is one of the major POV characters in the books. In the television adaptation Game of Thrones, Tyrion is played by Peter Dinklage.",
    "Arya Stark": "Arya Stark is the third child and second daughter of Lord Eddard Stark and Lady Catelyn Tully. A member of House Stark, she has five siblings: brothers Robb, Bran, Rickon, half-brother Jon Snow, and older sister Sansa. She is a POV character in A Song of Ice and Fire and is portrayed by Maisie Williams in the television adaptation, Game of Thrones. Like some of her siblings, Arya sometimes dreams that she is a direwolf. Her own direwolf is Nymeria, who is named in reference to the Rhoynar warrior-queen of the same name."
}

CHAR_INFO = lc_keys(_CHAR_INFO)


def get_character_info(intent, session):
    """Get information about a character"""

    card_title = intent['name']
    title_format = "About {}"
    session_attributes = {}
    should_end_session = True

    character = get_slot_value(intent, "character")

    example = "You can ask by saying, who is {}.".format(random.choice(CHAR_INFO.keys()))

    if not character:
        base_error = "I'm not sure who you mean."
        speech_output = base_error + " " + TRY_AGAIN
        reprompt_text = base_error + " " + example
    else:
        hits = search("char_summary", {"name": character})
        if hits:
            result = hits[0]
            card_title = title_format.format(result["_source"]["name"])

            speech_output = result["_source"]["summary"]
            reprompt_text = speech_output
        else:
            base_error = "I don't know about {}.".format(character)
            card_title = title_format.format(character)
            speech_output = base_error + " " + TRY_AGAIN
            reprompt_text = base_error + " " + example

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_house_words(intent, session):
    card_title = intent['name']
    title_format = "The words of House {}"
    session_attributes = {}
    should_end_session = True

    house = get_slot_value(intent, "house")

    example = "You can ask by saying, what are the words of house {}.".format("Stark")

    if not house:
        base_error = "I'm not sure which house you mean."
        speech_output = base_error + " " + TRY_AGAIN
        reprompt_text = base_error + " " + example
    else:
        house_hits = search("house", {"name": house})
        if house_hits:
            result = house_hits[0]
            card_title = title_format.format(result["_source"]["name"])

            speech_output = result["_source"]["words"]
            reprompt_text = speech_output
        else:
            base_error = "I don't know the words of house {}.".format(house)
            card_title = title_format.format(house)
            speech_output = base_error + " " + TRY_AGAIN
            reprompt_text = base_error + " " + example

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_actor(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True

    character = get_slot_value(intent, "character")

    example = "You can ask by saying, who plays {}.".format("Arya Stark")

    if not character:
        base_error = "I'm not sure who you mean."
        speech_output = base_error + " " + TRY_AGAIN
        reprompt_text = base_error + " " + example
    else:
        actor_hit = search("character", {"name": character})

        if actor_hit:
            card_title = character
            actors = actor_hit[0]["_source"]["actors"]
            character_long = actor_hit[0]["_source"]["name"]

            speech_output = "{} is played by {}".format(character_long, generate_and(actors))
            reprompt_text = speech_output
        else:
            base_error = "I don't know who plays {}.".format(character)
            speech_output = base_error + " " + TRY_AGAIN
            reprompt_text = base_error + " " + example

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def generate_and(strings):
    if len(strings) == 1:
        return strings[0]
    elif len(strings) == 2:
        return " and ".join(strings)
    else:
        front = ", ".join(strings[:-1])
        return front + ", and " + strings[-1]


def get_other_roles(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True

    actor = get_slot_value(intent, "actor")

    example = "You can ask by saying, what else has {} starred in.".format("Emilia Clarke")

    if not actor:
        base_error = "I'm not sure who you mean."
        speech_output = base_error + " " + TRY_AGAIN
        reprompt_text = base_error + " " + example
    else:
        actor_hits = search("actor", {"name": actor})

        if actor_hits and actor_hits[0]["_source"]["other_roles"]:
            card_title = actor
            other_roles = actor_hits[0]["_source"]["other_roles"]
            speech_output = "{} has also starred in {}".format(actor, generate_and(other_roles))
            reprompt_text = speech_output
        else:
            base_error = "I don't know about {}'s other roles.".format(actor)
            speech_output = base_error + " " + TRY_AGAIN
            reprompt_text = base_error + " " + example


    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Helpers that build all of the responses ----------------------


def search(doc_type, query_doc, min_score=0):
    """
    search the DB for matching information

    Note: I haven't tested this when ES is down or firewalled.
    :param doc_type: The database table (Elastic search sort of calls them types)
    :param query_doc: dict listing the fields and field values to search
    :param min_score: Filter any results below this score
    :return: List of elasticsearch documents with score (info is in _source)
    """
    assert isinstance(query_doc, dict)
    es = networking.get_elasticsearch()
    with_and = {k: {"query": v, "operator": "and"} for k, v in query_doc.items()}
    res = es.search(index=private.ES_INDEX, doc_type=doc_type, body={"query": {"match": with_and}})

    return [result for result in res["hits"]["hits"] if result["_score"] >= min_score]


def munge_speech_response(text):
    if not text:
        return text

    mapping = {"Dany": "Danny", "POV": "P.O.V.", "Edmure": "Edmiure", "Sandor": "Sandore"}

    for source, target in mapping.iteritems():
        text = re.sub(r"\b{}\b".format(re.escape(source)), target, text)

    return text

def get_slot_value(intent, slot):
    if slot not in intent["slots"]:
        return None

    return intent["slots"][slot].get("value")


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': munge_speech_response(output)
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': munge_speech_response(reprompt_text)
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.1',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
