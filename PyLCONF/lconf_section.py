"""
### PyLCONF.lconf_section

#### Overview

`extract_sections`: Extracts all LCONF-Sections from the source.
`section_splitlines`: Split one LCONF-Section into lines.
`prepare_section_lines`: Prevalidate a LCONF-Section raw string and returns it's Section-Lines skipping Blank-Lines and
    Comment-Lines.
`validate_one_section_string`: Validate one LCONF-Section raw string.
`validate_sections_from_file`: Validates a LCONF-File containing one or more LCONF-Sections.
`parse_section_lines`: Parses a LCONF-Section raw string already split into lines and updates the section object.
`parse_section`: Parses a LCONF-Section raw string and updates the section object.
"""
from os.path import (
    abspath as path_abspath,
    dirname as path_dirname,
    isfile as path_isfile,
    join as path_join,
)

from PyLCONF.constants import (
    ### Literal Name Tokens
    LCONF_SECTION_START as SECTION_START_TOKEN,
    LCONF_SECTION_END   as SECTION_END_TOKEN,

    ### Structural Tokens
    LCONF_KEY_VALUE_SEPARATOR,
    LCONF_LIST_IDENTIFIER,
    LCONF_TABLE_IDENTIFIER,
    LCONF_TABLE_VALUE_SEPARATOR,
    LCONF_SINGLE_BLOCK_IDENTIFIER,
    LCONF_REPEATED_BLOCK_IDENTIFIER,

    ### Value Types
    LCONF_Comment,
    LCONF_String,
    LCONF_Integer,
    LCONF_Single_Block,

    # Item-Requirement-Option
    ITEM_OPTIONAL,
    ITEM_REQUIRED,
    ITEM_REQUIRED_NOT_EMPTY,

    # EMIT Default-Comment Options
    EMIT_NO_COMMENTS,
    EMIT_ONLY_MANUAL_COMMENTS,
    EMIT_ALL_COMMENTS,

    # Others
    LCONF_EMPTY_STRING,
    LCONF_BLANK_COMMENT_LINE,

    COMMENT_DUMMY,
)

from PyLCONF.structure_classes import (
    Root,

    prepare_default_obj,
)

from PyLCONF.utilities import Err


LENGTH_START_TOKEN = len(SECTION_START_TOKEN)
LENGTH_END_TOKEN   = len(SECTION_END_TOKEN)

# =================================================================================================================== #

def extract_sections(source):
    """
    #### lconf_section.extract_sections

    Extracts all LCONF-Sections from the source.

    `extract_sections(source)`

    **Parameters:**

    * `source`: (raw str) which contains one or more LCONF-Sections

    **Returns:** (list) of LCONF-Sections text each inclusive the `___SECTION, ___END` TAG these are not split by line
        but each in one txt
    """

    # NOTE: This seems to take only about 20% of the time of Regex alternatives
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # # alternatives 1 (slowest if there is a good portion of additional text)
    # p = re_compile(r'({}(.|\n)*?{})'.format(SECTION_START_TOKEN, SECTION_END_TOKEN))
    # return [match[0] for match in p.findall(source)]
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # # alternatives 2
    # lconf_sections = []
    # p = re_compile(r'{}(.|\n)*?{}'.format(SECTION_START_TOKEN, SECTION_END_TOKEN))
    # for match in p.finditer(source):
    #     start, end = match.span()
    #     lconf_sections.append(source[start:end])
    # return lconf_sections
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    length_start_token = len(SECTION_START_TOKEN)
    length_end_token = len(SECTION_END_TOKEN)

    lconf_sections = []
    # Fastest: read the whole file at once and cut all between first : ___SECTION and last ___END in case there is a
    #         lot of additional text.
    # Raise already error if one of them is not found(using str.index)
    first_start_idx = source.index(SECTION_START_TOKEN)
    last_end_idx = source.rindex(SECTION_END_TOKEN)
    main_text_source = source[first_start_idx:last_end_idx + length_end_token]

    # Check multiple sections in source:
    if SECTION_START_TOKEN in main_text_source[length_start_token:]:
        start_idx = 0  # keep first ___SECTION extract_sections but search for ___END extract_sections
        search_for_start = False
        from_here_idx = start_idx
        while True:
            if search_for_start:
                start_idx = main_text_source[from_here_idx:].find(SECTION_START_TOKEN)
                if start_idx == -1:
                    break  # no more docs
                search_for_start = False
                from_here_idx = from_here_idx + start_idx
            else:
                end_idx = main_text_source[from_here_idx:].find(SECTION_END_TOKEN)
                if end_idx == -1:
                    raise Err('extract_sections', [
                        'SECTION_END_TOKEN NOT FOUND: expected <{}>'.format(SECTION_END_TOKEN),
                        '',
                        '',
                        '==================',
                        '{}'.format(main_text_source[from_here_idx:]),
                        '==================',
                        '',
                        ''
                    ])
                # add doc
                end_idx_with_extract_sections = from_here_idx + end_idx + length_end_token
                tmp_section_txt = main_text_source[from_here_idx:end_idx_with_extract_sections]
                if SECTION_START_TOKEN in tmp_section_txt[length_start_token:]:
                    raise Err('extract_sections', [
                        'LCONF-Section-Start FOUND within LCONF-Section. Section text:',
                        '',
                        '',
                        '==================',
                        '{}'.format(tmp_section_txt),
                        '==================',
                        '',
                        ''
                    ])
                lconf_sections.append(main_text_source[from_here_idx:end_idx_with_extract_sections])
                search_for_start = True
                from_here_idx = end_idx_with_extract_sections
    else:
        if SECTION_END_TOKEN in main_text_source[:-length_end_token]:
            raise Err('extract_sections', [
                'LCONF-Section-End FOUND within LCONF-Section. Section text:',
                '',
                '',
                '==================',
                '{}'.format(main_text_source),
                '==================',
                '',
                ''
            ])
        lconf_sections.append(main_text_source)
    return lconf_sections


def section_splitlines(section_text):
    """
    #### lconf_section.section_splitlines

    Split one LCONF-Section into lines.

    `section_splitlines(section_text)`

    **Parameters:**

    * `section_text`: (raw str) which contains exact one LCONF-Section

    **Returns:** (tuple) section_lines, section_indentation_number, section_name

    *Validates:*

    * LCONF-Section-Start-Line (first line)
    * Section-End-Line (last line)
    """

    section_lines = section_text.splitlines()
    first_line = section_lines[0]
    length_first_line = len(first_line)
    # FIRST LINE: special
    # Minimum expected length <___SECTION :: 4 :: X>    LENGTH_START_TOKEN + 10
    min_firstline_length = LENGTH_START_TOKEN + 10
    if length_first_line < min_firstline_length:
        raise Err('section_splitlines', [
            'FIRST LINE ERROR: Minimum expected length: <{}> Got: <{}>'.format(min_firstline_length,
                                                                               length_first_line),
            '',
            '<{}>'.format(first_line)
        ])
    elif first_line[-1] == ' ':
        raise Err('section_splitlines', [
            'FIRST LINE ERROR: TRAILING SPACE',
            '',
            '<{}>'.format(first_line)
        ])
    elif not first_line.startswith('{} :: '.format(SECTION_START_TOKEN)):
        raise Err('section_splitlines', [
           'FIRST LINE ERROR: MUST start with <{} :: >'.format(SECTION_START_TOKEN),
           '',
           '    <{}>'.format(first_line)
        ])

    # LCONF-Indentation-Per-Level | One LCONF-Digit (DIGIT TWO THROUGH DIGIT EIGHT) minimum 2 and maximum 8.
    section_indentation_number_char = first_line[LENGTH_START_TOKEN + 4]
    section_indentation_number_ord = ord(section_indentation_number_char)
    if section_indentation_number_ord < 50 or section_indentation_number_ord > 56:
        raise Err('section_splitlines', [
            'FIRST LINE ERROR: WRONG LCONF-Indentation-Per-Level Number:',
            '                  MUST be one of <2,3,4,5,6,7,8>. Got: <{}>'.format(section_indentation_number_char),
            '',
            '<{}>'.format(first_line)
        ])
    elif not first_line[LENGTH_START_TOKEN + 5:LENGTH_START_TOKEN + 9] == " :: ":
        raise Err('section_splitlines', [
            'FIRST LINE ERROR: LCONF-Indentation-Per-Level Number and LCONF-Section-Name MUST be separated by < :: >',
            '',
            '    <{}>'.format(first_line)
        ])
    elif first_line[LENGTH_START_TOKEN + 9] == ' ':
        raise Err('section_splitlines', [
            'FIRST LINE ERROR: LCONF-Section-Name MUST be preceded by ONE Space.',
            '',
            '    <{}>'.format(first_line)
        ])
    section_indentation_number = int(section_indentation_number_char)
    section_name_start_idx = min_firstline_length - 1
    section_name = first_line[section_name_start_idx:]

    # Validate LCONF-Section-End (last line): no indent
    if section_lines[-1] != SECTION_END_TOKEN:
        raise Err('section_splitlines', [
            'LCONF-Section-Name: {}'.format(section_name),
            '  LCONF-Section-End LINE ERROR: EXPECTED: <{}>'.format(SECTION_END_TOKEN),
            '      <{}>'.format(section_lines[-1])
        ])

    return section_lines, int(section_indentation_number_char), section_name


def prepare_section_lines(section_lines, section_indentation_number, section_name):
    """
    #### lconf_section.prepare_section_lines

    Prevalidate a LCONF-Section raw string and returns it's Section-Lines skipping Blank-Lines and Comment-Lines.

    `prepare_section_lines(section_lines, section_indentation_number, section_name)`

    **Parameters:**

    * `section_lines`: (list) which contains exact one LCONF-Section's lines (inclusive Blank and Comment Lines)
    * `section_indentation_number`: (int) the LCONF-Indentation-Per-Level number
    * `section_name`: (string) the section name

    **Returns:** (list) prepared_lines without the LCONF-Section-Start-Line or raises an error

    *Validates:*

    * No Trailing Spaces
    * Indentation increase jumps (increase more than one LCONF-Indentation-Per-Level)
    * Validates indentation is a multiple of LCONF-Indentation-Per-Level
    """
    prepared_lines = []
    prev_indent = 0
    for orig_line in section_lines[1:]:
        # Skip Blank-Line
        if orig_line:
            # Check Trailing Space
            if orig_line[-1] == ' ':
                raise Err('validate_one_section_string', [
                    'LCONF-Section-Name: {}'.format(section_name),
                    'TRAILING SPACE ERROR',
                    '<{}>'.format(orig_line)
                ])
            # Get Indentation
            line_indent = len(orig_line) - len(orig_line.lstrip())
            # Skip Comment-Line
            if orig_line[line_indent] == '#':
                continue
            # No Indentation Increase Jump
            if line_indent > prev_indent + section_indentation_number:
                raise Err('validate_one_section_string', [
                    'LCONF-Section-Name: {}'.format(section_name),
                    'INDENTATION INCREASE JUMP ERROR',
                        '<{}>'.format(orig_line),
                    '  prev_indent: <{}>  line_indent: <{}>'.format(prev_indent, line_indent),
                    '    Maximum expected indent: <{}> !!'.format(prev_indent + section_indentation_number),
                    '    Indentation must be a multiple of section_indentation_number: <{}>'.format(
                        section_indentation_number)
                ])
            # less indentation must be a multiple of section_indentation_number
            elif line_indent != prev_indent:
                if (line_indent % section_indentation_number) != 0:
                    raise Err('validate_one_section_string', [
                       'SectionName: {}'.format(section_name),
                       'INDENTATION LEVEL WRONG MULTIPLE ERROR:',
                       '    <{}>'.format(orig_line),
                       '    previous indent: <{}> - current line_indent: <{}> !!'.format(prev_indent, line_indent),
                       '    Indentation must be a multiple of LCONF-Indentation-Per-Level: <{}>'.format(
                            section_indentation_number)
                    ])

            prepared_lines.append((line_indent, orig_line))
            prev_indent = line_indent
    return prepared_lines


def validate_one_section_string(section_text):
    """
    #### lconf_section.validate_one_section_string

    Validate one LCONF-Section raw string: it must be already correctly extracted.

    `validate_one_section_string(section_text)`

    **Parameters:**

    * `section_text`: (raw str) which contains exact one LCONF-Section

    **Returns:** (bool) True if success else raises an error

    *Limitations:*

    This does not validate correct LCONF-Key-Names or LCONF-Value-Types which are part of a LCONF-Template-Structure.
    It does also not validate unique LCONF-Key-Names.

    *Validates:*

    * LCONF-Section-Start-Line (first line)
    * Section-End-Line (last line)
    * No Trailing Spaces
    * Indentation increase jumps (increase more than one LCONF-Indentation-Per-Level)
    * Validates indentation is a multiple of LCONF-Indentation-Per-Level
    * Checks for wrong multiple LCONF-List-Value-Separator in one line
    * Validates Identifiers

    """
    section_lines, section_indentation_number, section_name = section_splitlines(section_text)

    prepared_lines = prepare_section_lines(section_lines, section_indentation_number, section_name)

    # ------------------------------------------------------------------
    is_single_block = 'is_single_block'
    is_general_list = 'is_general_list'
    is_table = 'is_table'
    is_repeated_block = 'is_repeated_block'
    # is_repeated_block_type: NAMED or UNNAMED or EMPTY
    is_repeated_block_type = 'NONE'

    is_root = 'is_root'

    # Number of LCONF-Vertical-Line in table rows: will be based on the first row
    table_rows_expected_pipes = -1

    prev_indent = 0
    check_indent = 0
    stack = ['STACK', 'STACK', 'STACK', 'STACK', 'STACK', 'STACK', 'STACK', 'STACK', 'STACK', 'STACK']
    len_stack = 10
    cur_stack_idx = -1
    stack_situation = is_root
    next_idx = 0

    len_prepared_lines = len(prepared_lines)

    for cur_indent, orig_line in prepared_lines:
        next_idx += 1
        if next_idx < len_prepared_lines:
            indentation_next_possible_level = cur_indent + section_indentation_number
            # CHECK NESTED STACK
            if cur_stack_idx >= 0:
                # Current Indent same or less than: check_indent
                if cur_indent <= check_indent:
                    check_idx = int(cur_indent / section_indentation_number)
                    if check_idx == 0:
                        stack = ['STACK', 'STACK', 'STACK', 'STACK', 'STACK',
                                 'STACK', 'STACK', 'STACK', 'STACK', 'STACK']
                        len_stack = 10
                        cur_stack_idx = -1
                        stack_situation = is_root
                        check_indent = 0
                    else:
                        cur_stack_idx = check_idx - 1
                        stack_situation = stack[cur_stack_idx]
            else:
                # Reset
                cur_indent = 0
                check_indent = cur_indent
                cur_stack_idx = -1

            # PROCESS ALL
            orig_stack_situation = stack_situation

            # ====  ==== ==== continue orig_stack_situation ====  ==== ====   #
            # LCONF-List (General-List): Associates a LCONF-Key-Name with an ordered sequence (list) of data values.
            if orig_stack_situation == is_general_list:
                # may not contain value items:
                #   LCONF-Key-Value-Separator
                #   LCONF-Table-Identifier
                #   LCONF-List-Identifier
                #   LCONF-Single-Block-Identifier
                #   LCONF-Repeated-Block-Identifier
                if (LCONF_KEY_VALUE_SEPARATOR in orig_line or
                    orig_line[cur_indent] == LCONF_TABLE_IDENTIFIER or
                    orig_line[cur_indent] == LCONF_LIST_IDENTIFIER or
                    orig_line[cur_indent] == LCONF_SINGLE_BLOCK_IDENTIFIER or
                    orig_line[cur_indent] == LCONF_REPEATED_BLOCK_IDENTIFIER
                    ):
                    raise Err('validate_one_section_string', [
                       'SectionName: {}'.format(section_name),
                       '`LCONF-List (General-List)` WRONG ITEM ERROR:',
                       '  <{}>'.format(orig_line),
                       '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                       '      `Lists` may only contain LCONF-Values'
                    ])

            # LCONF-Table: Associates a LCONF-Key-Name with ordered tabular-data (columns and rows).
            elif orig_stack_situation == is_table:
                # may not contain value items:
                #   LCONF-Key-Value-Separator
                #   LCONF-List-Identifier
                #   LCONF-Single-Block-Identifier
                #   LCONF-Repeated-Block-Identifier
                #
                #   NOTE: LCONF-Table-Identifier and LCONF_TABLE_VALUE_SEPARATOR  are the same.
                #   First and last must be a LCONF_TABLE_VALUE_SEPARATOR - No need to check other identifiers
                if (LCONF_KEY_VALUE_SEPARATOR in orig_line or
                    orig_line[cur_indent] != LCONF_TABLE_VALUE_SEPARATOR or
                    orig_line[-1] != LCONF_TABLE_VALUE_SEPARATOR
                    ):
                    raise Err('validate_one_section_string', [
                        'SectionName: {}'.format(section_name),
                        '`LCONF-Table` WRONG ITEM ERROR:',
                        '  <{}>'.format(orig_line),
                        '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                        '      `Table Rows` MUST start and end with LCONF_TABLE_VALUE_SEPARATORs" <{}>'.format(
                            LCONF_TABLE_VALUE_SEPARATOR),
                        '      `Table Rows` MUST NOT contain LCONF-Key-Value-Separator'
                    ])

                # Item Lines (table rows) must contain all the same:
                #    Number of LCONF-Vertical-Line in table rows: will be based on the first row
                #   table_rows_expected_pipes
                if orig_line.count(LCONF_TABLE_VALUE_SEPARATOR) != table_rows_expected_pipes:
                    raise Err('validate_one_section_string', [
                       'SectionName: {}'.format(section_name),
                       'LCONF-Table ITEM Line (Row) ERROR:',
                       '  <{}>'.format(orig_line),
                       '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                       '      Number of expected `Vertical-Line`: <{}>. Counted `Vertical-Line`: <{}>'.format(
                          table_rows_expected_pipes,
                          orig_line.count(LCONF_TABLE_VALUE_SEPARATOR)
                       )
                    ])

            # LCONF-Repeated-Block: A collection of repeated LCONF-Single-Blocks.
            elif orig_stack_situation == is_repeated_block:
                # Repeated-Block may only contain single indented values: UnNamed or Named LCONF-Single-Blocks
                if LCONF_KEY_VALUE_SEPARATOR in orig_line or orig_line[cur_indent] != LCONF_SINGLE_BLOCK_IDENTIFIER:
                    raise Err('validate_one_section_string', [
                       'SectionName: {}'.format(section_name),
                       'WRONG TYPE ERROR:',
                       '  <{}>'.format(orig_line),
                       '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                       '      `LCONF-Named-Repeated-Block` MUST contain `Named LCONF-Single-Blocks`.'
                    ])

                # Check correct: LCONF-Named-Repeated-Block: Named Single-Block Identifier Name.
                if is_repeated_block_type == 'NAMED':
                    if len(orig_line) <= cur_indent + 1:
                        raise Err('validate_one_section_string', [
                           'SectionName: {}'.format(section_name),
                           'LCONF-Named-Single-Block IDENTIFIER ERROR:',
                           '  <{}>'.format(orig_line),
                           '    Named-Repeated-Block item lines MUST have a named Single-Block-Identifier.'
                        ])
                    if orig_line[cur_indent + 1] != ' ' or orig_line[cur_indent + 2] == ' ':
                        raise Err('validate_one_section_string', [
                           'SectionName: {}'.format(section_name),
                           'LCONF-Named-Single-Block IDENTIFIER ERROR:',
                           '  <{}>'.format(orig_line),
                           '    There MUST be ONE SPACE after the LCONF-Single-Block-Identifier `.`'
                        ])

                # Check correct: LCONF-UnNamed-Repeated-Block: UnNamed Single-Block Identifier Name.
                elif is_repeated_block_type == 'UNNAMED':
                    if len(orig_line) > cur_indent + 1:
                        raise Err('validate_one_section_string', [
                           'SectionName: {}'.format(section_name),
                           'LCONF-UnNamed-Single-Block IDENTIFIER ERROR:',
                           '  <{}>'.format(orig_line),
                           '    UnNamed-Repeated-Block item lines MUST only have one LCONF-Single-Block-Identifier `.`'
                        ])
                else:
                    raise Err('validate_one_section_string', [
                       'SectionName: {}'.format(section_name),
                       'WRONG Repeated-Block Item ERROR:',
                       '  <{}>'.format(orig_line),
                       '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                       '      `LCONF-Repeated-Block` Expected a: `Named or UnNamed LCONF-Single-Block type.',
                       '       Got: <{}>'.format(is_repeated_block_type)
                    ])

                # Check Empty LCONF-Single-Block
                next_line_indent, next_line = prepared_lines[next_idx]
                if next_line_indent == cur_indent + section_indentation_number:
                    stack_situation = is_single_block
                    check_indent = cur_indent
                    cur_stack_idx += 1
                    stack[cur_stack_idx] = stack_situation
                    if cur_stack_idx > len_stack - 3:
                        stack.extend(['STACK', 'STACK', 'STACK', 'STACK', 'STACK',
                                      'STACK', 'STACK', 'STACK', 'STACK', 'STACK'])
                        len_stack += 10
                # LCONF-Repeated-Block: EMPTY BLK-Item (LCONF-Single-Block):  No need to adjust the stack for this
                else:
                    # strictly speaking this is not not needed
                    is_repeated_block_type == 'EMPTY'


            # LCONF-Single-Block: no need to do anything here: orig_stack_situation == is_single_block

            # Root: check any new situation: no need to do anything here: orig_stack_situation == is_root

            # ====  ==== ==== check new orig_stack_situation ====  ==== ====   #
            else:
                # LCONF-List-Identifier
                if orig_line[cur_indent] == LCONF_LIST_IDENTIFIER:
                    if orig_line[cur_indent + 1] != ' ' or orig_line[cur_indent + 2] == ' ':
                        raise Err('validate_one_section_string', [
                           'SectionName: {}'.format(section_name),
                           'LIST IDENTIFIER ERROR:',
                           '  <{}>'.format(orig_line),
                           '    There MUST be ONE SPACE before the List LCONF-Key-Name.'
                        ])

                    # LCONF-Compact-List
                    if LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        # Validate: LCONF-Key-Value-Separator
                        if ' :: ' not in orig_line or '  ::' in orig_line or '::  ' in orig_line:
                            raise Err('validate_one_section_string', [
                               'SectionName: {}'.format(section_name),
                               'LCONF-Compact-List: KEY-VALUE-SEPARATOR ERROR: expected < :: >',
                               '  <{}>'.format(orig_line)
                            ])

                        # Check for wrong double LCONF_KEY_VALUE_SEPARATOR
                        if orig_line.count(LCONF_KEY_VALUE_SEPARATOR) > 1:
                            raise Err('validate_one_section_string', [
                               'SectionName: {}'.format(section_name),
                               'LCONF-Compact-List: more than one KEY-VALUE-SEPARATOR ERROR',
                               '  <{}>'.format(orig_line)
                            ])
                        # No need to adjust the stack for LCONF-Compact-List

                    # LCONF-General-List
                    else:
                        # Check Empty LCONF-General-List
                        next_line_indent, next_line = prepared_lines[next_idx]
                        if next_line_indent == cur_indent + section_indentation_number:
                            stack_situation = is_general_list
                            check_indent = cur_indent
                            cur_stack_idx += 1
                            stack[cur_stack_idx] = stack_situation
                            if cur_stack_idx > len_stack - 3:
                                stack.extend(['STACK', 'STACK', 'STACK', 'STACK', 'STACK',
                                              'STACK', 'STACK', 'STACK', 'STACK', 'STACK'])
                                len_stack += 10

                        # else: LCONF-General-List: EMPTY:  No need to adjust the stack for this

                # LCONF-Table-Identifier
                elif orig_line[cur_indent] == LCONF_TABLE_IDENTIFIER:
                    if orig_line[cur_indent + 1] != ' ' or orig_line[cur_indent + 2] == ' ':
                        raise Err('validate_one_section_string', [
                           'SectionName: {}'.format(section_name),
                           'TABLE IDENTIFIER ERROR:',
                           '  <{}>'.format(orig_line),
                           '    There MUST be ONE SPACE before the Table LCONF-Key-Name.'
                        ])
                    elif orig_line[-1] == LCONF_TABLE_VALUE_SEPARATOR:
                        raise Err('validate_one_section_string', [
                           'SectionName: {}'.format(section_name),
                           'TABLE IDENTIFIER ERROR:',
                           '  <{}>'.format(orig_line),
                           '    Table lines MUST NOT end with a LCONF-Table-Value-Separator.'
                        ])
                    if LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        raise Err('validate_one_section_string', [
                           'SectionName: {}'.format(section_name),
                           'TABLE IDENTIFIER ERROR:',
                           '  <{}>'.format(orig_line),
                           '    Table-Identifier lines MUST NOT contain LCONF-Key-Value-Separators.'
                        ])

                    # Check Empty LCONF-Table
                    next_line_indent, next_line = prepared_lines[next_idx]
                    if next_line_indent == cur_indent + section_indentation_number:
                        stack_situation = is_table
                        check_indent = cur_indent
                        cur_stack_idx += 1
                        stack[cur_stack_idx] = stack_situation
                        if cur_stack_idx > len_stack - 3:
                            stack.extend(['STACK', 'STACK', 'STACK', 'STACK', 'STACK',
                                          'STACK', 'STACK', 'STACK', 'STACK', 'STACK'])
                            len_stack += 10

                        # Item Lines (table rows) must contain all the same:
                        #    Number of LCONF-Vertical-Line in table rows: will be based on the first row
                        #   At least 2
                        table_rows_expected_pipes = next_line.count(LCONF_TABLE_VALUE_SEPARATOR)
                        if table_rows_expected_pipes < 2:
                            raise Err('validate_one_section_string', [
                               'SectionName: {}'.format(section_name),
                               'LCONF-Table ITEM Line (Row) ERROR:',
                               '  <{}>'.format(next_line),
                               '      Number of expected `Vertical-Line` must be at least 2.',
                               '      Counted `Vertical-Line`: <{}>'.format(
                                  orig_line.count(LCONF_TABLE_VALUE_SEPARATOR)
                               )
                            ])
                    # else: LCONF-Table: EMPTY:  No need to adjust the stack for this

                # `LCONF-Single-Block Identifier`: These can only be Named Single-Block
                elif orig_line[cur_indent] == LCONF_SINGLE_BLOCK_IDENTIFIER:
                    if orig_line[cur_indent + 1] != ' ' or orig_line[cur_indent + 2] == ' ':
                        raise Err('validate_one_section_string', [
                        'SectionName: {}'.format(section_name),
                        'LCONF-Single-Block IDENTIFIER ERROR:',
                        '  <{}>'.format(orig_line),
                        '    There MUST be ONE SPACE after the LCONF-Single-Block Identifier <{}>.'.format(
                            LCONF_SINGLE_BLOCK_IDENTIFIER)
                        ])
                    if LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        raise Err('validate_one_section_string', [
                           'SectionName: {}'.format(section_name),
                           'SINGLE-BLOCK IDENTIFIER ERROR:',
                           '  <{}>'.format(orig_line),
                           '    Single-Block Identifier lines MUST NOT contain LCONF-Key-Value-Separators.'
                        ])
                    # Check Empty LCONF-Single-Block
                    next_line_indent, next_line = prepared_lines[next_idx]
                    if next_line_indent == cur_indent + section_indentation_number:
                        stack_situation = is_single_block
                        check_indent = cur_indent
                        cur_stack_idx += 1
                        stack[cur_stack_idx] = stack_situation
                        if cur_stack_idx > len_stack - 3:
                            stack.extend(['STACK', 'STACK', 'STACK', 'STACK', 'STACK',
                                          'STACK', 'STACK', 'STACK', 'STACK', 'STACK'])
                            len_stack += 10
                    # else: LCONF-Single-Block: EMPTY:  No need to adjust the stack for this

                # `LCONF-Repeated-Block`
                elif orig_line[cur_indent] == LCONF_REPEATED_BLOCK_IDENTIFIER:
                    if orig_line[cur_indent + 1] != ' ' or orig_line[cur_indent + 2] == ' ':
                        raise Err('validate_one_section_string', [
                        'SectionName: {}'.format(section_name),
                        'BLOCK IDENTIFIER ERROR:',
                        '  <{}>'.format(orig_line),
                        '    There MUST be ONE SPACE after the LCONF_REPEATED_BLOCK_IDENTIFIER <{}>.'.format(
                            LCONF_REPEATED_BLOCK_IDENTIFIER)
                        ])
                    if LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        raise Err('validate_one_section_string', [
                           'SectionName: {}'.format(section_name),
                           'SINGLE-BLOCK IDENTIFIER ERROR:',
                           '  <{}>'.format(orig_line),
                           '    Repeated-Block Identifier lines MUST NOT contain LCONF-Key-Value-Separators.'
                        ])

                    # Check Empty LCONF-Repeated-Block
                    next_line_indent, next_line = prepared_lines[next_idx]
                    if next_line_indent == cur_indent + section_indentation_number:
                        stack_situation = is_repeated_block
                        check_indent = cur_indent
                        cur_stack_idx += 1
                        stack[cur_stack_idx] = stack_situation
                        if cur_stack_idx > len_stack - 3:
                            stack.extend(['STACK', 'STACK', 'STACK', 'STACK', 'STACK',
                                          'STACK', 'STACK', 'STACK', 'STACK', 'STACK'])
                            len_stack += 10

                        if len(next_line) == next_line_indent + 1:
                            is_repeated_block_type = 'UNNAMED'
                        else:
                            is_repeated_block_type = 'NAMED'
                    # else: LCONF-Single-Block: EMPTY:  No need to adjust the stack for this

                # `LCONF-Key-Value-Pair:  we checked already for: LCONF-List (Compact-List)
                elif LCONF_KEY_VALUE_SEPARATOR in orig_line:
                    # Validate: LCONF-Key-Value-Separator
                    if ('  ::' in orig_line or '::  ' in orig_line or
                        (' :: ' not in orig_line and orig_line[-3:] != ' ::')):
                        raise Err('validate_one_section_string', [
                           'SectionName: {}'.format(section_name),
                           'KEY-VALUE-SEPARATOR < :: > ERROR:',
                           '  <{}>'.format(orig_line)
                        ])

                    # Check for wrong double LCONF_KEY_VALUE_SEPARATOR
                    if orig_line.count(LCONF_KEY_VALUE_SEPARATOR) > 1:
                        raise Err('validate_one_section_string', [
                           'SectionName: {}'.format(section_name),
                           'LCONF-Key-Value-Pair: more than one KEY-VALUE-SEPARATOR ERROR',
                           '  <{}>'.format(orig_line)
                        ])
                # WRONG
                else:
                    raise Err('validate_one_section_string', [
                       'SectionName: {}'.format(section_name),
                       'SOMETHING Wrong with this line: maybe indentation, wrong type ..',
                       '  <{}>'.format(orig_line)
                    ])
            prev_indent = cur_indent
    return True


def validate_sections_from_file(path_to_lconf_file):
    """
    #### lconf_section.validate_sections_from_file

    Validates a LCONF-File containing one or more LCONF-Sections.

    `validate_sections_from_file(path_to_lconf_file)`

    **Parameters:**

    * `path_to_lconf_file`: (str) path to a file

    **Returns:** (bool) True if success else raises an error

    *Limitations:*

    This does not validate correct LCONF-Key-Names or LCONF-Value-Types which are part of a LCONF-Template-Structure.
    It does also not validate unique LCONF-Key-Names.

    *Validates:*

    * LCONF-Section-Start-Line (first line)
    * Section-End-Line (last line)
    * No Trailing Spaces
    * Indentation increase jumps (increase more than one LCONF-Indentation-Per-Level)
    * Validates indentation is a multiple of LCONF-Indentation-Per-Level
    * Checks for wrong multiple LCONF-List-Value-Separator in one line
    * Validates Identifiers

    """
    if not path_isfile(path_to_lconf_file):
        raise Err('validate_sections_from_file', [
           'Input path seems not to be a file:'
           '   <{}>'.format(path_to_lconf_file)
        ])

    print('\n\n====== VALIDATING SECTIONS IN FILE:\n   <{}>'.format(path_to_lconf_file))
    with open(path_to_lconf_file, 'r') as io:
        for section_lconf_source in extract_sections(io.read()):
            validate_one_section_string(section_lconf_source)
    return True

def parse_section_lines(lconf_obj, section_lines, section_name, template_structure_obj):
    """
    #### lconf_section.parse_section_lines

    Parses a LCONF-Section raw string already split into lines and updates the section object.

    `parse_section_lines(lconf_obj, section_lines, section_name, template_structure_obj)`

    **Parameters:**

    * `lconf_obj`: (obj) a prepared copy of template_structure_obj
    * `section_lines`: (list)
    * `section_name`: (str)
    * `template_structure_obj`: (obj)
    **Returns:** (obj) updated final lconf_obj.
    """
    lconf_obj.set_class__dict__item('section_name', section_name)

    print("parse_section_lines: STILL MISSI CODE")

    lconf_obj.set_class__dict__item('is_parsed', True)
    return lconf_obj


def parse_section(lconf_obj, section_text, template_structure_obj, validate=False):
    """
    #### lconf_section.parse_section

    Parses a LCONF-Section raw string and updates the section object.

    `parse_section(lconf_obj, section_text, template_structure_obj, validate=False)`

    **Parameters:**

    * `lconf_obj`: (obj) a prepared copy of template_structure_obj
    * `section_text`: (raw str) which contains one LCONF-Section
    * `template_structure_obj`: (obj)
    * `validate`: (bool) if True the `section_text` is first validated and only afterwards parsed.

    **Returns:** (obj) updated final lconf_obj.

        * additionally updates some attributes
    """
    if validate:
        print("parse_section: validate is not yet implemented.")
    section_lines, section_indentation_number, section_name = section_splitlines(section_text)
    return parse_section_lines(lconf_obj, section_lines, section_name, template_structure_obj)

# =====================================================================================================================
def TOOD_deletelater():
    print("\n\nTOOD_deletelater\n\n")

    # ('Key-Name', 'Default-Value', Value-Type, Item-Requirement-Option, Empty-Replacement-Value),
    lconf_template_structure = Root(4, "Example1", [
       # Default LCONF_BLANK_COMMENT_LINE,
       ('#1', LCONF_BLANK_COMMENT_LINE,                      LCONF_Comment, COMMENT_DUMMY, COMMENT_DUMMY),
       # Default Comment Line
       ('#2', '# Comment-Line: below Main `Key-Value-Pair`', LCONF_Comment, COMMENT_DUMMY, COMMENT_DUMMY),
       ('key1value_pair_name', 'Tony',                       LCONF_String,  ITEM_OPTIONAL, LCONF_EMPTY_STRING),
       ('key2value_pair_age',      48,                       LCONF_Integer, ITEM_OPTIONAL, None),
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
    # with_comments = True
    #emit_result = emit_default_obj(lconf_template_structure, EMIT_ONLY_MANUAL_COMMENTS)
    #print("\n\nemit_result: \n\n", emit_result, "\n\n")
    #
    # path_to_lconf_file = path_join(path_dirname(path_abspath(__file__)), "emitted_test_lconf.lconf")
    #
    # with open(path_to_lconf_file, 'w') as io:
    #     io.write(emit_result)

    # ===========

    default_obj_result = prepare_default_obj(lconf_template_structure, with_comments=False)
    # print("\n\ndefault_obj_result: \n\n", default_obj_result, "\n\n")

    #default_obj_result["key2value_pair_age"] = 99
    #print("\n\ndefault_obj_result: \n\n", default_obj_result, "\n\n")

    #print("\n\nlconf_template_structure: \n\n", lconf_template_structure, "\n\n")

    # ===========
    section_text = """___SECTION :: 4 :: Own Test Section

# OWN COMMENT
key1value_pair_name :: FRED
key2value_pair_age :: 17
___END"""
    parse_section_obj = parse_section(default_obj_result, section_text, lconf_template_structure, validate=False)
    print("\n\nparse_section_obj: \n\n", parse_section_obj, "\n\n")
    print("\n\nparse_section_obj.section_name: <", parse_section_obj.section_name, ">")
    print("\n\nparse_section_obj.is_parsed: <", parse_section_obj.is_parsed, ">")


if __name__ == '__main__':

    TOOD_deletelater()
