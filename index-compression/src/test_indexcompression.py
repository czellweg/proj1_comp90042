# Christof Zellweger
# 502193
# 2012-04-21

'''
This module is for testing only and therefore has the indexcompression module
as a dependency.

No explanatory comments or discussion is included here, please find those in
the indexcompression module. Here we only test for correct functionality and to
test the performance of the indexcompression module.
'''
from itertools import chain
import indexcompression as ic
import platform
import time

def calculate_int_bytes_of_IF(IFfilename):
    '''
    Calculates how many bytes are needed for just storing the numbers in the
    postings list of the inverted index, based on the architecture of the
    system.
    
    Expects the inverted index to be in the format: 
    term[docId1, docId2,..., docIdn], an example would be 'term[1,3,4,5,7,9]'
    
    I've left out docstring tests as it depends on the machine the tests are
    run from, as it's either 32bit or 64bit.
    '''
    lines = open(IFfilename).readlines()
    flattened_list = flatten(get_postings_list_ints(lines))
    
    arch_xbit = int(platform.architecture()[0].split('bit')[0])
    return len(flattened_list) * arch_xbit / 8;


def flatten(listoflists):
    '''
    Flattens the list of lists.
    
    >>> flatten([[1, 2, 3], [4, 5, 6]])
    [1, 2, 3, 4, 5, 6]
    >>> flatten([[],[1], [1,2], [1,2,3]])
    [1, 1, 2, 1, 2, 3]
    '''
    return list(chain.from_iterable(listoflists))


def get_postings_list_ints(lines):
    '''
    Gets a list of lists of ints that represent the postings for the terms.
    
    >>> get_postings_list_ints(['whats[1,2,3]','whatever[4,5,6]'])
    [[1, 2, 3], [4, 5, 6]]
    >>> get_postings_list_ints(['whats[1]','whatever[2]'])
    [[1], [2]]
    '''
    
    l = [list(line.split('[')[1].split(']')[0].split(',')) for line in lines]
    int_list_list = [map(int, subl) for subl in l]
    return int_list_list


def test_gamma_compression_plain_docids(IFfilename):
    '''
    Tests the performance of Gamma codes using plain docIds.
    '''
    int_bytes = calculate_int_bytes_of_IF(IFfilename)
    all_postings_docids = flatten(get_postings_list_ints(open(IFfilename).readlines()))
    
    t = time.time()
    bitstream = ic.gamma_encode(all_postings_docids)
    t2 = time.time() - t
    nr_of_bytes = len(bitstream) / 8
    
    
    t = time.time()
    ic.gamma_decode(bitstream)
    t3 = time.time() - t

    print 'Gamma-encoding: using plain doc ids'
    print '----------------------------------'
    print 'Uncompressed (bytes): ' + str(int_bytes)
    print 'Compressed (bytes): ' + str(nr_of_bytes)
    print 'Compression factor: ' + str(float(int_bytes) / float(nr_of_bytes))
    print 'Length of bitstream: ' + str(len(bitstream))
    print 'Time to compress (s): ' + str(t2)
    print 'Time to decompress (s): ' + str(t3)
    print '==================================='


def test_VB_compression_plain_docids(IFfilename):
    '''
    Tests the performance of VB codes using plain docIds.
    '''
    int_bytes = calculate_int_bytes_of_IF(IFfilename)
    
    all_postings_docids = flatten(get_postings_list_ints(open(IFfilename).readlines()))
    t = time.time()
    bytelists = ic.vb_encode(all_postings_docids)
    t2 = time.time() - t
    flattened = flatten(bytelists)
    
    # since every entry in the flattened list is 8 bits long, the number of
    # used bytes is exactly the length of the flattened list
    compressed_bytes = len(flattened)
    t = time.time()
    ic.vb_decode(bytelists)
    t3 = time.time() - t
    print 'VB-encdoing: using plain doc ids'
    print '-------------------------------'
    print '# of IDs to compress: ' + str(len(all_postings_docids))
    print 'Uncompressed (bytes): ' + str(int_bytes)
    print 'Compressed (bytes): ' + str(compressed_bytes)
    print 'Compression factor: ' + str(float(int_bytes) / float(compressed_bytes))
    print 'Time to compress (s): ' + str(t2)
    print 'Time to decompress (s): ' + str(t3)
    print '==================================='
    
    
def test_VB_compression_gaps_docids(IFfilename):
    '''
    Tests the performance of VB codes using gaps.
    '''
    int_bytes = calculate_int_bytes_of_IF(IFfilename)
    lines = open(IFfilename).readlines()
    int_lists = get_postings_list_ints(lines)
    gap_lists = get_gaps_from_int_lists(int_lists)
    
    all_postings_gapids = flatten(gap_lists)
    
    t = time.time()
    bytelists = ic.vb_encode(all_postings_gapids)
    t2 = time.time() - t
    
    flattened = flatten(bytelists)
    
    
    compressed_bytes = len(flattened)
    t = time.time()
    ic.vb_decode(bytelists)
    t3 = time.time() - t

    print 'VB-encoding: using gaps instead of plain doc ids'
    print '-----------------------------------------------'
    print '# of IDs to compress: ' + str(len(all_postings_gapids))
    print 'Uncompressed (bytes): ' + str(int_bytes)
    print 'Compressed (bytes): ' + str(compressed_bytes)
    print 'Compression factor: ' + str(float(int_bytes) / float(compressed_bytes))
    print 'Time to compress (s): ' + str(t2)
    print 'Time to decompress (s): ' + str(t3)
    print '==================================='

def test_gamma_compression_gaps_docids(IFfilename):
    '''
    Tests the performance of Gamma codes using gaps.
    '''
    int_bytes = calculate_int_bytes_of_IF(IFfilename)
    
    
    lines = open(IFfilename).readlines()
    int_lists = get_postings_list_ints(lines)
    gap_lists = get_gaps_from_int_lists(int_lists)
    
    all_postings_gapids = flatten(gap_lists)
    
    t = time.time()
    bitstream = ic.gamma_encode(all_postings_gapids)
    t2 = time.time() - t
    
    nr_of_bytes = len(bitstream) / 8
    t = time.time()
    ic.gamma_decode(bitstream)
    t3 = time.time() - t

    print 'Gamma-encoding: using gaps instead of plain doc ids'
    print '-----------------------------------------------'
    print 'Uncompressed (bytes): ' + str(int_bytes)
    print 'Compressed (bytes): ' + str(nr_of_bytes)
    print 'Compression factor: ' + str(float(int_bytes) / float(nr_of_bytes))
    print 'Length of bitstream: ' + str(len(bitstream))
    print 'Time to compress (s): ' + str(t2)
    print 'Time to decompress (s): ' + str(t3)
    print '==================================='

def get_gaps_from_int_lists(docids_list):
    '''
    Returns a list of lists of gaps, given a list of plain docIds
    
    >>> get_gaps_from_int_lists([[1,2,3,4], [13,20,27,30]])
    [[1, 1, 1, 1], [13, 7, 7, 3]]
    '''
    
    gaplists = map(calculate_gaps, docids_list)
    return gaplists

def calculate_gaps(docids):
    '''
    Given a list of docIds, this method returns the list of gaps leaving the
    first entry unchanged.
    
    >>> calculate_gaps([1,2,3,4])
    [1, 1, 1, 1]
    >>> calculate_gaps([13,20,27,30])
    [13, 7, 7, 3]
    >>> calculate_gaps([13])
    [13]
    '''
    # since the 
    gaplist = [y - x for x,y in zip(docids,docids[1:])]
    # keep the first entry in the list and leave it unchanged
    gaplist.insert(0, docids[0])
    return gaplist

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
#    test variable-byte encoding
    test_VB_compression_plain_docids("postings-list.txt")
    test_VB_compression_gaps_docids("postings-list.txt")
    
#    test gamma encodings
    test_gamma_compression_plain_docids("postings-list.txt")
    test_gamma_compression_gaps_docids("postings-list.txt")