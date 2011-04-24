import doctest

def basic_tests():
    doctest.testfile('basic_tests.txt', optionflags=doctest.NORMALIZE_WHITESPACE)
    
basic_tests()