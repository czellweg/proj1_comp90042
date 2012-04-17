'''
Activity Log: compressed term index
===================================

------------------------------------------------------------------------------

04 April 2012
-------------

12.05 - 13.00: reading in chapter 4 and 5 of the IR book, take notes of
important concepts
  	
  	* list of resources:
	
	Basic presentation about inverted indices and compression methods
	http://www.ir.iit.edu/~dagr/cs529/files/handouts/02aCompression-2per.PDF
	
	The widely known IR online book
	eBook: Introduction to Information Retrieval, Manning et al., chapter 4, 5
	
	
	PhD thesis by Roi Blanco Gonzales Index Compression for Information Retrieval
	Systems
	www.dc.fi.udc.es/~roi/publications/rblanco-phd.pdf
	
	Well-explained compression methods (Gamma, Golomb, Huffmann)
	http://www.ir.uwaterloo.ca/slides/buettcher_index_compression.pdf
	
	Explanations regarding inverted files/indices
	http://orion.lcg.ufrj.br/Dr.Dobbs/books/book5/chap03.htm
	
	Gamma-Codes well explained:
	http://www.cs.clemson.edu/~juan/CPSC862/Concept-50/IR-Compression.pdf



------------------------------------------------------------------------------

11 April, 2012
--------------

10.40 - 11.00: make a ToDo list, ordered by priority

11.00 - 12.00: skim through the resources (see above) and take note of
important concepts, find a simple algorithm to implement
	
	* chapter 5 (IRBook) talks about variable byte (VB) codes (docID gap
	compression)
	
	* word size of 1 byte seems to be a good compromise between compression ratio
	and speed of decompression (page 98)
	
	* as a first go, I'll implement a VB-algorithm as outlined with pseudo-code on
	page 97
	
	* I'll test my implementation with handmade postings-list & the postings list
	format will be a simple docId-index, e.g. 
	term1 -> 1,4,6,7,9,34,124, 
	term2 -> 34,456,67,78,90,1234,3456
	
	* the data-structure I want to use is: (term1, [1,4,6,7,9,34,124])


12.00 - 13.00: search for & examine off-the-shelf implementations of IF
compression algorithms
	
	* also checked out Lucene/PyLucene: to test my algorithm, I can maybe create
	an index (e.g. over the NLTK reuters corpus) and retrieve the postings list
	for a given term
	
	* read some tutorials on http://www.lucenetutorial.com/ on how to use Lucene
	and how to create an index from documents in a directory
	
	* as it turns out, Lucene uses the VB compression algorithm described in chapt
	5 too, see http://lucene.apache.org/core/old_versioned_docs/versions/3_5_0/fil
	eformats.html#VInt
	
	* the Lucene index tool 'Luke' was of help to find out what Lucene actually
	saves in the index
	
	* this brought me to the idea that I can simply use an IndexReader to get the
	necessary information that Luke displays

	* also looked at Whoosh, a pure Python indexing and search library -> decided
	to go with Lucene first and see how far I get, if Lucene doesn't turn out to
	be a good choice, I try out Whoosh


13.00 - 14.15: implementing simple Java Lucene index based on NLTKs Reuters
corpora and output a postings list
	
	* I want to extract an inverted index from this so that I can test my VB
	compression algorithm
	
	* implementation outputs: "term1 -> [docid_1, docid_2, docid_3,..., docId_n]"
	
	* this can be used as index to test my compression algorithm


------------------------------------------------------------------------------

12 April, 2012
--------------

10.30 - 13.00: since yesterday's attempts at creating the index were
successful, I want to build the same class but using PyLucene this time
	
	* downloading and compiling JCC to be able to install PyLucene
	
	* compiling PyLucene worked well, and part of the installation was smooth as
	well. However, had to recompile multiple times to get the correct combination
	of arguments
	
	* seeing that I've lost quite some time on this already, I'm just using the
	Java-code generated output for my simple inverted index without re-
	implementing the whole thing in python again - if there is still some time
	left at the end, I'll implement it


13.00 - 14.00: tried to get 'git push' to work but something seems to be wrong
with my SSH keys
	
	* when I run: ssh -T git@github.com -> it works fine, authentication
	successful
	
	* however, if I run 'git remote add origin
	czellweg@github.com:czellweg/proj1_comp90042.git' I get a 'Permission denied
	(publickey)' error
	
	* okay, stupid me: use user 'git' instead of 'czellweg' -> 'git remote add
	origin git@github.com:czellweg/proj1_comp90042.git' - copy-paste
	 without thinking is sometimes the way forward ;-)

14.00 - 18.00: implementing VB-algorithm as outlined with pseudo-code in IRBook
on page 97
	
	* at first, I didn't realize that the VBEncodeNumber should output binary
	representations
	
	* now finding the best way to represent a number as binary sequence, looked at
	bytearrays, need further investigation. Seems to be an easy enough problem but
	couldn't find a quick solution so far
	
	* since Python 2.6, there is a bin() function which converts a number into
	it's binary representation. I have introduced this into the code but there is
	some more padding, stripping etc. involved to get the desired result. Will
	finish implementing the algorithm and see how the performance is under load. I
	would assume that there could be significant overhead.
	
	* looked at & understand gamma codes. I'd like to implement them as well and
	compare and contrast those two methods.

------------------------------------------------------------------------------

13 April, 2012
--------------

11.00 - 13.00: testing the performance of the VB compression compared to a non-
compressed index.
    
    * to do so, I will implement 2 methods to calculate how many bytes are used
    by only the postings list entries, leaving out all the terms since they're
    not compressed.
    
    * the term itself is not compressed (or encoded) in my inverted file. To
    remove unnecessary characters (and thus minimizing the size of the inverted
    file), my new format of the output file from lucene-test is:
    term1[docId1, docId2, ..., docIdn] (I've removed the '->')
    
    * my inverted file contains 16'448 terms and their postings list
    
    * as a first test, I'm just compressing the plain docIds and I'm not
    calculating the gaps.

14.00 - 15.00: first tests have shown that the compressed index is bigger than
the uncompressed one. Looking for the bug now.

    * turns out I had a small mistake in calculating the the number of bytes
    for the compressed index (binary sequence).
    
    * while finding the bug, I came to the realisation that it's not really
    possible (or I don't know Python well enough maybe) to physically compress
    the numbers, i.e. real bitwise manipulations of any given byte. The reason
    for this is discussed at length in the indexcompression.py module itself.
    
'''