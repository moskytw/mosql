'''It provides SQLite-specific implementation for some :mod:`mosql.util` functions.
'''

def format_param(s=''):
    # TODO: This function leaks doc.
    return ':%s' % s if s else '?'

if __name__ == '__main__':
    import doctest
    doctest.testmod()
