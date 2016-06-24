from __future__ import unicode_literals
from __future__ import print_function
import sys
import argparse
import unittest
import handler

from import_imdb import get_aliases


def parse_args():
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def main():
    args = parse_args()


if __name__ == "__main__":
    sys.exit(main())


class AssortedTests(unittest.TestCase):
    def test_aliases(self):
        self.assertSequenceEqual(["Hai"], get_aliases("Hai"))
        self.assertSequenceEqual(["Zachary Scuderi", "Sneaky"], get_aliases("Zachary 'Sneaky' Scuderi"))

    def test_speech_munge(self):
        self.assertEqual("Danny", handler.munge_speech_response("Dany"))
        self.assertEqual("Hi there", handler.munge_speech_response("Hi there"))


def make_session(new=True, session_id="session1234", user_id="user1234"):
    return {
        "new": new,
        "sessionId": session_id,
        "attributes": {},
        "user": {
            "userId": user_id
        },
        "application": {
            "applicationId": "amzn1.echo-sdk-ams.app.[unique-value-here]"
        }
    }


def make_intent_request(intent_name, slot_value, request_id="request5678"):
    return {
        "intent": {
            "slots": slot_value,
            "name": intent_name
        },
        "type": "IntentRequest",
        "requestId": request_id,
        "timestamp": "2016-06-24T04:25:19Z",
        "locale": "en-US"
    }


def make_input(intent, slot_map):
    return {
        "session": make_session(False),
        "version": "1.0",
        "request": make_intent_request(intent, {k: {"name": k, "value": v} for k, v in slot_map.items()})
    }


def get_speech_output(response):
    return response["response"]["outputSpeech"]["text"]


def make_help_input():
    return {
        "session": make_session(True),
        "request": make_intent_request("AMAZON.HelpIntent", {}),
        "version": "1.0"
    }


def make_stop_input():
    return {
        "session": make_session(False),
        "request": make_intent_request("AMAZON.StopIntent", {}),
        "version": "1.0"
    }


class TestIntents(unittest.TestCase):
    def setUp(self):
        self.context = None

    def _assert_normal(self, response):
        self.assertIsNotNone(response)
        self.assertIn("version", response)
        self.assertIn("response", response)
        self.assertIn("outputSpeech", response["response"])
        self.assertIn("text", response["response"]["outputSpeech"])
        self.assertIn("sessionAttributes", response)
    
    def test_help(self):
        response = handler.lambda_handler(make_help_input(), self.context)
        self._assert_normal(response)
        self.assertIn("Hello", get_speech_output(response))
        self.assertFalse(response["response"]["shouldEndSession"])

    def test_stop(self):
        response = handler.lambda_handler(make_stop_input(), self.context)
        self._assert_normal(response)
        self.assertTrue(response["response"]["shouldEndSession"])

    def test_house(self):
        # test correct response
        response = handler.lambda_handler(make_input("GetHouseWords", {"house": "Stark"}), self.context)
        self._assert_normal(response)
        self.assertTrue(response["response"]["shouldEndSession"])
        self.assertEqual("Winter is Coming", get_speech_output(response))

        # test the card info
        self.assertEqual("Stark", response["response"]["card"]["title"])
        self.assertIn("Winter is Coming", response["response"]["card"]["content"])

        # test unknown house
        response = handler.lambda_handler(make_input("GetHouseWords", {"house": "Starrk"}), self.context)
        self._assert_normal(response)
        self.assertNotEqual("Winter is Coming", get_speech_output(response))

        # test missing house slot
        response = handler.lambda_handler(make_input("GetHouseWords", {}), self.context)
        self._assert_normal(response)
        self.assertNotEqual("Winter is Coming", get_speech_output(response))

    def test_character_info(self):
        # test correct response
        response = handler.lambda_handler(make_input("GetCharacterInfo", {"character": "Jon Snow"}), self.context)
        self._assert_normal(response)
        self.assertTrue(response["response"]["shouldEndSession"])
        self.assertIn("Stark", get_speech_output(response))

        # test the card info
        self.assertEqual("Jon Snow", response["response"]["card"]["title"])
        self.assertIn("Stark", response["response"]["card"]["content"])

        # test mangled name
        response = handler.lambda_handler(make_input("GetCharacterInfo", {"character": "John Snow"}), self.context)
        self._assert_normal(response)
        self.assertNotIn("Stark", get_speech_output(response))

        # missing slot
        response = handler.lambda_handler(make_input("GetCharacterInfo", {}), self.context)
        self._assert_normal(response)
        self.assertNotIn("Stark", get_speech_output(response))

    def test_character_missing(self):
        # test correct response
        response = handler.lambda_handler(make_input("GetCharacterInfo", {"character": "Robert Baratheon"}), self.context)
        self._assert_normal(response)
        self.assertTrue(response["response"]["shouldEndSession"])
        self.assertIn("don't know", get_speech_output(response))

    def test_actor_other_roles(self):
        # test correct response
        response = handler.lambda_handler(make_input("GetOtherRoles", {"actor": "Lena Headey"}), self.context)
        self._assert_normal(response)
        self.assertTrue(response["response"]["shouldEndSession"])
        self.assertIn("Dredd", get_speech_output(response))

        # test the card info
        self.assertEqual("Lena Headey", response["response"]["card"]["title"])
        self.assertIn("Dredd", response["response"]["card"]["content"])

    def test_get_actor(self):
        response = handler.lambda_handler(make_input("GetActor", {"character": "Tyrion Lannister"}), self.context)
        self._assert_normal(response)
        self.assertTrue(response["response"]["shouldEndSession"])
        self.assertIn("Peter", get_speech_output(response))

        # test the card info
        self.assertEqual("Tyrion Lannister", response["response"]["card"]["title"])
        self.assertIn("Peter", response["response"]["card"]["content"])

        # test a char with multiple actors
        response = handler.lambda_handler(make_input("GetActor", {"character": "Tommen"}), self.context)
        self._assert_normal(response)
        self.assertIn("Dean-Charles Chapman", get_speech_output(response))
        self.assertIn("Callum Wharry", get_speech_output(response))
