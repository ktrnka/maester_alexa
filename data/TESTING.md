Most important characters for testing/curation
================
Taken from top roles on IMDB:

* Tyrion Lannister
* Cersei Lannister
* Daenerys Targaryen
* Jon Snow
* Sansa Stark
* Arya Stark
* Jaime Lannnister
* Jorah Mormont
* Theon Greyjoy
* Samwell Tarly
* Lord Varys
* Petyr Baelish/Littlefinger Should test both names
* Brienne of Tarth
* Bronn
* Grand Maester Pycelle
* Bran Stark
* Sandor Clegane/The Hound Should test both names
* Davos Seaworth

Note that the lookup will behave differently for who-plays-X vs tell-me-about-X because the X in the former is the IMDB
name and the latter uses the wiki name.

Testing for version 1
-----

* Tyrion Lannister -> links to many of the other top 10. Good summ.
* Tyrion -> ASR failure
* Cersei Lannister -> links to Robert, etc. Joffery, Mrycella, Tommen
* Cersei -> ASR failure
* Daenerys Targaryen -> links to Viserys 
* Daenerys -> didn't understand the question
* Jon Snow -> Eddard Stark, Ghost
* Sansa Stark -> if I say "about Sansa Stark" the ASR fails. If I'm more explicit it succeeds.
* Arya Stark -> Eddard Stark, Catelyn Tully, all other siblings
* Jaime Lannnister -> Tywin/Joanna. BAD HTML
* Jorah Mormont -> "Westeros" 
* Theon Greyjoy -> Balon Greyjoy BAD HTML
* Samwell Tarly NO DESCRIPTION
* Lord Varys NO DESCRIPTION
* Petyr Baelish/Littlefinger Petyr Baelish works. Little finger doesn't work
* Brienne of Tarth NO DESCRIPTION
* Bronn NO DESCRIPTION
* Grand Maester Pycelle MISSING
* Bran Stark HTML
* Sandor Clegane/The Hound Sandor success but the hound fails
* Davos Seaworth 