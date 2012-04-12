'''
Created on Apr 12, 2012

@author: zaeggi
'''

def encode(numbers):
    pass


def encode_number(n):
    '''
    >>> encode_number(10)
    [10]
    >>> encode_number(128)
    [1, 0]
    >>> encode_number(129)
    [1, 1]
    >>> encode_number(500)
    [3, 116]
    >>> encode_number(1000)
    [7, 104]
    '''
    byteslist = []
    while(True):
        byteslist.insert(0, n % 128)
        if n < 128:
            break
        n = n / 128
    byteslist[len(byteslist)-1] += 128
    return byteslist


if __name__ == '__main__':
    import doctest
    doctest.testmod()