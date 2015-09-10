class Err(Exception):
    """ Prints Project Error.

    * `error_origin`: (str) to specify from where the error comes.
    * `info_list`   : (list) list of strings to print as message: each list item starts at a new line.
    """

    def __init__(self, error_origin, info_list):
        Exception.__init__(self, error_origin, info_list)
        self.__error_origin = error_origin
        self.__info_list = '\n'.join(info_list)
        self.__txt = '''

        ========================================================================
        PyLCONF-ERROR: generated in <{}>


        {}

        ========================================================================

        '''.format(self.__error_origin, self.__info_list)
        print(self.__txt)


class SectionErr(Exception):
    """ Prints Project Section Error.

    * `error_origin`: (str) to specify from where the error comes.
    * `section_format`: (str) the format of the section.
    * `section_name`: (str) the name of the section.
    * `section_line`: (str) the line of the section.
    * `info_list`   : (list) list of strings to print as message: each list item starts at a new line.
    """

    def __init__(self, error_origin, section_format, section_name, section_line, info_list):
        Exception.__init__(self, error_origin, info_list)
        self.__error_origin = error_origin
        self.__section_format = section_format
        self.__section_name = section_name
        self.__section_line = section_line
        self.__info_list = '\n'.join(info_list)
        self.__txt = '''

        ========================================================================
        PyLCONF-ERROR: generated in <{}>

        LCONF-Section-Format: <{}>
        LCONF-Section-Name:   <{}>

        {}

        LCONF-Section-Line:

            <{}>

        ========================================================================

        '''.format(self.__error_origin, self.__section_format, self.__section_name, self.__info_list, self.__section_line)
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
