"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


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
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Ask a Maester. Try asking who is Jon Snow."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Ask about a character such as, " \
                    "who is Jon Snow."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


_CHAR_INFO = {
    "Catelyn Stark": "Lady Catelyn Stark also called Catelyn Tully is the wife of Lord Eddard Stark and Lady of Winterfell. Together they have five children: Robb, Sansa, Arya, Bran, and Rickon. Catelyn was born into House Tully of Riverrun, the liege lords of the riverlands. She is the daughter of Lord Hoster Tully and Lady Minisa Whent, and her siblings are Lysa and Edmure.",
    "Jon Snow": "Jon Snow is the bastard son of Eddard Stark, by a mother whose identity is a source of speculation. He was raised by his father alongside his true-born half-siblings, but joins the Night's Watch when he nears adulthood. He is constantly accompanied by his albino direwolf Ghost. At the beginning of A Game of Thrones, Jon is fourteen years old. He is one of the major POV characters in the books. In the television adaptation Game of Thrones, Jon is portrayed by Kit Harington.",
    "Eddard Stark": "Eddard Stark, also called Ned, is the head of House Stark, Lord of Winterfell, and Warden of the North. He is a close friend to King Robert I Baratheon, with whom he was raised. Eddard is one of the major POV characters in the books. In the television adaptation Game of Thrones, he is played by Sean Bean in Season 1 and by Sebastian Croft and Robert Aramayo during flashbacks in Season 6.",
    "Daenerys Targaryen": "Princess Daenerys Targaryen, known as Daenerys Stormborn and Dany, is one of the last confirmed members of House Targaryen, along with her older brother Viserys, and she is one of the major POV characters in A Song of Ice and Fire. In the television adaptation Game of Thrones, Daenerys is played by Emilia Clarke.",
    "Tyrion Lannister": "Tyrion Lannister is a member of House Lannister and is the third and youngest child of Lord Tywin Lannister and the late Joanna Lannister. His older siblings are Cersei Lannister, the queen of King Robert Baratheon, and Ser Jaime Lannister, a knight of Robert's Kingsguard. Tyrion is a dwarf; because of this he is sometimes mockingly called the Imp and the Halfman. He is one of the major POV characters in the books. In the television adaptation Game of Thrones, Tyrion is played by Peter Dinklage.",
    "Arya Stark": "Arya Stark is the third child and second daughter of Lord Eddard Stark and Lady Catelyn Tully. A member of House Stark, she has five siblings: brothers Robb, Bran, Rickon, half-brother Jon Snow, and older sister Sansa. She is a POV character in A Song of Ice and Fire and is portrayed by Maisie Williams in the television adaptation, Game of Thrones. Like some of her siblings, Arya sometimes dreams that she is a direwolf. Her own direwolf is Nymeria, who is named in reference to the Rhoynar warrior-queen of the same name."
}

CHAR_INFO = {k.lower(): v for k, v in _CHAR_INFO.items()}


def get_character_info(intent, session):
    """Get information about a character"""

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    character = get_slot_value(intent, "character")

    if not character:
        speech_output = "I'm not sure who you meant. Please try again."
        reprompt_text = "I'm not sure who you meant. You can ask by saying, who is Jon Snow."
    elif character.lower() in CHAR_INFO:
        card_title = character
        speech_output = CHAR_INFO[character.lower()]
        reprompt_text = CHAR_INFO[character.lower()]
    else:
        speech_output = "I don't know {}. Please try again.".format(character)
        reprompt_text = "I don't know {}. You can ask by saying, who is Jon Snow.".format(character)

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


HOUSE_WORDS = {u'allyrion': u'No Foe May Pass',
               u'ambrose': u'Never Resting',
               u'arryn': u'As High as Honor',
               u'ashford': u'Our Sun Shines Bright',
               u'baratheon': u'Ours is the Fury',
               u'beesbury': u'Beware Our Sting',
               u'bolton': u'Our Blades Are Sharp',
               u'buckwell': u'Pride and Purpose',
               u'bulwer': u'Death Before Disgrace',
               u'caron': u'No Song So Sweet',
               u'cerwyn': u'Honed and Ready',
               u'codd': u'Though All Men Do Despise Us',
               u'crakehall': u'None so Fierce',
               u'egen': u'By Day or Night',
               u"flint of widow's watch": u'Ever Vigilant',
               u'follard': u'None so Wise',
               u'footly': u'Tread Lightly Here',
               u'fossoway of cider hall': u'A Taste of Glory',
               u'fowler': u'Let Me Soar',
               u'graceford': u'Work Her Will',
               u'grandison': u'Rouse Me Not',
               u'greyjoy': u'We Do Not Sow',
               u'hastwyck': u'None So Dutiful',
               u'hightower': u'We Light the Way',
               u'hornwood': u'Righteous in Wrath',
               u'jordayne': u'Let It Be Written',
               u'karstark': u'The Sun of Winter',
               u'lannister': u'Hear Me Roar! Their unofficial motto, just as well known, states, "A Lannister always pays his debts."',
               u'lonmouth': u'The Choice Is Yours',
               u'mallister': u'Above the Rest',
               u'marbrand': u'Burning Bright',
               u'martell': u'Unbowed, Unbent, Unbroken',
               u'merryweather': u'Behold Our Bounty',
               u'mooton': u'Wisdom and Strength',
               u'mormont': u'Here We Stand',
               u'oakheart': u'Our Roots Go Deep',
               u'peckledon': u'Unflinching',
               u'penrose': u'Set Down Our Deeds',
               u'piper': u'Brave and Beautiful',
               u'plumm': u'Come Try Me',
               u'redfort': u'As Strong as Stone',
               u'royce': u'We Remember',
               u'sarsfield': u'True to the Mark',
               u'serrett': u'I Have No Rival',
               u'smallwood': u'From These Beginnings',
               u'stark': u'Winter is Coming',
               u'stokeworth': u'Proud to Be Faithful',
               u'swyft': u'Awake! Awake!',
               u'swygert': u'Truth Conquers',
               u'tallhart': u'Proud and Free',
               u'targaryen': u'Fire and Blood',
               u'tarly': u'First in Battle',
               u'tollett': u'When All is Darkest',
               u'toyne': u'Fly High, Fly Far',
               u'trant': u'So End Our Foes',
               u'tully': u'Family, Duty, Honor',
               u'tyrell': u'Growing Strong',
               u'velaryon': u'The Old, the True, the Brave',
               u'waxley': u'Light in Darkness',
               u'wendwater': u'For All Seasons',
               u'wensington': u'Sound the Charge',
               u'westerling': u'Honor, not Honors',
               u'wode': u'Touch Me Not',
               u'wydman': u'Right Conquers Might',
               u'yronwood': u'We Guard the Way'}


def get_house_words(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    house = get_slot_value(intent, "house")

    if not house:
        speech_output = "I'm not sure which house you meant. Please try again."
        reprompt_text = "I'm not sure which house you meant. You can ask by saying, what are the words of house stark."
    elif house.lower() in HOUSE_WORDS:
        card_title = house
        speech_output = HOUSE_WORDS[house.lower()]
        reprompt_text = HOUSE_WORDS[house.lower()]
    else:
        speech_output = "I don't have information on house {}. Please try again.".format(house)
        reprompt_text = "I don't recognize house {}. You can ask by saying, what are the words of house stark.".format(house)

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_actor(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    character = get_slot_value(intent, "character")

    if not character:
        speech_output = "I'm not sure who you mean. Please try again."
        reprompt_text = "I'm not sure who you mean. You can ask by saying, who plays Tyrion Lannister."
    elif character.lower() in CHAR2ACTOR:
        card_title = character
        actor = CHAR2ACTOR[character.lower()]

        speech_output = "{} is played by {}".format(character, actor)
        reprompt_text = speech_output
    else:
        speech_output = "I don't know who plays {}. Sorry.".format(character)
        reprompt_text = "I don't know who plays {}. You can ask by saying, who plays Tyrion Lannister.".format(character)

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_roles_string(roles):
    if len(roles) == 1:
        return roles[0]
    elif len(roles) == 2:
        return " and ".join(roles)
    else:
        front = ", ".join(roles[:-1])
        return front + ", and" + roles[-1]


def get_other_roles(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    actor = get_slot_value(intent, "actor")

    if not actor:
        speech_output = "I'm not sure who you mean. Please try again."
        reprompt_text = "I'm not sure who you mean. You can ask by saying, what else has Lena Headley starred in."
    elif actor.lower() in ACTOR2ROLES:
        card_title = actor
        speech_output = "{} has also starred in {}".format(actor, get_roles_string(ACTOR2ROLES[actor.lower()]))
        reprompt_text = speech_output
    else:
        speech_output = "I don't know about {}. Sorry.".format(actor)
        reprompt_text = "I don't know about {}. You can ask by saying, who plays Tyrion Lannister.".format(actor)

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------

def get_slot_value(intent, slot):
    if slot not in intent["slots"]:
        return None

    return intent["slots"][slot].get("value")


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
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