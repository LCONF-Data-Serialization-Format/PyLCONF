class Err(Exception):
    """ Prints Project Error.

    * `error_type`: (str) to specify from where the error comes.
    * `info`      : (list) list of strings to print as message: each list item starts at a new line.
    """

    def __init__(self, error_type, info):
        Exception.__init__(self, error_type, info)
        self.__error_type = error_type
        self.__info = '\n'.join(info)
        self.__txt = '''

        ========================================================================
        PyLCONF-{} ERROR:


        {}

        ========================================================================

        '''.format(self.__error_type, self.__info)
        print(self.__txt)


class MethodDeactivatedErr(Exception):
    """ Prints an own raised Deactivated Error.
    """

    def __init__(self):
        Exception.__init__(self, 'Method is deactivated.')
        self.__txt = '''

        ========================================================================
        LCONF-MethodDeactivated ERROR:


        Method is deactivated.

        ========================================================================

        '''
        print(self.__txt)
