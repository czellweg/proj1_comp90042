# Christof Zellweger
# 502193
# 2012-04-04

'''
Introduction
------------

I've chosen to implement two index compression algorithms and compare and
contrast them. This docstring contains the discussion of my findings. First, I
will explain both algorithms and then present my measurements and comparisons.

The two chosen compression algorithm are variable-byte encoding (VB-encoding)
and Elias Gamma encoding (henceforth only called gamma-codes or gamma-
encoding). VB-encoding, as the name suggest, works on the byte-level (smallest
unit is 1 byte) whereas Gamma-codes work on the bit-level. Please refer to the
sections below for more information on both algorithms.

Both methods have been implemented using binary string / list representations
of the encoded numbers, no bit-shift operations have been used. Therefore, both
algorithms don't offer physical compression as storing and handling binary
string / list representations is more space-intense than working on bit-shift
level. The reason for this decision was simple: I wanted to learn about the two
algorithms, how they work and how they perform when compared to each other and
under different scenarios. Implementing them using bit-shift operations would
have been interesting as well but also slightly more cumbersome without
revealing much benefit, i.e. I wouldn't have learned anything about the
algorithms themselves, it would have been a very technical task.


Variable Byte encoding (VB-encoding)
------------------------------------

VB-encoding works on the byte-level. To encode a given number, the necessary
number of bytes are determined first and 7 out of the 8 bits are available for
number-encoding with the highest-order bit (also called the continuation bit)
specifying whether the current byte is the final byte (0=not final byte,
1=final byte) for not. Depending on the implementation, the continuation bit
values (0 or 1) might be vice versa as described above.

As a simple example, suppose we want to VB-encode the decimal number 10.
Decimal 10 is binary 00001010. Since we only need 4 bits, we can encode decimal
10 using 1 byte. This means that the used byte is also the 'last' byte so the
continuation bit has to be set to 1. Therefore, decimal 10 VB-encdoded is
10001010.

Lets also encode a number which needs multiple bytes to be represented, so we
encode decimal 824 which is binary 00000011 00111000. We need 2 bytes to do so,
so the highest-order byte is not the final byte and therefore has its highest-
order bit set to 0. However, the lowest-order byte (second byte) marks the
final byte and therefore has its highest-order bit set to 1. If we combine them
all, we get 00000110 for the highest-order byte and 10111000 for the second
byte which results in a VB-code of 00000110 10111000. Remember that the
highest-order bit in each byte is disregarded when decompressing to get back
the original decimal number, that is also why there is an 'additional' 0 as the
lowest-order bit in the highest-order byte when encoding decimal 824.

Compared to gamma-codes (see next section), VB-codes are wasteful if only very
small number are encoded since the bits in a byte not needed cannot be used
otherwise. VB-encoding is used in the MIDI file format and is also the default
compression method in Apache Lucene (see http://lucene.apache.org/core/old_vers
ioned_docs/versions/3_5_0/fileformats.html#VInt). See also
http://en.wikipedia.org/wiki /Variable-length_quantity.

 
Elias Gamma encoding:
--------------------

Other than VB-codes, Gamma-codes are at home on the bit-level, i.e. they are a
bit less wasteful but also need more CPU power for decompression. There are no
delimiters like the continuation bit in VB-codes but rather the encoded form of
a number is divided in 2 parts: a length and an offset part. The length part is
the unary code defining the number of bits of the offset and a 0 appended so
that we know while decompressing when the length-part for a number has been
completely read. The offset is the encoded number with the highest-order bit
(which is obviously always 1) removed. When decoding, we simply read the
length-part after which we know the number of bits to read and set the appended
0 after the offset to 1.

Again, an example helps understand the above explanation. Suppose we want to
encode decimal 10 which is binary 1010. The corresponding gamma-code is
1110010. We have the leading three 1's and the appended 0. The three 1's define
the length of the offset. We then simply switch the 0 that follows the three
1's to 1 and read 3 more bits, therefore we get back again binary 1010 which is
decimal 10.

But why is it that this scheme works well and what's the mathematical
background for it? Suppose we have a number G (or in the case of an index a gap
which is the difference between two doc-ids) we want to encode. What is the
lower bound (=optimal) number of bits per encoded gap in a binary format?
Obviously this is log_2(G). Suppose that 1<=G<=2^n and the number of gaps is
2^n. In other words, to get an optimal bit-wise encoding, at least n bits are
needed to do so since the largest gap value (by 'gap value' I mean the actual
numerical value of the gap, e.g. a gap with value 4 results from 2 docIds 412
and 416 for example) can be 2^n. As an example, take n=4. Then the largest gap
value which can occur is 2^4 = 16 and log_2(16) = 4, so 4 bits are at least
needed to encode all gaps between size 0 and 16. Although there are certainly
cases where such a gap (i.e. gap value 16 in case of n=4 bits) does not occur
in a postings list, if we assume that the gap values are all equally
distributed, they are likely to occur and we must account for them.

However, since we only have a stream of bits, we need to know where the one
number ends and the next begins. Gamma- codes handles this issue with its
length and offset part as this results in a prefix-free number scheme, i.e. no
gamma-code is the prefix of another gamma-code. Therefore, when gamma-codes are
used, we need log_2(G)+1 bits for the length part and the offset needs
log_2(G), therefore we need 2xlog_2(G)+1 bits overall. Compared to the optimal
number of bits of log_2(G), 2xlog_2(G)+1 grows only by a constant factor.

This justification is true if we assume that the gaps (numbers to encode) are
all equiprobable, i.e. they are uniformly distributed. This doesn't have to be
the case in a real-world setting thought. The good news is that it doesn't
matter what distribution the gaps have as it can mathematically be shown (using
entropy, see IR-book chapter 5) that the needed bits for encoding are within a
factor of approximately 2 of the theoretically optimal number of bits. Again,
this is pretty good as with larger number, the needed number of bits grows only
by a constant factor.


Discussion of results
---------------------

To discuss my results, I ran the test_indexcompression module on a Mac OSX,
dual core 2.53GHz and 8GB ram. The postings input file has been generated using
the Java program PostingsFileGenerator in the project 'lucene-test' and is an
index over the Reuters corpus as provided by NLTK. Following are the results
this discussion is based on (these can be had by running the
test_indexcompression module):

VB-encdoing: using plain doc ids
-------------------------------
# of IDs to compress: 191715
Uncompressed (bytes): 1533720
Compressed (bytes): 373565
Compression factor: 4.10563088084
Time to compress (s): 1.45905399323
Time to decompress (s): 0.463293075562
===================================
VB-encoding: using gaps instead of plain doc ids
-----------------------------------------------
# of IDs to compress: 191715
Uncompressed (bytes): 1533720
Compressed (bytes): 242794
Compression factor: 6.31696005667
Time to compress (s): 1.13764190674
Time to decompress (s): 0.385030984879
===================================
Gamma-encoding: using plain doc ids
----------------------------------
Uncompressed (bytes): 1533720
Compressed (bytes): 481092
Compression factor: 3.18799730613
Length of bitstream: 3848743
Time to compress (s): 0.468030929565
Time to decompress (s): 4.56869387627
===================================
Gamma-encoding: using gaps instead of plain doc ids
-----------------------------------------------
Uncompressed (bytes): 1533720
Compressed (bytes): 237196
Compression factor: 6.4660449586
Length of bitstream: 1897569
Time to compress (s): 0.409807920456
Time to decompress (s): 2.48318386078
===================================


I tested different performance metrics, namely compression factor, time to
compress and time to decompress on both the postings-list based on plain docIds
and the postings- list based on gaps. I would expect the compression factor to
be significantly higher in both algorithms when only gaps are used as the
numbers to be encoded are generally smaller.

I will first analyse both algorithms on their own and then compare and contrast
them.

When encoding/decoding ~192'000 numbers, VB-codes achieve a compression factor
of ~4.1 when plain docIds are used and compression takes ~3.1 times longer than
decompression. If the list of docIds has been preprocessed so that only the
gaps are encoded, further increase in compression of 53% is possible compared
to a compression using only plain docIds which equals a compression factor of
~6.1 compared to the uncompressed docIds list. In the case of gaps, compression
is slightly faster compared to decompression and takes about ~2.95 times
longer.

Gamma-codes using plain docIds achieve a compression factor of ~3.1 and
compression is about ~9.7 times faster than decompression. Using gaps instead
of plain docIds, the compression factor was ~6.5 and compression was ~6.1 times
faster than decompression.

As expected, both algorithms perform significantly better if a list of gaps is
used instead of the plain docIds. That was the whole point really of those two
algorithms: encode small numbers using a minimum number of bits or bytes and
therefore achieve a certain level of compression. The results for the
compression factors when using plain docIds and gaps support the fact that
Gamma codes perform exceptionally well with very small numbers whereas VB-codes
are a better choice when larger numbers have to be encoded. VB-codes have a
better compression factor when plain docIds are used but Gamma codes win when
gaps are used. The times to compress and decompress are reciprocal for the 2
algorithms: VB-codes generally take longer to compress and Gamma-codes are
slower when it comes to decompression. This is another expected result: while
decoding, VB-codes works on a byte level and doesn't have to process every
single bit whereas with Gamma codes, encoding is straight forward and involves
only a 'concatenation' of two parts. However, decoding a Gamma bit-sequence
involves reading every single bit and frequently switch 0's to 1's, i.e. it is
more CPU intense.

Which method to chose? This really depends on the environment and what the
focus is (maximum compression? fast encoding/decoding? etc). The ratio
regarding encoding/decoding times (~2.95 - ~3.1) using VB-codes is smaller than
the corresponding ratio using Gamma-codes (~6.1 - ~9.7) so this method might be
chosen over Gamma codes if a lot of encoding and decoding is to be expected.
However, if a high compression factor is the number one priority, Gamma codes
might outperform VB-codes. In general, compression methods on a byte level are
usually a good compromise between compression factors and speed of
encoding/decoding (see also chapter 5 in IRbook).

There are two implementations of the gamma-decode function. This is due to the
fact that while I was testing, I realized that the recursive approach did not
perform well and decoding a single number took about 0.5s - 0.8s. This was
obviously unacceptable so I've later implemented an iterative solution which
performs orders of magnitudes faster.

Timing the encoding/decoding is to be taken with a pinch of salt: the fact that
I'm working with strings instead of bit-shift operations and that I need to
cast back and forth from/to integers takes a toll on the overall performance.
However, I believe the measured times (their magnitudes in relation to each
other) are indicative to what could be expected had I used real compression
using bit-shifts. Of course, I would have to implement these bit-shift
compressions to proof this claim, however I didn't have enough time to do so.
Furthermore, I'm convinced that a seasoned Python programmer could improved the
performance of both implementations further simply by knowing the nifty tricks
of how to write fast code in this particular language. Since I'm relatively new
to Python, optimization was not my focus but rather easy-to-understand code.

Also keep in mind that these are only two possible algorithms for index
compression, others are for example Golomb codes, codes using Huffman or
Fibonacci encoding or Rice codes. All of them have their own weaknesses and
strengths. It would have been interesting to check these out as well but given
the time frame, implementing these as well was feasible.

'''


def gamma_encode(numbers):
    '''
    Encodes the list of numbers using gamma-codes.
    
    >>> gamma_encode([1])
    '0'
    >>> gamma_encode([9])
    '1110001'
    >>> gamma_encode([1025, 511])
    '11111111110000000000111111111011111111'
    >>> gamma_decode(gamma_encode([1025, 511]))
    [1025, 511]
    
    
    '''
    result = []
    for num in numbers:
        result.append(gamma_encode_number(num))
    bitstring = ''.join([res for res in result])
    return bitstring

def gamma_decode2(bitstring, result_list):
    '''
    Decodes a gamma-encoded bitstring using a recursive approach.
    
    >>> gamma_decode2('0', [])
    [1]
    >>> gamma_decode2('100', [])
    [2]
    >>> gamma_decode2('101', [])
    [3]
    >>> gamma_decode2('11000', [])
    [4]
    >>> gamma_decode2('1110001', [])
    [9]
    >>> gamma_decode2('1110101', [])
    [13]
    >>> gamma_decode2('111101000', [])
    [24]
    >>> gamma_decode2('11111111011111111', [])
    [511]
    >>> gamma_decode2('111111111100000000001', [])
    [1025]
    >>> gamma_decode2('11111111110000000000111111111011111111', [])
    [1025, 511]
    >>> gamma_decode2('101110001110001', [])
    [3, 4, 9]
    '''
    if len(bitstring) == 1:
        return [1]

    bitstring = map(int, bitstring)
#    find the first zero after consecutive (unary 1s
    zero_index = bitstring.index(0)
    
    bitstring[zero_index] = 1
    
    binary_num = bitstring[zero_index: 2 * zero_index + 1]
    str_rep = ''.join([`num` for num in binary_num])
    result_list.append(int(str_rep, 2))
    
    if (2 * zero_index + 1) == len(bitstring):
#        we're done with the full stream
        return result_list
#    we still have more numbers to decode - do the same thing again with rest
#    of list
    return gamma_decode2(bitstring[2 * zero_index + 1:], result_list)


def gamma_decode(bitstring):
    '''
    
    
    >>> gamma_decode('101110001110001')
    [3, 4, 9]
    >>> gamma_decode('11111111110000000000111111111011111111')
    [1025, 511]
    >>> gamma_decode('0')
    [1]
    >>> gamma_decode('100')
    [2]
    >>> gamma_decode('101')
    [3]
    >>> gamma_decode('11000')
    [4]
    >>> gamma_decode('1110001')
    [9]
    >>> gamma_decode('1110101')
    [13]
    >>> gamma_decode('111101000')
    [24]
    >>> gamma_decode('11111111011111111')
    [511]
    >>> gamma_decode('111111111100000000001')
    [1025]
    >>> gamma_decode('11111111110000000000111111111011111111')
    [1025, 511]
    >>> gamma_decode('101110001110001')
    [3, 4, 9]
    '''


    if len(bitstring) == 1:
        return [1]
    bitlist = map(int, bitstring)
    index = 0
    result_list = []
    while (index != len(bitlist) - 1):
        length = 0
        while(bitlist[index] == 1):
            length += 1
            index += 1
        
        bitlist[index] = 1
        binary_num = bitlist[index:(index + length+1)]
        str_rep = ''.join([`num` for num in binary_num])
        result_list.append(int(str_rep, 2))
        index += length+1
        
        if index > (len(bitlist) - 1):
            break
    return result_list

def unary_code(length):
    '''
    >>> unary_code(0)
    '0'
    >>> unary_code(1)
    '10'
    >>> unary_code(4)
    '11110'
    >>> unary_code(9)
    '1111111110'
    '''
    
    return '1' * length + '0'


def gamma_encode_number(number):
    '''
    >>> gamma_encode_number(1)
    '0'
    >>> gamma_encode_number(2)
    '100'
    >>> gamma_encode_number(3)
    '101'
    >>> gamma_encode_number(4)
    '11000'
    >>> gamma_encode_number(9)
    '1110001'
    >>> gamma_encode_number(10)
    '1110010'
    >>> gamma_encode_number(13)
    '1110101'
    >>> gamma_encode_number(24)
    '111101000'
    >>> gamma_encode_number(511)
    '11111111011111111'
    >>> gamma_encode_number(1025)
    '111111111100000000001'
    '''
    
    if number == 1:
        return '0'
    
    offset = str(bin(number).lstrip('0b'))
    offset = offset[:0] + offset[1:]
    return unary_code(len(offset)) + offset


def vb_encode(numbers):
    '''
    >>> vb_encode([824, 5, 214577])
    [['00000110', '10111000'], ['10000101'], ['00001101', '00001100', '10110001']]
    >>> vb_encode([1])
    [['10000001']]
    '''
    bytestream = []
    [bytestream.append(vb_encode_number(n)) for n in numbers]
    return bytestream


def vb_decode(bytestream):
    '''
    >>> vb_decode([['00000110', '10111000'], ['10000101'], ['00001101', '00001100', '10110001']])
    [824, 5, 214577]
    '''
    numbers = []
    n = 0
    # make sure we traverse the list in order
    for i in range(0, len(bytestream)):
        byte_list = bytestream[i]
        for j in range(0, len(byte_list)):
            bite = byte_list[j]
            intval = int(bite, 2)
            if intval < 128:
                n = 128 * n + intval
            else:
                n = 128 * n + (intval - 128)
                numbers.append(n)
                n = 0
    return numbers

def vb_encode_number(n):
    '''
    >>> vb_encode_number(10)
    ['10001010']
    
    '''
    byteslist = []
    while(True):
        res = n % 128
        byteslist.insert(0, str(bin(res).lstrip('0b')).zfill(8))
        if n < 128:
            break
        n = n / 128
    num = int(byteslist[len(byteslist)-1], 2)
    num += 128
    byteslist[len(byteslist)-1] = str(bin(num).lstrip('0b')).zfill(8)
    return byteslist

if __name__ == '__main__':
    import doctest
    doctest.testmod()