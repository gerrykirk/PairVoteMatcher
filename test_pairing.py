import doctest

def test_pairing():
    doctest.testfile('test_pairing.txt', optionflags=doctest.NORMALIZE_WHITESPACE)
    
test_pairing()