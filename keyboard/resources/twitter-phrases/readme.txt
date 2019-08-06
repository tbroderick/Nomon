Challenging Twitter Phrase Set
==================================================
http://www.keithv.com/data/twitter-phrases.zip

A data set consisting of sentences written on Twitter during 2016.  The goal was
to provide phrases that would be challenging to recognize while still being
memorable. It is comprised of two subsets:
 * In-vocabulary (IV) set - Phrases were all words were in a 100K vocab.
 * Out-of-vocabulary (OOV) set - Phrases were a single word was OOV.

Files:
==================================================
twitter-iv.txt  - 194 in-vocabulary phrases
twitter-oov.txt - 213 out-of-vocabulary phrases
watch-iv.txt    - Subset of twitter-iv.txt, 81 IV phrases used in [1]
watch-oov.txt   - Subset of twitter-oov.txt, 43 OOV phrases used in [1]

Procedure:
==================================================
We sourced our phrases from Twitter messages sampled during 2016.  We parsed
the tweets to find likely sentences based on capitalization and end-of-sentence
punctuation. We generated a banned word list of 1,706 obscene words
semi-automatically from a variety of sources. We removed sentences containing a
banned word. We removed sentences with fewer than 4 or more than 10 words. 

Using a word list of 100K English words [2], we created a set of 1.04M sentences
where all words were in-vocabulary.  We created a second set of 141K sentences
that had a single out-of-vocabulary (OOV) word.

We fielded a random subset of 850 of these sentences to 3-5 Amazon Mechanical
Turk workers.  We only kept sentences that the majority of workers rated as easy
to understand, judged as having no spelling errors, and that workers could type
from memory with no errors (ignoring case and punctuation).  These were further
manually reviewed by one of the authors to remove any remaining offensive
sentences. The final phrase set had 213 OOV phrases and 194 in-vocabulary
phrases.

The watch sets used in [1] were further limited to six of fewer words, phrases
containing acronyms were removed, phrases were converted to lowercase, and any
end-of-sentence punctuation was removed.

For full details, see our CHI 2019 paper:

[1] Keith Vertanen, Dylan Gaines, Crystal Fletcher, Alex M. Stanage, Robbie
Watling, and Per Ola Kristensson. 2019. VelociWatch: Designing and Evaluating a
Virtual Keyboard for the Input of Challenging Text. In Proceedings of the 2019
CHI Conference on Human Factors in Computing Systems (CHI '19). ACM, New York,
NY, USA, to appear.

[2] http://keithv.com/data/vocab_100k.txt
