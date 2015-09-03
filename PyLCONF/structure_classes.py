"""
### PyLCONF.structure_classes

#### Overview

Most of the code in `structure_classes.py` is based on the [ReOBJ package](<https://github.com/peter1000/ReOBJ)
by the same author: `The BSD 3-Clause License`.

These Classes are used for *LCONF-Template-Structure* to implement the defaults, LCONF-Value-Types and related order.

#### Features

`Root`: LCONF-Template-Structure Main/Root obj class (dict).
`Single_Block`: LCONF-Template-Structure Single-Block obj class (dict).

`emit_default_obj`: Return a section_string from a none parsed `LCONF-Template-Structure`.
`prepare_default_obj`: Returns a prepared default lconf obj (a recursive copy of a template_structure_obj).
"""

from os.path import (
    abspath as path_abspath,
    dirname as path_dirname,
    join as path_join
)

from PyLCONF.utilities import (
       Err,
       MethodDeactivatedErr,
)

from PyLCONF.constants import (
    ### Single Characters
    LCONF_SPACE,
    LCONF_PLUS,
    LCONF_MINUS,

    ### Literal Name Tokens
    LCONF_SECTION_START as SECTION_START_TOKEN,
    LCONF_SECTION_END   as SECTION_END_TOKEN,
    LCONF_TRUE,
    LCONF_FALSE,

    ### Value Types
    LCONF_Comment,
    LCONF_String,
    LCONF_Boolean,
    LCONF_Integer,
    LCONF_Single_Block,
    LCONF_Repeated_Block,

    # Item-Requirement-Option
    ITEM_OPTIONAL,
    ITEM_REQUIRED,
    ITEM_REQUIRED_NOT_EMPTY,

    # EMIT Default-Comment Options
    EMIT_NO_COMMENTS,
    EMIT_ONLY_MANUAL_COMMENTS,
    EMIT_ALL_COMMENTS,

    # Others
    LCONF_INTEGER_LOWEST,
    LCONF_INTEGER_HIGHEST,
    LCONF_EMPTY_STRING,
    LCONF_BLANK_COMMENT_LINE,

    COMMENT_DUMMY,
    LCONF_DEFAULT_SINGLE_BLOCK,
    LCONF_EMPTY_REPEATED_BLOCK,
)

from PyLCONF.lconf_classes import (
    LconfRoot,
)


# =================================================================================================================== #

def _deactivated(*args, **kwargs):
    raise MethodDeactivatedErr()


# === === === `LCONF-Value-Types`  === === === #
#
# def LCONF_Comment():
#     pass
#
# def LCONF_String(str_str, extra_err_info):
#     """
#     #### structure_classes.LCONF_String
#
#     Return the input `str_str`.
#
#     `LCONF_String(str_str, extra_err_info)`
#
#     **Parameters:**
#
#     * `str_str`: (str) string of a LCON-String.
#     * `extra_err_info`: (str) any additional info which will be printed if an error is raised: e.g line number,
#         original line ect..
#
#     **Returns:** (str) the input str_str
#
#     *Definition:*
#
#     A LCONF-String Value is a sequence of zero or more Unicode characters. It never spans multiple lines.
#
#     NOTE: this function is only here use the same interface for all LCONF-Value-Types.
#     """
#     return str_str
#
#
# def LCONF_Integer(int_str, extra_err_info):
#     """
#     #### structure_classes.LCONF_Integer
#
#     Return an integer of the input `int_str`.
#
#     `LCONF_Integer(int_str, extra_err_info)`
#
#     **Parameters:**
#
#     * `int_str`: (str) string of a LCONF-Integer.
#     * `extra_err_info`: (str) any additional info which will be printed if an error is raised: e.g line number,
#         original line ect..
#
#     **Returns:** (int) conversion of the input int_str
#
#     *Definition:*
#
#     A LCONF-Integer Value MUST contain only LCONF-Digits. It MAY have a preceding LCONF-Plus or LCONF-Minus.
#
#     * 64 bit (signed long) range expected (-9223372036854775808 to 9223372036854775807).
#     """
#
#     # check any preceding LCONF-Plus or LCONF-Minus.
#     if int_str[0] == LCONF_PLUS or int_str[0] == LCONF_MINUS:
#         if int_str[1:].isdigit():
#             value_int = int(int_str)
#     elif int_str.isdigit():
#         value_int = int(int_str)
#     else:
#         raise Err('`LCONF_Integer`', [
#             'int_str MUST contain only LCONF-Digits. It MAY have a preceding LCONF-Plus or LCONF-Minus.',
#             '  We got: <{}>'.format(int_str),
#             '    extra_err_info: {}'.format(extra_err_info)
#         ])
#
#     if value_int < LCONF_INTEGER_LOWEST or value_int > LCONF_INTEGER_HIGHEST:
#         raise Err('LCONF_Integer', [
#            'int_str 64 bit (signed long) range expected (-9223372036854775808 to +9223372036854775807).',
#            '  We got: <{}>'.format(int_str),
#            '    extra_err_info: {}'.format(extra_err_info)
#         ])
#     return value_int
#


# === === === `LCONF-Template-Structure` Classes === === === #
#
# | **Name**             | **Definition**                                                              |
# |:---------------------|:----------------------------------------------------------------------------|
# | LCONF-Key-Value-Pair | Associates a LCONF-Key-Name with one data value.                            |
# | LCONF-Table          | Associates a LCONF-Key-Name with ordered tabular-data (columns and rows).   |
# | LCONF-List           | Associates a LCONF-Key-Name with an ordered sequence (list) of data values. |
# | LCONF-Single-Block   | A collection of any of the five LCONF-Structures.                           |
# | LCONF-Repeated-Block | A collection of repeated LCONF-Single-Blocks.                               |


class Root(dict):
    """
    #### structure_classes.Root

    LCONF-Template-Structure Main/Root obj class (dict).

    `Root(default_indentation_per_level, default_section_name, key_value_list)`

    **Parameters:**

    * `default_indentation_per_level`: (int)
    * `default_section_name`: (str)
    * `key_value_list`: (list) of tuples: FORMAT:
        ('Key-Name', 'Default-Value', Value-Type, Item-Requirement-Option, Empty-Replacement-Value)

    **Has Additional Attributes:**

    * `key_order`: (list) the keys in order as initialized inclusive `Default-Comment/Blank Lines`
    * `key_order_no_comments`: (list) the keys in order as initialized exclusive `Default-Comment/Blank Lines`
    * `default_indentation_per_level`
    * `default_section_name`
    """

    def __init__(self, default_indentation_per_level, default_section_name, key_value_list):
        if key_value_list.__class__ is list:
            dict.__init__(self, {key_value_tuple[0]: key_value_tuple[1:] for key_value_tuple in key_value_list})
            self.__dict__['key_order'] = [item[0] for item in key_value_list]
            self.__dict__['key_order_no_comments'] = [item[0] for item in key_value_list if item[2] != LCONF_Comment]
            self.__dict__['default_indentation_per_level'] = default_indentation_per_level
            self.__dict__['default_section_name'] = default_section_name
        else:
            raise Err('Root.__init__()', [
               'key_value_list must be a list of key/value pairs: We got type: <{}>'.format(type(key_value_list)),
               '   <{}>'.format(key_value_list)
            ])

    def set_class__dict__item(self, key, value):
        """ Sets the class __dict__: key to value: if key did not exist it is added

        * `key`: (str)
        * `value`: (any)
        """
        self.__dict__[key] = value

    # DEACTIVATED
    clear = _deactivated
    copy = _deactivated
    __add__ = _deactivated
    __delattr__ = _deactivated
    __delitem__ = _deactivated
    __setitem__ = _deactivated
    __setattr__ = _deactivated
    __reduce__ = _deactivated
    setdefault = _deactivated
    pop = _deactivated
    popitem = _deactivated
    update = _deactivated
    get = _deactivated
    fromkeys = _deactivated


class Single_Block(dict):
    """
    #### structure_classes.Single_Block

    LCONF-Template-Structure Single-Block obj class (dict).

    `Single_Block(key_value_list)`

    **Parameters:**

    * `key_value_list`: (list) of tuples: FORMAT:
        ('Key-Name', 'Default-Value', Value-Type, Item-Requirement-Option, Empty-Replacement-Value)

        * MUST NOT be empty

    **Has Additional Attributes:**

    * `key_order`: (list) the keys in order as initialized inclusive `Default-Comment/Blank Lines`
    * `key_order_no_comments`: (list) the keys in order as initialized exclusive `Default-Comment/Blank Lines`
    """

    def __init__(self, key_value_list):
        if key_value_list.__class__ is list:
            if key_value_list:
                dict.__init__(self, {key_value_tuple[0]: key_value_tuple[1:] for key_value_tuple in key_value_list})
                self.__dict__['key_order'] = [item[0] for item in key_value_list]
                self.__dict__['key_order_no_comments'] = [item[0] for item in key_value_list if item[2] != LCONF_Comment]
            else:
                raise Err('Single_Block.__init__()', [
                   'key_value_list MUST NOT be Empty: We got: <{}>'.format(key_value_list),
                ])
        else:
            raise Err('Single_Block.__init__()', [
               'key_value_list MUST be a list of key/value pairs: We got type: <{}>'.format(type(key_value_list)),
               '   <{}>'.format(key_value_list)
            ])

    def set_class__dict__item(self, key, value):
        """ Sets the class __dict__: key to value: if key did not exist it is added

        * `key`: (str)
        * `value`: (any)
        """
        self.__dict__[key] = value

    # DEACTIVATED
    clear = _deactivated
    copy = _deactivated
    __add__ = _deactivated
    __delattr__ = _deactivated
    __delitem__ = _deactivated
    __setitem__ = _deactivated
    __setattr__ = _deactivated
    __reduce__ = _deactivated
    setdefault = _deactivated
    pop = _deactivated
    popitem = _deactivated
    update = _deactivated
    get = _deactivated
    fromkeys = _deactivated

# class Repeated_Block(dict):
#     """
#     #### structure_classes.Repeated_Block
#
#     LCONF-Template-Structure Repeated-Block obj class (dict).
#
#     `Repeated_Block(key_value_list)`
#
#     **Parameters:**
#
#     * `min_required_blocks`:   (int) number of minimum required defined Single-Blocks  (Repeated-Block Items)
#
#         * 0 or greater
#         * to not define it: set it to `-1`
#
#     * `max_allowed_blocks`:    (int) number of maximum allowed defined Single-Blocks   (Repeated-Block Items)
#
#         * 1 or greater
#         * to not define it: set it to `-1`
#
#     * `template_single_block`: (obj) template implementation of the Single-Blocks      (Repeated-Block Items)
#
#     **Has Additional Attributes:**
#
#     * `min_required_blocks`: (int) number of minimum required defined Single-Blocks
#     * `max_allowed_blocks`:  (int) number of maximum allowed defined Single-Blocks
#     """
#
#     def __init__(self, min_required_blocks, max_allowed_blocks, template_single_block):
#         # if key_value_list.__class__ is list:
#         #     if key_value_list:
#         #         dict.__init__(self, {key_value_tuple[0]: key_value_tuple[1:] for key_value_tuple in key_value_list})
#         #         self.__dict__['key_order'] = [item[0] for item in key_value_list]
#         #         self.__dict__['key_order_no_comments'] = [item[0] for item in key_value_list if item[2] != LCONF_Comment]
#         #     else:
#         #         raise Err('Repeated_Block.__init__()', [
#         #            'key_value_list MUST NOT be Empty: We got: <{}>'.format(key_value_list),
#         #         ])
#         # else:
#         #     raise Err('Repeated_Block.__init__()', [
#         #        'key_value_list MUST be a list of key/value pairs: We got type: <{}>'.format(type(key_value_list)),
#         #        '   <{}>'.format(key_value_list)
#         #     ])
#
#     def set_class__dict__item(self, key, value):
#         """ Sets the class __dict__: key to value: if key did not exist it is added
#
#         * `key`: (str)
#         * `value`: (any)
#         """
#         self.__dict__[key] = value
#
#     # DEACTIVATED
#     clear = _deactivated
#     copy = _deactivated
#     __add__ = _deactivated
#     __delattr__ = _deactivated
#     __delitem__ = _deactivated
#     __setitem__ = _deactivated
#     __setattr__ = _deactivated
#     __reduce__ = _deactivated
#     setdefault = _deactivated
#     pop = _deactivated
#     popitem = _deactivated
#     update = _deactivated
#     get = _deactivated
#     fromkeys = _deactivated

# =================================================================================================================== #



def _emit_default_obj__only_manual_comments(result_, key_name, item_value_tuple, indent, indent_per_level):
    """
    """
    default_value, value_type, item_required_option, empty_replacement_value = item_value_tuple

    if value_type == LCONF_Comment:
        if default_value:
            result_.append('{}{}'.format(indent, default_value))
        else:
            # LCONF_BLANK_COMMENT_LINE
            result_.append(default_value)
    else:
        if value_type == LCONF_String:
            if default_value:
                result_.append('{}{} :: {}'.format(indent, key_name, default_value))
            else:
                result_.append('{}{} ::'.format(indent, key_name))
        elif value_type == LCONF_Integer:
            if default_value:
                result_.append('{}{} :: {}'.format(indent, key_name, default_value))
            else:
                result_.append('{}{} ::'.format(indent, key_name))
        elif value_type == LCONF_Single_Block:
            result_.append('{}. {}'.format(indent, key_name))
            for single_block__key_name in default_value.key_order:
                _emit_default_obj__only_manual_comments(result_, single_block__key_name,
                                                        default_value[single_block__key_name],
                                                        indent + indent_per_level, indent_per_level)
        else:
            raise Err('_emit_default_obj__no_comments', [
               'UnKnown LCONF-Value-Type ERROR: We got type: <{}>'.format(value_type),
               '   key_name: <{}> default_value: <{}> value_type: <{}>'.format(key_name, default_value, value_type)
            ])

    #     if item_value_.__class__ is str:
    #         if item_value_:
    #             result_.append('{}{} :: {}'.format(indent, key_, item_value_))
    #         else:
    #             result_.append('{}{} ::'.format(indent, key_))
    #     # `LCONF-Single-Block`
    #     elif item_value_.__class__ is KVMap:
    #         result_.append('{}. {}'.format(indent, key_))
    #         for mapping_key in item_value_.key_order:
    #             _output_helper_emit__default_obj(result_, mapping_key, item_value_[mapping_key][0], onelinelists_,
    #                with_comments_, indent + '   ')
    #     elif item_value_.__class__ is KVList:
    #         if onelinelists_ == LCONF_DEFAULT:
    #             use_oneline_list_type = LCONF_YES if item_value_.use_oneline else LCONF_NO
    #         else:
    #             use_oneline_list_type = onelinelists_
    #
    #         # do the check
    #         if use_oneline_list_type == LCONF_YES:
    #             temp_items = []
    #             for i_ in item_value_:
    #                 temp_items.append('%s' % i_)
    #             if temp_items:
    #                 result_.append('{}- {} :: {}'.format(indent, key_, ','.join(temp_items)))
    #             else:
    #                 result_.append('{}- {} ::'.format(indent, key_))
    #
    #         elif use_oneline_list_type == LCONF_NO:
    #             result_.append('{}- {}'.format(indent, key_))
    #             for a_ in item_value_:
    #                 result_.append('{}   {}'.format(indent, a_))
    #     elif item_value_.__class__ is ListOT:
    #         result_.append('{}- {} |{}|'.format(indent, key_, '|'.join(item_value_.column_names)))
    #         for row_ in item_value_:
    #             temp_items = []
    #             for i_ in row_:
    #                 temp_items.append('%s' % i_)
    #             result_.append('{}   {}'.format(indent, ','.join(temp_items)))
    #     elif item_value_.__class__ is BlkI:
    #         result_.append('{}* {}'.format(indent, key_))
    #         # IMPORTANT: Dummy Blk
    #         result_.append('{}   dummy_blk'.format(indent))
    #         dummy_blk = item_value_['dummy_blk']
    #         for mapping_key in dummy_blk.key_order:
    #             _output_helper_emit__default_obj(result_, mapping_key, dummy_blk[mapping_key][0], onelinelists_, with_comments_,
    #                indent + '      ')  # 3 for blk-name + 3 new for the blk items
    #     else:
    #         result_.append('{}{} :: {}'.format(indent, key_, item_value_))


def _emit_default_obj__all_comments(result_, key_name, item_value_tuple, indent, indent_per_level):
    """
    """
    # TODO: Comments: should we check for correct setting: if key_name[0] == '#': OR Check even the default_value[0] == '#'
    default_value, value_type, item_required_option, empty_replacement_value = item_value_tuple

    if value_type == LCONF_Comment:
        if default_value:
            result_.append('{}{}'.format(indent, default_value))
        else:
            # LCONF_BLANK_COMMENT_LINE
            result_.append(default_value)
    else:

        if value_type == LCONF_Single_Block:
            # Auto-Comment-Lines
            result_.append("# Key-Name: `{}` | Type: <{}> | <{}>".format(key_name, value_type, item_required_option))
            result_.append("#   Default: <{}> | Empty-Default: <{}>".format(LCONF_DEFAULT_SINGLE_BLOCK, empty_replacement_value))

            result_.append('{}. {}'.format(indent, key_name))
            for single_block__key_name in default_value.key_order:
                _emit_default_obj__all_comments(result_, single_block__key_name,
                                                default_value[single_block__key_name],
                                                indent + indent_per_level, indent_per_level)
        else:
            # Auto-Comment-Lines
            result_.append("# Key-Name: `{}` | Type: <{}> | <{}>".format(key_name, value_type, item_required_option))
            result_.append("#   Default: <{}> | Empty-Default: <{}>".format(default_value, empty_replacement_value))

            if value_type == LCONF_String:
                if default_value:
                    result_.append('{}{} :: {}'.format(indent, key_name, default_value))
                else:
                    result_.append('{}{} ::'.format(indent, key_name))
            elif value_type == LCONF_Integer:
                if default_value:
                    result_.append('{}{} :: {}'.format(indent, key_name, default_value))
                else:
                    result_.append('{}{} ::'.format(indent, key_name))
            elif value_type == LCONF_Single_Block:
                result_.append('{}. {}'.format(indent, key_name))
                for single_block__key_name in default_value.key_order:
                    _emit_default_obj__only_manual_comments(result_, single_block__key_name,
                                                            default_value[single_block__key_name],
                                                            indent + indent_per_level, indent_per_level)
            else:
                raise Err('_emit_default_obj__no_comments', [
                   'UnKnown LCONF-Value-Type ERROR: We got type: <{}>'.format(value_type),
                   '   key_name: <{}> default_value: <{}> value_type: <{}>'.format(key_name, default_value, value_type)
                ])
        result_.append(LCONF_BLANK_COMMENT_LINE)


def _emit_default_obj__no_comments(result_, key_name, item_value_tuple, indent, indent_per_level):
    """ Helper for output: processes a MAIN or Block-Key

    :param result_:
    :param key_:
    :param item_value_:
    :param onelinelists_:
    :param with_comments_:
    :param indent:

    item_value_tuple: ('Default-Value', Value-Type, Item-Requirement-Option, Empty-Replacement-Value)
    """
    default_value, value_type, item_required_option, empty_replacement_value = item_value_tuple

    if value_type == LCONF_String:
        if default_value:
            result_.append('{}{} :: {}'.format(indent, key_name, default_value))
        else:
            result_.append('{}{} ::'.format(indent, key_name))
    elif value_type == LCONF_Integer:
        if default_value:
            result_.append('{}{} :: {}'.format(indent, key_name, default_value))
        else:
            result_.append('{}{} ::'.format(indent, key_name))
    elif value_type == LCONF_Single_Block:
        result_.append('{}. {}'.format(indent, key_name))
        for single_block__key_name in default_value.key_order_no_comments:
            _emit_default_obj__no_comments(result_, single_block__key_name,
                                           default_value[single_block__key_name],
                                           indent + indent_per_level, indent_per_level)
    else:
        raise Err('_emit_default_obj__no_comments', [
           'UnKnown LCONF-Value-Type ERROR: We got type: <{}>'.format(value_type),
           '   key_name: <{}> default_value: <{}> value_type: <{}>'.format(key_name, default_value, value_type)
        ])


def emit_default_obj(template_structure_obj, with_comments):
    """
    #### structure_classes.emit_default_obj

    Return a section_string from a none parsed `LCONF-Template-Structure`.

    `emit_default_obj(lconf_template_structure_obj, with_comments)`

    **Parameters:**

    * `template_structure_obj`: (obj) instance of a LCONF-Template-Structure Main/Root obj.
    * `with_comments`: (str) if True emits also any LCONF-Default-Comment-Lines.

        * EMIT_NO_COMMENTS           # NO Comments at all
        * EMIT_ONLY_MANUAL_COMMENTS  # Only Manual Default Comments
        * EMIT_ALL_COMMENTS          # Auto Comments and Manual Default Comments

    """

    result = ['{} :: {} :: {}'.format(SECTION_START_TOKEN,
                                      template_structure_obj.default_indentation_per_level,
                                      template_structure_obj.default_section_name)]

    indent_per_level = LCONF_SPACE * template_structure_obj.default_indentation_per_level
    print("\n\nfinal_indent_per_level: <{}>".format(indent_per_level))

    # Loop through LCONF-Template-Structure Main/Root obj
    if with_comments == EMIT_ONLY_MANUAL_COMMENTS:
        for key_name in template_structure_obj.key_order:
            _emit_default_obj__only_manual_comments(result, key_name, template_structure_obj[key_name], '', indent_per_level)

    elif with_comments == EMIT_ALL_COMMENTS:
        for key_name in template_structure_obj.key_order:
            _emit_default_obj__all_comments(result, key_name, template_structure_obj[key_name], '', indent_per_level)

    elif with_comments == EMIT_NO_COMMENTS:
        for key_name in template_structure_obj.key_order_no_comments:
            _emit_default_obj__no_comments(result, key_name, template_structure_obj[key_name], '', indent_per_level)
    else:
        raise Err('emit_default_obj', [
            'WRONG `with_comments`: MUST be one of: `EMIT_NO_COMMENTS, EMIT_ONLY_MANUAL_COMMENTS, EMIT_ALL_COMMENTS`',
            '       We Got: <{}>'.format(with_comments),
            ''
        ])

    result.append(SECTION_END_TOKEN)
    return '\n'.join(result)


def _prepare_default_obj__no_comments(input_obj, key):
    """ Helper: to make a recursively copy of the lconf_section__template_ob

    """
    default_value, value_type, item_required_option, empty_replacement_value = input_obj[key]


    if value_type == LCONF_Single_Block:
        print("_prepare_default_obj__no_comments: value_type == LCONF_Single_Block : not yet implemented")
    else:
        return default_value


def _prepare_default_obj__with_comments(input_obj, key):
    """ Helper: to make a recursively copy of the lconf_section__template_ob

    """
    default_value, value_type, item_required_option, empty_replacement_value = input_obj[key]


    if value_type == LCONF_Single_Block:
        print("_prepare_default_obj__with_comments: value_type == LCONF_Single_Block : not yet implemented")
    else:
        return default_value


def prepare_default_obj(template_structure_obj, with_comments=False):
    """
    #### structure_classes.prepare_default_obj

    Returns a prepared default lconf obj (a recursive copy of a template_structure_obj).

    `prepare_default_obj(template_structure_obj, with_comments=False)`

    **Parameters:**

    * `template_structure_obj`: (obj) instance of a LCONF-Template-Structure Main/Root obj.
    * `with_comments`: (bool) if True includes also also any defined LCONF-Default-Comment-Lines.

    **Returns:** (lconf_default_obj obj) prepared copy of the template_structure_obj
    """
    if with_comments:
        lconf_default_obj = LconfRoot(
           {key: _prepare_default_obj__with_comments(template_structure_obj, key) for key in
              template_structure_obj.key_order},
           template_structure_obj.key_order
        )
        lconf_default_obj.set_class__dict__item('has_comments', True)
    else:
        lconf_default_obj = LconfRoot(
           {key: _prepare_default_obj__no_comments(template_structure_obj, key) for key in
              template_structure_obj.key_order_no_comments},
           template_structure_obj.key_order_no_comments
        )
        lconf_default_obj.set_class__dict__item('has_comments', False)
    return lconf_default_obj

# =====================================================================================================================
def TOOD_deletelater():
    print("\n\nTOOD_deletelater\n\n")

    # ('Key-Name', 'Default-Value', Value-Type, Item-Requirement-Option, Empty-Replacement-Value),
    lconf_template_structure = Root(4, "Example1", [
        # Default LCONF_BLANK_COMMENT_LINE,
        ('#1', LCONF_BLANK_COMMENT_LINE,                      LCONF_Comment, COMMENT_DUMMY, COMMENT_DUMMY),
        # Default Comment Line
        ('#2', '# Comment-Line: below Main `Key-Value-Pair`', LCONF_Comment, COMMENT_DUMMY, COMMENT_DUMMY),
        ('FirstName', 'Mary',                                 LCONF_String,  ITEM_REQUIRED_NOT_EMPTY, LCONF_EMPTY_STRING),
        ('LastName',  'Watson',                               LCONF_String,  ITEM_REQUIRED_NOT_EMPTY, LCONF_EMPTY_STRING),
        ('Age',      48,                                      LCONF_Integer, ITEM_OPTIONAL, None),
        ('single_block_address', Single_Block([
            ('#1', '# Comment-Line:  Single_Block items', LCONF_Comment, COMMENT_DUMMY, COMMENT_DUMMY),
            ('Street', '768 5th Ave # 1332', LCONF_String,  ITEM_REQUIRED_NOT_EMPTY, LCONF_EMPTY_STRING),
            ('City', 'New York', LCONF_String,  ITEM_REQUIRED_NOT_EMPTY, LCONF_EMPTY_STRING),
            ('State', 'NY', LCONF_String,  ITEM_REQUIRED_NOT_EMPTY, LCONF_EMPTY_STRING),
            ('ZIPCode', '10019', LCONF_String,  ITEM_REQUIRED_NOT_EMPTY, None),
            ]), LCONF_Single_Block, ITEM_REQUIRED_NOT_EMPTY, LCONF_DEFAULT_SINGLE_BLOCK),
        # Default Comment Line
        ('#3', '# Comment-Line: blabla`', LCONF_Comment, COMMENT_DUMMY, COMMENT_DUMMY),
        ('Registered', False,             LCONF_Boolean,  ITEM_OPTIONAL, None),
        # ('repeated_block_LanguageSkills', Repeated_Block([
        #     Single_Block([
        #         ('Listening', LCONF_EMPTY_STRING, LCONF_String,  ITEM_REQUIRED_NOT_EMPTY, LCONF_EMPTY_STRING),
        #     ], LCONF_Single_Block, ITEM_REQUIRED_NOT_EMPTY, LCONF_DEFAULT_SINGLE_BLOCK),
        #
        # ]), LCONF_Repeated_Block, ITEM_OPTIONAL, LCONF_EMPTY_REPEATED_BLOCK),
    ])


    #
    # print("\n\nlconf_template_structure.key_order: \n", lconf_template_structure.key_order)
    # print("\n\nlconf_template_structure.key_order_no_comments: \n", lconf_template_structure.key_order_no_comments)
    #
    # print("\n\nlconf_template_structure: \n", lconf_template_structure)
    #
    # for k in lconf_template_structure.key_order:
    #     print(k, " : ", lconf_template_structure[k])
    #
    # print("\n\nlconf_template_structure.default_section_name: \n", lconf_template_structure.default_section_name)
    #
    # lconf_template_structure.set_class__dict__item("default_section_name", "NEW NAME")
    # print("\n\n   NEW NAME lconf_template_structure.default_section_name: \n", lconf_template_structure.default_section_name)



    # ===========
    emit_result = emit_default_obj(lconf_template_structure, EMIT_ALL_COMMENTS)
    print("\n\nemit_result: \n\n", emit_result, "\n\n")

    path_to_lconf_file = path_join(path_dirname(path_abspath(__file__)), "emitted_test_lconf.lconf")

    with open(path_to_lconf_file, 'w') as io:
        io.write(emit_result)

    # ===========

    default_obj_result = prepare_default_obj(lconf_template_structure, with_comments=False)
    print("\n\ndefault_obj_result: \n\n", default_obj_result, "\n\n")

    #default_obj_result["key2value_pair_age"] = 99
    #print("\n\ndefault_obj_result: \n\n", default_obj_result, "\n\n")

    #print("\n\nlconf_template_structure: \n\n", lconf_template_structure, "\n\n")

if __name__ == '__main__':

    TOOD_deletelater()


# =================================================================================================================== #
