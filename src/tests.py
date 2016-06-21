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


def make_input(intent, slot_map):
    return {
        "session": {
            "new": False,
            "sessionId": "session1234",
            "attributes": {},
            "user": {
                "userId": None
            },
            "application": {
                "applicationId": "amzn1.echo-sdk-ams.app.[unique-value-here]"
            }
        },
        "version": "1.0",
        "request": {
            "intent": {
                "slots": {k: {"name": k, "value": v} for k, v in slot_map.items()},
                "name": intent
            },
            "type": "IntentRequest",
            "requestId": "request5678"
        }
    }


def get_speech_output(response):
    return response["response"]["outputSpeech"]["text"]

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

    def test_house(self):
        # test correct response
        response = handler.lambda_handler(make_input("GetHouseWords", {"house": "Stark"}), self.context)
        self._assert_normal(response)
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
        self.assertIn("don't know", get_speech_output(response))


    def test_actor_other_roles(self):
        # test correct response
        response = handler.lambda_handler(make_input("GetOtherRoles", {"actor": "Lena Headey"}), self.context)
        self._assert_normal(response)
        self.assertIn("Dredd", get_speech_output(response))

        # test the card info
        self.assertEqual("Lena Headey", response["response"]["card"]["title"])
        self.assertIn("Dredd", response["response"]["card"]["content"])

    def test_get_actor(self):
        response = handler.lambda_handler(make_input("GetActor", {"character": "Tyrion Lannister"}), self.context)
        self._assert_normal(response)
        self.assertIn("Peter", get_speech_output(response))

        # test the card info
        self.assertEqual("Tyrion Lannister", response["response"]["card"]["title"])
        self.assertIn("Peter", response["response"]["card"]["content"])

        # test a char with multiple actors
        response = handler.lambda_handler(make_input("GetActor", {"character": "Tommen"}), self.context)
        self._assert_normal(response)
        self.assertIn("Dean-Charles Chapman", get_speech_output(response))
        self.assertIn("Callum Wharry", get_speech_output(response))
