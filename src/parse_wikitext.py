""" Parse wikitext for information about a character/event/etc.
    Output to json file, designed to be read by elasticsearch.
"""

import argparse
import codecs
from collections import defaultdict
import json
import os
import re
import sys

def strip_junk(line):
    return line.strip().strip('\N{SOFT HYPHEN}')

class Article(object):
    NAME_RE = re.compile('title=([^&=]+)')

    def __init__(self, f):
        self.name = self._get_name(f)
        self.category = ''
        self.summary = ''
        self._extract_data(f)

    def _get_name(self, filename):
        """ Extract name from article name, e.g.
            index.php?title=Eddard_Stark&action=edit_extracted'
        """
        results = re.findall(self.NAME_RE, filename)
        if results:
            name = results[0].replace('_', ' ')
            return name
        else:
            return None

    def _read_file(self, f):
        with codecs.open(f, 'r', 'utf-8') as source:
            text = [line for line in source]
        return text

    def _extract_summary(self, text):
        summary = []
        reading_summary = False
        skipping_infobox = False

        for line in text:
            line = strip_junk(line)
            # skip blank lines
            if not line:
                continue

            # ignore redirects formatted with curly brackets
            if line.startswith('{{See'):
                continue
            # ignore infobox, which often appears before summary
            if line.startswith('{{') or line.startswith('{|'):
                skipping_infobox = True
                continue
            if line == '}}' or line == '|}':
                skipping_infobox = False
                continue
            # ignore pictures
            if line.startswith('[[File:'):
                continue
            # ignore redirect lines
            if line.startswith(':'):
                continue
            # ignore redirect articles
            if line.startswith('#REDIRECT'):
                print('Warning article appears to be a redirect:', line, file=sys.stderr)
                break

            # already reading a summary
            if reading_summary and not skipping_infobox:
                if line.startswith('=='):
                    # started a new section, so the summary is done
                    break
                else:
                    summary.append(line)
                    continue

            # we've found the start of the summary if not in an infobox
            if not skipping_infobox:
                reading_summary = True
                summary.append(line)
        return summary

    def _clean_line(self, line):
        """ Strip out wiki specific formatting.
        """
        # Remove double or trip apostrophes, used for formatting
        line = re.sub(r"''[']?", '', line)
        # Keep only the text portion of a wiki link (where the article name and in-text label differ)
        # example: [[Robb Stark|Robb]]   -->  Robb
        line = re.sub(r"\[\[" + r"[^\|\]]+" + r"\|" + r"([^\]]+)" + r"\]\]", r'\1', line)
        # remove the brackets used for a wiki link (which does not use a special label)
        # e.g. [[Jon Snow]]  -->  Jon Snow
        line = re.sub(r"[\[\]]+", "", line)
        # remove text references in curly braces
        # e.g. {{ref|aSoS|3}}
        line = re.sub(r"{{.+}}", "", line)
        return line

    def _extract_data(self, f):
        raw_text = self._read_file(f)
        summary = self._extract_summary(raw_text)
        clean_summary = [self._clean_line(line) for line in summary]
        self.summary = clean_summary


def setup_parser():
    """ Setup argument parser. """
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('wikitext_dir', help='directory containing wikitext files')
    parser.add_argument('output_f', help='output JSON file')
    return parser

def get_file_list(d):
    return [os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]

def extract_name(file_path):
    """ Extract article name from file path and clean it up.
    """
    article_name = os.path.split(file_path)[-1]
    # example: index.php?title=Arys_Oakheart&action=edit_extracted.txt
    article_name = re.sub("&.+", "", article_name)
    article_name = re.sub(r"index\.php\?title=", "", article_name)
    article_name = re.sub(r"_", " ", article_name)
    return article_name

def output_to_json(articles, f):
    with codecs.open(f, 'w', 'utf-8-sig') as output:
        json.dump(articles, output, indent=4, sort_keys=True)

def main():
    args = setup_parser().parse_args()
    raw_articles = get_file_list(args.wikitext_dir)
    articles = defaultdict(dict)
    for article in raw_articles:
        print('Parsing article:', article)
        article_name = extract_name(article)
        article_data = Article(article)
        articles[article_name] = {"character_name": article_name, "summary": article_data.summary}
        print()
    output_to_json(articles, args.output_f)

if __name__ == '__main__':
    main()
