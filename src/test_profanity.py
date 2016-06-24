from __future__ import unicode_literals

import unittest

import profanity


class TestProfanity(unittest.TestCase):
    def test_bastard_adjective(self):
        uncleaned = "Barra is the bastard daughter of Robert I"
        cleaned = "Barra is the baseborn daughter of Robert I"
        self.assertEquals(profanity.clean(uncleaned), cleaned)

    def test_bastard_adjective_2(self):
        uncleaned = "Garrett Flowers is a bastard son of Garth the Gross."
        cleaned = "Garrett Flowers is a baseborn son of Garth the Gross."
        self.assertEquals(profanity.clean(uncleaned), cleaned)

    def test_bastard_adjective_caps(self):
        uncleaned = "Ser Walder Rivers, also known as Bastard Walder,"
        cleaned = "Ser Walder Rivers, also known as baseborn Walder,"
        self.assertEquals(profanity.clean(uncleaned), cleaned)

    def test_bastard_noun(self):
        uncleaned = "Lord Walder Frey's bastards."
        cleaned = "Lord Walder Frey's baseborn children."
        self.assertEquals(profanity.clean(uncleaned), cleaned)

    def test_whore(self):
        uncleaned = "Zei is a whore in Mole's Town. She is good with a crossbow."
        cleaned = "Zei is a prostitute in Mole's Town. She is good with a crossbow."

    def test_whorehouse(self):
        uncleaned = "working at the whorehouse owned by her mother"
        cleaned = "working at the brothel owned by her mother"


if __name__ == '__main__':
    unittest.main()
