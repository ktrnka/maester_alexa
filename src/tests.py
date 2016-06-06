from __future__ import unicode_literals
from __future__ import print_function
import sys
import argparse
import unittest
import handler

from build_imdb import get_aliases


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

        # test mangled name
        response = handler.lambda_handler(make_input("GetCharacterInfo", {"character": "John Snow"}), self.context)
        self._assert_normal(response)
        self.assertNotIn("Stark", get_speech_output(response))

        # missing slot
        response = handler.lambda_handler(make_input("GetCharacterInfo", {}), self.context)
        self._assert_normal(response)
        self.assertNotIn("Stark", get_speech_output(response))

    def test_actor_other_roles(self):
        # test correct response
        response = handler.lambda_handler(make_input("GetOtherRoles", {"actor": "Peter Dinklage"}), self.context)
        self._assert_normal(response)
        self.assertIn("X-Men", get_speech_output(response))

    def test_get_actor(self):
        response = handler.lambda_handler(make_input("GetActor", {"character": "Tyrion Lannister"}), self.context)
        self._assert_normal(response)
        self.assertIn("Peter", get_speech_output(response))
