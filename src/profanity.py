""" Clean profanity to make sure we fit into the family friendly Alexa environment.
"""

from __future__ import unicode_literals

import re


PROFANITY_REGEXES = {
    # legitimized bastard as a noun
    r"(legitimi[sz]ed) bastard": r"\1 baseborn child",
    # bastard as a noun
    r"bastards\.": r"baseborn children.",
    r"bastard\.": r"baseborn child.",
    # bastard as an adjective
    r"bastard ([A-Za-z]+)": r"baseborn \1",
    # whore
    "whore": "prostitute",
    "whores": "prostitutes",
    # whorehouse
    "whorehouse": "brothel",
    # bitch
    "bitch": "female dog",
    }


def clean(text):
    cleaned_text = text
    for pattern, replacement in PROFANITY_REGEXES.items():
        cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE)
    return cleaned_text
