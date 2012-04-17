'''



'''

from itertools import chain
import platform

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

def convert_bytes(bytez):
    '''
    Converts the number of bytes into a more convenient format, T for terabyte,
    M for megabyte etc.
    
    NOTE: this method has been copied as is from
    http://www.5dollarwhitebox.org/drupal/node/84
    '''
    bytez = float(bytez)
    if bytez >= 1099511627776:
        terabytes = bytez / 1099511627776
        size = '%.2fT' % terabytes
    elif bytez >= 1073741824:
        gigabytes = bytez / 1073741824
        size = '%.2fG' % gigabytes
    elif bytez >= 1048576:
        megabytes = bytez / 1048576
        size = '%.2fM' % megabytes
    elif bytez >= 1024:
        kilobytes = bytez / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % bytez
    return size

def test_compression_plain_docids(IFfilename):
    int_bytes = calculate_int_bytes_of_IF(IFfilename)
    print 'Uncompressed: ' + str(int_bytes)
    
    all_postings_docids = flatten(get_postings_list_ints(open(IFfilename).readlines()))
    bytelists = vb_encode(all_postings_docids)
    flattened = flatten(bytelists)
    
    # since every entry in the flattened list is 8 bits long, the number of
    # used bytes is exactly the length of the flattened list
    byte_bytes = len(flattened)
    print 'Variable-bit length: ' + str(byte_bytes)
    
    print 'Compression factor (Uncompressed / VB): ' + str(float(int_bytes) / float(byte_bytes))
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()