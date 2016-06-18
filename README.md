Game of Thrones trivia skill for Alexa Skills Kit.

Code notes
==========

* Python dependencies are split into two requirements.txt files - one for scripts we run on our machines and the other for requirements on Lambda.
* src/private.py has stuff like the Elasticsearch credentials and isn't in version control

Architecture notes
==================

* Factoid data mostly lives in Elastic Search and we query that for lookup but I'm trying to avoid too many round-trips to ES per lambda call if possible.
For example, before Elastic Search everything was just Python dicts with exact-match lookup.
To give someone an example I'd generate something like "Try asking, who is %s" where %s was randomly sampled from the dict
so that they'd get a sense of coverage. But to do the same thing in Elastic Search with the way the code was structured I'd
need a second round-trip when the query actually succeeds so that needs refactoring to keep the num round trips down.
* Want to separate out the pieces different people might work on, so maybe one place for all the crap dealing with Elastic
Search index/type/field (read: database/table/column) names. I'd like to pull out all natural language generation and
strings at some point but I'm not sure how complex it'll actually get.