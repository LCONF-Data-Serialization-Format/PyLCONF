"""
### PyLCONF.lconf_section

#### Overview

`extract_sections`: Extracts all LCONF-Sections from the source.
`section_splitlines`: Split one LCONF-Section into lines and validates the LCONF-Section-Start-Line / End-Line
`prepare_section_lines`: Prevalidate a LCONF-Section raw string and returns it's Section-Lines skipping
    LCONF_BLANK_LINE and LCONF-Section-Comment-Line.
`validate_one_section_fast`: Validate one LCONF-Section raw string fast.
`validate_one_section_complet`: Validate one LCONF-Section raw string completly.

"""
from os.path import (
    abspath as path_abspath,
    dirname as path_dirname,
    isfile as path_isfile,
    join as path_join,
)

from PyLCONF.constants import (
    ### Single Characters

    LCONF_SPACE,
    ### Literal Name Tokens
    LCONF_SECTION_START as SECTION_START_TOKEN,
    LCONF_SECTION_END   as SECTION_END_TOKEN,
    LCONF_FORMAT_LCONF,
    LCONF_FORMAT_SCHEMA_STRICT,
    LCONF_FORMAT_SCHEMA_FLEXIBLE,
    ### Structural Tokens
    STRUCTURE_LIST_IDENTIFIER,
    STRUCTURE_LIST_VALUE_SEPARATOR,
    STRUCTURE_TABLE_IDENTIFIER,
    STRUCTURE_TABLE_VALUE_SEPARATOR,
    STRUCTURE_SINGLE_BLOCK_IDENTIFIER,
    STRUCTURE_BLOCKS_IDENTIFIER,
    LCONF_COMMENT_LINE_IDENTIFIER,
    LCONF_KEY_VALUE_SEPARATOR,
)

from PyLCONF.utilities import (
    Err,
    SectionErr,
)


LENGTH_START_TOKEN   = 10
LENGTH_END_TOKEN     = 6

# Minimum expected length <___SECTION :: 4 :: LCONF :: X>
MIN_FIRSTLINE_LENGTH = 29

SECTION_FORMAT_PATTERN = " :: LCONF :: "
SCHEMA_STRICT_FORMAT_PATTERN = " :: STRICT :: "
SCHEMA_FLEXIBLE_FORMAT_PATTERN = " :: FLEXIBLE :: "

SECTION_NAME_START_IDX = 28
SCHEMA_STRICT_NAME_START_IDX = 29
SCHEMA_FLEXIBLE_NAME_START_IDX = 31


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

    lconf_sections = []
    # Fastest: read the whole file at once and cut all between first : ___SECTION and last ___END in case there is a
    #         lot of additional text.
    # Raise already error if one of them is not found(using str.index)
    first_start_idx = source.index(SECTION_START_TOKEN)
    last_end_idx = source.rindex(SECTION_END_TOKEN)
    main_text_source = source[first_start_idx:last_end_idx + LENGTH_END_TOKEN]

    # Check multiple sections in source:
    if SECTION_START_TOKEN in main_text_source[LENGTH_START_TOKEN:]:
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
                        '==================',
                        '{}'.format(main_text_source[from_here_idx:]),
                        '==================',
                        ''
                    ])
                # add doc
                end_idx_with_extract_sections = from_here_idx + end_idx + LENGTH_END_TOKEN
                tmp_section_txt = main_text_source[from_here_idx:end_idx_with_extract_sections]
                if SECTION_START_TOKEN in tmp_section_txt[LENGTH_START_TOKEN:]:
                    raise Err('extract_sections', [
                        'LCONF_SECTION_START FOUND within LCONF-Section. Section text:',
                        '',
                        '==================',
                        '{}'.format(tmp_section_txt),
                        '==================',
                        ''
                    ])
                lconf_sections.append(main_text_source[from_here_idx:end_idx_with_extract_sections])
                search_for_start = True
                from_here_idx = end_idx_with_extract_sections
    else:
        if SECTION_END_TOKEN in main_text_source[:-LENGTH_END_TOKEN]:
            raise Err('extract_sections', [
                'LCONF_SECTION_END FOUND within LCONF-Section. Section text:',
                '',
                '==================',
                '{}'.format(main_text_source),
                '==================',
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

    **Returns:** (tuple) section_lines, section_indentation_number, section_format, section_name

    *Validates:*

    * LCONF-Section-Start-Line (first line)
    * LCONF-Section-End-Line (last line)
    """

    section_lines = section_text.splitlines()
    first_line = section_lines[0]
    length_first_line = len(first_line)
    # FIRST LINE: special
    if length_first_line < MIN_FIRSTLINE_LENGTH:
        raise Err('section_splitlines', [
            'FIRST LINE ERROR: Minimum expected length: <{}> Got: <{}>'.format(MIN_FIRSTLINE_LENGTH,
                                                                               length_first_line),
            '',
            '<{}>'.format(first_line)
        ])
    elif first_line[-1] == LCONF_SPACE:
        raise Err('section_splitlines', [
            'FIRST LINE ERROR: Trailing space',
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
            'FIRST LINE ERROR: Wrong LCONF-Indentation-Per-Level Number:',
            '                  MUST be one of <2,3,4,5,6,7,8>. Got: <{}>'.format(section_indentation_number_char),
            '',
            '<{}>'.format(first_line)
        ])

    # Second part of the first line: all after the LCONF-Indentation-Per-Level Number
    section_first_line_second_part = first_line[LENGTH_START_TOKEN + 5:]
    if section_first_line_second_part.startswith(SECTION_FORMAT_PATTERN):
        section_format = LCONF_FORMAT_LCONF
        section_name_start_idx = SECTION_NAME_START_IDX
    elif section_first_line_second_part.startswith(SCHEMA_STRICT_FORMAT_PATTERN):
        section_format = LCONF_FORMAT_SCHEMA_STRICT
        section_name_start_idx = SCHEMA_STRICT_NAME_START_IDX
    elif section_first_line_second_part.startswith(SCHEMA_FLEXIBLE_FORMAT_PATTERN):
        section_format = LCONF_FORMAT_SCHEMA_FLEXIBLE
        section_name_start_idx = SCHEMA_FLEXIBLE_NAME_START_IDX
    else:
        raise Err('section_splitlines', [
            'FIRST LINE ERROR: After the Indentation-Per-Level Number we expected a LCONF_FORMAT_LCONF Pattern',
            '                  <{}>'.format(SECTION_FORMAT_PATTERN),
            '                  <{} >'.format(SCHEMA_STRICT_FORMAT_PATTERN),
            '                  < {}>'.format(SCHEMA_FLEXIBLE_FORMAT_PATTERN),
            '',
            '                  But Got: <{}>'.format(section_first_line_second_part),
            '',
            '<{}>'.format(first_line)
        ])


    if first_line[section_name_start_idx] == LCONF_SPACE:
        raise Err('section_splitlines', [
            'FIRST LINE ERROR: LCONF-Section-Name MUST be preceded by only ONE Space.',
            '',
            '    <{}>'.format(first_line)
        ])
    section_indentation_number = int(section_indentation_number_char)
    section_name = first_line[section_name_start_idx:]

    # Validate LCONF_SECTION_END (last line): no indent
    if section_lines[-1] != SECTION_END_TOKEN:
        raise Err('section_splitlines', [
            'LCONF-Section-Name: {}'.format(section_name),
            '  LCONF_SECTION_END LINE ERROR: EXPECTED: <{}>'.format(SECTION_END_TOKEN),
            '      <{}>'.format(section_lines[-1])
        ])

    return section_lines, int(section_indentation_number_char), section_format, section_name


def prepare_section_lines(section_lines, section_indentation_number, section_format, section_name):
    """
    #### lconf_section.prepare_section_lines

    Prevalidate a LCONF-Section raw string and returns it's Section-Lines skipping LCONF_BLANK_LINE and
    LCONF-Section-Comment-Line.

    `prepare_section_lines(section_lines, section_indentation_number, section_format, section_name)`

    **Parameters:**

    * `section_lines`: (list) which contains exact one LCONF-Section's lines (inclusive Blank and Comment Lines)
    * `section_indentation_number`: (int) the LCONF-Indentation-Per-Level number
    * `section_format`: (string) the section format
    * `section_name`: (string) the section name

    **Returns:** (list) prepared_lines without the LCONF-Section-Start-Line or raises an error

    *Validates:*

    * No Trailing Spaces
    * Indentation increase jumps (increase more than one LCONF-Indentation-Per-Level)
    * Indentation is a multiple of LCONF-Indentation-Per-Level
    """
    prepared_lines = []
    prev_indent = 0
    for orig_line in section_lines[1:]:
        # Skip complete Blank-Line (zero characters)
        if orig_line:
            # Check Trailing Space
            if orig_line[-1] == LCONF_SPACE:
                raise SectionErr('prepare_section_lines', section_format, section_name, orig_line, [
                    'TRAILING SPACE ERROR',
                ])
            # Get Indentation
            line_indent = len(orig_line) - len(orig_line.lstrip())
            # Skip LCONF-Section-Comment-Line
            if orig_line[line_indent] == LCONF_COMMENT_LINE_IDENTIFIER:
                continue
            # No Indentation Increase Jump
            if line_indent > prev_indent + section_indentation_number:
                raise SectionErr('prepare_section_lines', section_format, section_name, orig_line, [
                    'INDENTATION INCREASE JUMP ERROR',
                    '',
                    '  prev_indent: <{}> - current line_indent: <{}>'.format(prev_indent, line_indent),
                    '    Maximum expected indent: <{}> !!'.format(prev_indent + section_indentation_number),
                    '    Indentation must be a multiple of section_indentation_number: <{}>'.format(
                        section_indentation_number),
                ])
            # less indentation must be a multiple of section_indentation_number
            elif line_indent != prev_indent:
                if (line_indent % section_indentation_number) != 0:
                    raise SectionErr('prepare_section_lines', section_format, section_name, orig_line, [
                        'INDENTATION INCREASE JUMP ERROR',
                        '',
                        '  prev_indent: <{}> - current line_indent: <{}>'.format(prev_indent, line_indent),
                        '    Indentation must be a multiple of section_indentation_number: <{}>'.format(
                            section_indentation_number),
                    ])
            prepared_lines.append((line_indent, orig_line))
            prev_indent = line_indent
    return prepared_lines


def validate_one_section_fast(section_text):
    """
    #### lconf_section.validate_one_section_fast

    Validate one LCONF-Section raw string: it must be already correctly extracted.

    `validate_one_section_fast(section_text)`

    **Parameters:**

    * `section_text`: (raw str) which contains exact one LCONF-Section

    **Returns:** (bool) True if success else raises an error

    *Limitations:*

    This does not validate correct LCONF-Key-Names or LCONF-Value-Types with a corresponding LCONF-Schema.
    It does also not validate unique LCONF-Key-Names.

    *Validates:*

    * LCONF-Section-Start-Line (first line)
    * LCONF-Section-End-Line (last line)
    * No Trailing Spaces
    * Indentation increase jumps (increase more than one LCONF-Indentation-Per-Level)
    * Indentation is a multiple of LCONF-Indentation-Per-Level
    * Validates Identifiers
    * Table rows same number of columns

    """
    section_lines, section_indentation_number, section_format, section_name = section_splitlines(section_text)
    prepared_lines = prepare_section_lines(section_lines, section_indentation_number, section_format, section_name)

    # ------------------------------------------------------------------
    is_single_block = 'is_single_block'
    is_general_list = 'is_general_list'
    is_table = 'is_table'
    is_repeated_block = 'is_repeated_block'
    # is_repeated_block_type: NAMED or UNNAMED or EMPTY
    is_repeated_block_type = 'NONE'

    is_root = 'is_root'

    # Number of LCONF_VERTICAL_LINE in table rows: will be based on the first row
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
            # indentation_next_possible_level = cur_indent + section_indentation_number
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
            # STRUCTURE_LIST (General-List): Associates a LCONF-Key-Name with an ordered sequence (list) of data values
            if orig_stack_situation == is_general_list:
                # MUST NOTt contain value items:
                #   STRUCTURE_LIST_IDENTIFIER
                #   STRUCTURE_TABLE_IDENTIFIER
                #   STRUCTURE_SINGLE_BLOCK_IDENTIFIER
                #   STRUCTURE_BLOCKS_IDENTIFIER
                #   LCONF_KEY_VALUE_SEPARATOR
                if (orig_line[cur_indent] == STRUCTURE_LIST_IDENTIFIER or
                    orig_line[cur_indent] == STRUCTURE_TABLE_IDENTIFIER or
                    orig_line[cur_indent] == STRUCTURE_SINGLE_BLOCK_IDENTIFIER or
                    orig_line[cur_indent] == STRUCTURE_BLOCKS_IDENTIFIER or
                    LCONF_KEY_VALUE_SEPARATOR in orig_line
                    ):
                    raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                        'STRUCTURE_LIST ERROR: wrong item',
                        '',
                        '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                        '        `Lists` may only contain LCONF-Values',
                    ])

            # STRUCTURE_TABLE: Associates a LCONF-Key-Name with ordered tabular-data (columns and rows).
            elif orig_stack_situation == is_table:
                # MUST NOTt contain value items:
                #   STRUCTURE_LIST_IDENTIFIER
                #   STRUCTURE_SINGLE_BLOCK_IDENTIFIER
                #   STRUCTURE_BLOCKS_IDENTIFIER
                #   LCONF_KEY_VALUE_SEPARATOR
                #
                #   NOTE: STRUCTURE_TABLE_IDENTIFIER and STRUCTURE_TABLE_VALUE_SEPARATOR are the same.
                #   First and last must be a STRUCTURE_TABLE_VALUE_SEPARATOR - No need to check other identifiers
                if (orig_line[cur_indent] != STRUCTURE_TABLE_VALUE_SEPARATOR or
                    orig_line[-1] != STRUCTURE_TABLE_VALUE_SEPARATOR or
                    LCONF_KEY_VALUE_SEPARATOR in orig_line
                    ):
                    raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                        'STRUCTURE_TABLE ERROR: wrong item',
                        '',
                        '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                        '        `Table Rows` MUST start and end with STRUCTURE_TABLE_VALUE_SEPARATORs" <{}>'.format(
                            STRUCTURE_TABLE_VALUE_SEPARATOR),
                        '    STRUCTURE_TABLE Row lines MUST NOT contain LCONF_KEY_VALUE_SEPARATORs.',
                    ])

                # Item Lines (table rows) must contain all the same:
                #    Number of STRUCTURE_TABLE_VALUE_SEPARATOR in table rows: will be based on the first row
                #   table_rows_expected_pipes
                elif orig_line.count(STRUCTURE_TABLE_VALUE_SEPARATOR) != table_rows_expected_pipes:
                    raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                        'STRUCTURE_TABLE ERROR: wrong columns number.',
                        '',
                        '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                        '        Number of expected `STRUCTURE_TABLE_VALUE_SEPARATOR`: <{}>.'.format(
                            table_rows_expected_pipes),
                        '        Counted `Vertical-Line`: <{}>'.format(
                            orig_line.count(STRUCTURE_TABLE_VALUE_SEPARATOR)),
                    ])

            # STRUCTURE_NAMED_BLOCKS: A collection of repeated named STRUCTURE_SINGLE_BLOCKs.
            # STRUCTURE_UNNAMED_BLOCKS: A collection of repeated unnamed STRUCTURE_SINGLE_BLOCKs.
            elif orig_stack_situation == is_repeated_block:
                # Repeated-Block may only contain single indented values: named or unnamed STRUCTURE_SINGLE_BLOCKs
                if (LCONF_KEY_VALUE_SEPARATOR in orig_line or
                    orig_line[cur_indent] != STRUCTURE_SINGLE_BLOCK_IDENTIFIER
                    ):
                    raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                        'STRUCTURE_BLOCKS ERROR: wrong item type.',
                        '',
                        '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                        '        `STRUCTURE_BLOCKS` MUST contain `STRUCTURE_SINGLE_BLOCKs`.',
                    ])
                # Check STRUCTURE_NAMED_BLOCKS Identifier has a Name.
                if is_repeated_block_type == 'NAMED':
                    if len(orig_line) <= cur_indent + 1:
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'STRUCTURE_NAMED_BLOCKS ERROR: IDENTIFIER line.',
                            '',
                            '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                            '       `STRUCTURE_NAMED_BLOCKS` item line MUST have a name.',
                        ])
                    elif orig_line[cur_indent + 1] != LCONF_SPACE or orig_line[cur_indent + 2] == LCONF_SPACE:
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'STRUCTURE_NAMED_BLOCKS ERROR: IDENTIFIER line.',
                            '',
                            '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                            '    There MUST be ONE SPACE after the STRUCTURE_SINGLE_BLOCK_IDENTIFIER <{}>.'.format(
                                STRUCTURE_SINGLE_BLOCK_IDENTIFIER),
                        ])
                elif is_repeated_block_type == 'UNNAMED':
                    if len(orig_line) > cur_indent + 1:
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'STRUCTURE_UNNAMED_BLOCKS ERROR: IDENTIFIER line.',
                            '',
                            '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                            '       `STRUCTURE_UNNAMED_BLOCKS` item line MUST NOT have a name.',
                        ])
                else:
                    raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                        'STRUCTURE_BLOCKS ERROR: WRONG Blocks type.',
                        '',
                        '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                        '       `STRUCTURE_BLOCKS` Expected a: NAMED or UNNAMED is_repeated_block_type.',
                        '       Got: <{}>'.format(is_repeated_block_type),
                    ])

                # Check STRUCTURE_BLOCKS: Item Empty STRUCTURE_SINGLE_BLOCK
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
                # STRUCTURE_BLOCKS: EMPTY BLK-Item (STRUCTURE_SINGLE_BLOCK):  No need to adjust the stack for this
                else:
                    # strictly speaking this is not needed
                    is_repeated_block_type == 'EMPTY'


            # STRUCTURE_SINGLE_BLOCK: no need to do anything here: orig_stack_situation == is_single_block

            # Root: check any new situation: no need to do anything here: orig_stack_situation == is_root

            # ====  ==== ==== check new orig_stack_situation ====  ==== ====   #
            else:
                # STRUCTURE_LIST_IDENTIFIER
                if orig_line[cur_indent] == STRUCTURE_LIST_IDENTIFIER:
                    if orig_line[cur_indent + 1] != LCONF_SPACE or orig_line[cur_indent + 2] == LCONF_SPACE:
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'STRUCTURE_LIST_IDENTIFIER ERROR.',
                            '',
                            '    There MUST be ONE SPACE before the List LCONF-Key-Name.',
                        ])

                    # Compact_STRUCTURE_LIST
                    if LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        # Validate: LCONF_KEY_VALUE_SEPARATOR
                        if ' :: ' not in orig_line or '  ::' in orig_line or '::  ' in orig_line:
                            raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                                'Compact_STRUCTURE_LIST: KEY-VALUE-SEPARATOR ERROR: expected < :: >',
                            ])
                    # General STRUCTURE_LIST
                    else:
                        # Check STRUCTURE_LIST: Item Empty STRUCTURE_LIST
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
                        # else: STRUCTURE_LIST: EMPTY:  No need to adjust the stack for this

                # STRUCTURE_TABLE_IDENTIFIER
                elif orig_line[cur_indent] == STRUCTURE_TABLE_IDENTIFIER:
                    if orig_line[cur_indent + 1] != LCONF_SPACE or orig_line[cur_indent + 2] == LCONF_SPACE:
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'STRUCTURE_TABLE_IDENTIFIER ERROR.',
                            '',
                            '    There MUST be ONE SPACE before the Table LCONF-Key-Name.',
                        ])
                    elif orig_line[-1] == STRUCTURE_TABLE_VALUE_SEPARATOR:
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'STRUCTURE_TABLE_IDENTIFIER line MUST NOT end with a STRUCTURE_TABLE_VALUE_SEPARATOR.',
                        ])
                    elif LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'STRUCTURE_TABLE_IDENTIFIER lines MUST NOT contain LCONF_KEY_VALUE_SEPARATORs.',
                        ])

                    # Check STRUCTURE_TABLE: Empty (no Row lines)
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
                        #    Number of STRUCTURE_TABLE_VALUE_SEPARATOR in table rows: will be based on the first row
                        #    At least 2
                        table_rows_expected_pipes = next_line.count(STRUCTURE_TABLE_VALUE_SEPARATOR)
                        if table_rows_expected_pipes < 2:
                            raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                                'STRUCTURE_TABLE ITEM Line (Row).',
                                '    Number of expected `STRUCTURE_TABLE_VALUE_SEPARATOR` must be at least 2.',
                                '    Counted `Vertical-Line`: <{}>'.format(
                                    orig_line.count(STRUCTURE_TABLE_VALUE_SEPARATOR)),
                                '',
                                'next_line: <{}>'.format(next_line),
                                '',
                                'orig_line: <{}>'.format(orig_line)
                            ])
                    # else: STRUCTURE_TABLE: EMPTY:  No need to adjust the stack for this

                # `STRUCTURE_SINGLE_BLOCK_IDENTIFIER`: These can only be Named STRUCTURE_SINGLE_BLOCKs
                elif orig_line[cur_indent] == STRUCTURE_SINGLE_BLOCK_IDENTIFIER:
                    if orig_line[cur_indent + 1] != LCONF_SPACE or orig_line[cur_indent + 2] == LCONF_SPACE:
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'There MUST be ONE SPACE before the SINGLE_BLOCK name.',
                        ])
                    elif LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'STRUCTURE_SINGLE_BLOCK_IDENTIFIER lines MUST NOT contain LCONF_KEY_VALUE_SEPARATORs.',
                        ])

                    # Check STRUCTURE_SINGLE_BLOCK: Empty
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
                    # else: STRUCTURE_SINGLE_BLOCK: EMPTY:  No need to adjust the stack for this

                # `STRUCTURE_BLOCKS_IDENTIFIER`
                elif orig_line[cur_indent] == STRUCTURE_BLOCKS_IDENTIFIER:
                    if orig_line[cur_indent + 1] != LCONF_SPACE or orig_line[cur_indent + 2] == LCONF_SPACE:
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'There MUST be ONE SPACE before the STRUCTURE_BLOCKS_IDENTIFIER name.',
                        ])
                    elif LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'STRUCTURE_BLOCKS_IDENTIFIER lines MUST NOT contain LCONF_KEY_VALUE_SEPARATORs.',
                        ])


                    # Check STRUCTURE_BLOCKS: Empty
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

                # `STRUCTURE_PAIR:  we checked already for: Compact_STRUCTURE_LIST
                elif LCONF_KEY_VALUE_SEPARATOR in orig_line:
                    # Validate: LCONF_KEY_VALUE_SEPARATOR
                    if ('  ::' in orig_line or '::  ' in orig_line or
                        (' :: ' not in orig_line and orig_line[-3:] != ' ::')
                        ):
                        raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                            'LCONF_KEY_VALUE_SEPARATOR < :: > ERROR:',
                        ])
                # WRONG
                else:
                    raise SectionErr('validate_one_section_fast', section_format, section_name, orig_line, [
                        'SOMETHING Wrong with this line: maybe indentation, wrong type ..',
                    ])
            prev_indent = cur_indent
    return True


def validate_one_section_complet(section_text, lconf_schema_obj):
    """
    #### lconf_section.validate_one_section_complet

    Validate one LCONF-Section raw string completly: it must be already correctly extracted.

    `validate_one_section_complet(section_text)`

    **Parameters:**

    * `section_text`: (raw str) which contains exact one LCONF-Section
    * `lconf_schema_obj`: (obj) LCONF-Schema object.

    **Returns:** (bool) True if success else raises an error

    *Validates:*

    * LCONF-Section-Start-Line (first line)
    * LCONF-Section-End-Line (last line)
    * No Trailing Spaces
    * Indentation increase jumps (increase more than one LCONF-Indentation-Per-Level)
    * Indentation is a multiple of LCONF-Indentation-Per-Level
    * Validates Identifiers

    * Additional Validation

        * Checks for wrong multiple LCONF-List-Value-Separator in one line
        * Validates correct LCONF-Key-Names, LCONF-Item-Requirement-Option and LCONF-Value-Types with a corresponding
            LCONF-Schema object.
        * Table rows same number of columns as defined in the LCONF-Schema object.

    """
    print("\n\nvalidate_one_section_complet NOT YET IMPLEMENTED\n\n")

                        # # Check for wrong double LCONF_KEY_VALUE_SEPARATOR
                        # if orig_line.count(LCONF_KEY_VALUE_SEPARATOR) > 1:
                        #     raise Err('validate_one_section_fast', [
                        #        'SectionName: {}'.format(section_name),
                        #        'Compact_STRUCTURE_LIST: more than one KEY-VALUE-SEPARATOR ERROR',
                        #        '  <{}>'.format(orig_line)
                        #     ])
                        # # No need to adjust the stack for Compact_STRUCTURE_LIST

    #                 # Check for wrong double LCONF_KEY_VALUE_SEPARATOR
    #                 if orig_line.count(LCONF_KEY_VALUE_SEPARATOR) > 1:
    #                     raise Err('validate_one_section_fast', [
    #                        'SectionName: {}'.format(section_name),
    #                        'LCONF-Key-Value-Pair: more than one KEY-VALUE-SEPARATOR ERROR',
    #                        '  <{}>'.format(orig_line)
    #                     ])


def validate_one_section_schema(section_text):
    """
    #### lconf_section.validate_one_section_schema

    Validate one LCONF-Section-Schema raw string: it must be already correctly extracted.

    `validate_one_section_schema(section_text)`

    **Parameters:**

    * `section_text`: (raw str) which contains exact one LCONF-Section-Schema

    **Returns:** (bool) True if success else raises an error

    *Limitations:*

    It does also not validate unique LCONF-Key-Names.  Maye TODO

    *Validates:*

    * LCONF-Section-Start-Line (first line)
    * LCONF-Section-End-Line (last line)
    * No Trailing Spaces
    * Indentation increase jumps (increase more than one LCONF-Indentation-Per-Level)
    * Indentation is a multiple of LCONF-Indentation-Per-Level
    * Validates Identifiers
    * Table rows same number of columns

    """
    section_lines, section_indentation_number, section_format, section_name = section_splitlines(section_text)

    if section_format ==
    prepared_lines = prepare_section_lines(section_lines, section_indentation_number, section_format, section_name)

    # ------------------------------------------------------------------
    is_single_block = 'is_single_block'
    is_general_list = 'is_general_list'
    is_table = 'is_table'
    is_repeated_block = 'is_repeated_block'
    # is_repeated_block_type: NAMED or UNNAMED or EMPTY
    is_repeated_block_type = 'NONE'

    is_root = 'is_root'

    # Number of LCONF_VERTICAL_LINE in table rows: will be based on the first row
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
            # indentation_next_possible_level = cur_indent + section_indentation_number
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
            # STRUCTURE_LIST (General-List): Associates a LCONF-Key-Name with an ordered sequence (list) of data values
            if orig_stack_situation == is_general_list:
                # MUST NOTt contain value items:
                #   STRUCTURE_LIST_IDENTIFIER
                #   STRUCTURE_TABLE_IDENTIFIER
                #   STRUCTURE_SINGLE_BLOCK_IDENTIFIER
                #   STRUCTURE_BLOCKS_IDENTIFIER
                #   LCONF_KEY_VALUE_SEPARATOR
                if (orig_line[cur_indent] == STRUCTURE_LIST_IDENTIFIER or
                    orig_line[cur_indent] == STRUCTURE_TABLE_IDENTIFIER or
                    orig_line[cur_indent] == STRUCTURE_SINGLE_BLOCK_IDENTIFIER or
                    orig_line[cur_indent] == STRUCTURE_BLOCKS_IDENTIFIER or
                    LCONF_KEY_VALUE_SEPARATOR in orig_line
                    ):
                    raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                        'STRUCTURE_LIST ERROR: wrong item',
                        '',
                        '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                        '        `Lists` may only contain LCONF-Values',
                    ])

            # STRUCTURE_TABLE: Associates a LCONF-Key-Name with ordered tabular-data (columns and rows).
            elif orig_stack_situation == is_table:
                # MUST NOTt contain value items:
                #   STRUCTURE_LIST_IDENTIFIER
                #   STRUCTURE_SINGLE_BLOCK_IDENTIFIER
                #   STRUCTURE_BLOCKS_IDENTIFIER
                #   LCONF_KEY_VALUE_SEPARATOR
                #
                #   NOTE: STRUCTURE_TABLE_IDENTIFIER and STRUCTURE_TABLE_VALUE_SEPARATOR are the same.
                #   First and last must be a STRUCTURE_TABLE_VALUE_SEPARATOR - No need to check other identifiers
                if (orig_line[cur_indent] != STRUCTURE_TABLE_VALUE_SEPARATOR or
                    orig_line[-1] != STRUCTURE_TABLE_VALUE_SEPARATOR or
                    LCONF_KEY_VALUE_SEPARATOR in orig_line
                    ):
                    raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                        'STRUCTURE_TABLE ERROR: wrong item',
                        '',
                        '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                        '        `Table Rows` MUST start and end with STRUCTURE_TABLE_VALUE_SEPARATORs" <{}>'.format(
                            STRUCTURE_TABLE_VALUE_SEPARATOR),
                        '    STRUCTURE_TABLE Row lines MUST NOT contain LCONF_KEY_VALUE_SEPARATORs.',
                    ])

                # Item Lines (table rows) must contain all the same:
                #    Number of STRUCTURE_TABLE_VALUE_SEPARATOR in table rows: will be based on the first row
                #   table_rows_expected_pipes
                elif orig_line.count(STRUCTURE_TABLE_VALUE_SEPARATOR) != table_rows_expected_pipes:
                    raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                        'STRUCTURE_TABLE ERROR: wrong columns number.',
                        '',
                        '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                        '        Number of expected `STRUCTURE_TABLE_VALUE_SEPARATOR`: <{}>.'.format(
                            table_rows_expected_pipes),
                        '        Counted `Vertical-Line`: <{}>'.format(
                            orig_line.count(STRUCTURE_TABLE_VALUE_SEPARATOR)),
                    ])

            # STRUCTURE_NAMED_BLOCKS: A collection of repeated named STRUCTURE_SINGLE_BLOCKs.
            # STRUCTURE_UNNAMED_BLOCKS: A collection of repeated unnamed STRUCTURE_SINGLE_BLOCKs.
            elif orig_stack_situation == is_repeated_block:
                # Repeated-Block may only contain single indented values: named or unnamed STRUCTURE_SINGLE_BLOCKs
                if (LCONF_KEY_VALUE_SEPARATOR in orig_line or
                    orig_line[cur_indent] != STRUCTURE_SINGLE_BLOCK_IDENTIFIER
                    ):
                    raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                        'STRUCTURE_BLOCKS ERROR: wrong item type.',
                        '',
                        '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                        '        `STRUCTURE_BLOCKS` MUST contain `STRUCTURE_SINGLE_BLOCKs`.',
                    ])
                # Check STRUCTURE_NAMED_BLOCKS Identifier has a Name.
                if is_repeated_block_type == 'NAMED':
                    if len(orig_line) <= cur_indent + 1:
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'STRUCTURE_NAMED_BLOCKS ERROR: IDENTIFIER line.',
                            '',
                            '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                            '       `STRUCTURE_NAMED_BLOCKS` item line MUST have a name.',
                        ])
                    elif orig_line[cur_indent + 1] != LCONF_SPACE or orig_line[cur_indent + 2] == LCONF_SPACE:
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'STRUCTURE_NAMED_BLOCKS ERROR: IDENTIFIER line.',
                            '',
                            '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                            '    There MUST be ONE SPACE after the STRUCTURE_SINGLE_BLOCK_IDENTIFIER <{}>.'.format(
                                STRUCTURE_SINGLE_BLOCK_IDENTIFIER),
                        ])
                elif is_repeated_block_type == 'UNNAMED':
                    if len(orig_line) > cur_indent + 1:
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'STRUCTURE_UNNAMED_BLOCKS ERROR: IDENTIFIER line.',
                            '',
                            '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                            '       `STRUCTURE_UNNAMED_BLOCKS` item line MUST NOT have a name.',
                        ])
                else:
                    raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                        'STRUCTURE_BLOCKS ERROR: WRONG Blocks type.',
                        '',
                        '    orig_stack_situation: <{}>'.format(orig_stack_situation),
                        '       `STRUCTURE_BLOCKS` Expected a: NAMED or UNNAMED is_repeated_block_type.',
                        '       Got: <{}>'.format(is_repeated_block_type),
                    ])

                # Check STRUCTURE_BLOCKS: Item Empty STRUCTURE_SINGLE_BLOCK
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
                # STRUCTURE_BLOCKS: EMPTY BLK-Item (STRUCTURE_SINGLE_BLOCK):  No need to adjust the stack for this
                else:
                    # strictly speaking this is not needed
                    is_repeated_block_type == 'EMPTY'


            # STRUCTURE_SINGLE_BLOCK: no need to do anything here: orig_stack_situation == is_single_block

            # Root: check any new situation: no need to do anything here: orig_stack_situation == is_root

            # ====  ==== ==== check new orig_stack_situation ====  ==== ====   #
            else:
                # STRUCTURE_LIST_IDENTIFIER
                if orig_line[cur_indent] == STRUCTURE_LIST_IDENTIFIER:
                    if orig_line[cur_indent + 1] != LCONF_SPACE or orig_line[cur_indent + 2] == LCONF_SPACE:
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'STRUCTURE_LIST_IDENTIFIER ERROR.',
                            '',
                            '    There MUST be ONE SPACE before the List LCONF-Key-Name.',
                        ])

                    # Compact_STRUCTURE_LIST
                    if LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        # Validate: LCONF_KEY_VALUE_SEPARATOR
                        if ' :: ' not in orig_line or '  ::' in orig_line or '::  ' in orig_line:
                            raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                                'Compact_STRUCTURE_LIST: KEY-VALUE-SEPARATOR ERROR: expected < :: >',
                            ])
                    # General STRUCTURE_LIST
                    else:
                        # Check STRUCTURE_LIST: Item Empty STRUCTURE_LIST
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
                        # else: STRUCTURE_LIST: EMPTY:  No need to adjust the stack for this

                # STRUCTURE_TABLE_IDENTIFIER
                elif orig_line[cur_indent] == STRUCTURE_TABLE_IDENTIFIER:
                    if orig_line[cur_indent + 1] != LCONF_SPACE or orig_line[cur_indent + 2] == LCONF_SPACE:
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'STRUCTURE_TABLE_IDENTIFIER ERROR.',
                            '',
                            '    There MUST be ONE SPACE before the Table LCONF-Key-Name.',
                        ])
                    elif orig_line[-1] == STRUCTURE_TABLE_VALUE_SEPARATOR:
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'STRUCTURE_TABLE_IDENTIFIER line MUST NOT end with a STRUCTURE_TABLE_VALUE_SEPARATOR.',
                        ])
                    elif LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'STRUCTURE_TABLE_IDENTIFIER lines MUST NOT contain LCONF_KEY_VALUE_SEPARATORs.',
                        ])

                    # Check STRUCTURE_TABLE: Empty (no Row lines)
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
                        #    Number of STRUCTURE_TABLE_VALUE_SEPARATOR in table rows: will be based on the first row
                        #    At least 2
                        table_rows_expected_pipes = next_line.count(STRUCTURE_TABLE_VALUE_SEPARATOR)
                        if table_rows_expected_pipes < 2:
                            raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                                'STRUCTURE_TABLE ITEM Line (Row).',
                                '    Number of expected `STRUCTURE_TABLE_VALUE_SEPARATOR` must be at least 2.',
                                '    Counted `Vertical-Line`: <{}>'.format(
                                    orig_line.count(STRUCTURE_TABLE_VALUE_SEPARATOR)),
                                '',
                                'next_line: <{}>'.format(next_line),
                                '',
                                'orig_line: <{}>'.format(orig_line)
                            ])
                    # else: STRUCTURE_TABLE: EMPTY:  No need to adjust the stack for this

                # `STRUCTURE_SINGLE_BLOCK_IDENTIFIER`: These can only be Named STRUCTURE_SINGLE_BLOCKs
                elif orig_line[cur_indent] == STRUCTURE_SINGLE_BLOCK_IDENTIFIER:
                    if orig_line[cur_indent + 1] != LCONF_SPACE or orig_line[cur_indent + 2] == LCONF_SPACE:
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'There MUST be ONE SPACE before the SINGLE_BLOCK name.',
                        ])
                    elif LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'STRUCTURE_SINGLE_BLOCK_IDENTIFIER lines MUST NOT contain LCONF_KEY_VALUE_SEPARATORs.',
                        ])

                    # Check STRUCTURE_SINGLE_BLOCK: Empty
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
                    # else: STRUCTURE_SINGLE_BLOCK: EMPTY:  No need to adjust the stack for this

                # `STRUCTURE_BLOCKS_IDENTIFIER`
                elif orig_line[cur_indent] == STRUCTURE_BLOCKS_IDENTIFIER:
                    if orig_line[cur_indent + 1] != LCONF_SPACE or orig_line[cur_indent + 2] == LCONF_SPACE:
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'There MUST be ONE SPACE before the STRUCTURE_BLOCKS_IDENTIFIER name.',
                        ])
                    elif LCONF_KEY_VALUE_SEPARATOR in orig_line:
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'STRUCTURE_BLOCKS_IDENTIFIER lines MUST NOT contain LCONF_KEY_VALUE_SEPARATORs.',
                        ])


                    # Check STRUCTURE_BLOCKS: Empty
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

                # `STRUCTURE_PAIR:  we checked already for: Compact_STRUCTURE_LIST
                elif LCONF_KEY_VALUE_SEPARATOR in orig_line:
                    # Validate: LCONF_KEY_VALUE_SEPARATOR
                    if ('  ::' in orig_line or '::  ' in orig_line or
                        (' :: ' not in orig_line and orig_line[-3:] != ' ::')
                        ):
                        raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                            'LCONF_KEY_VALUE_SEPARATOR < :: > ERROR:',
                        ])
                # WRONG
                else:
                    raise SectionErr('validate_one_section_schema', section_format, section_name, orig_line, [
                        'SOMETHING Wrong with this line: maybe indentation, wrong type ..',
                    ])
            prev_indent = cur_indent
    return True


# =====================================================================================================================
def TOOD_deletelater():
    print("\n\nTOOD_deletelater\n\n")
    path_to_lconf_file = path_join(path_dirname(path_abspath(__file__)), "../lconf-examples/test.lconfsd")
    with open(path_to_lconf_file, 'r') as io:
        lconf_content = io.read()
    #print("\n\n", lconf_content, "\n\n")

    # for idx, section_text in enumerate(extract_sections(lconf_content)):
    #     print("\n\nSection: {} =====\n\n".format(idx), section_text, "\n\n")
    #     #result_validation = validate_one_section_fast(section_text)
    #     #print("\nresult_validation: ", result_validation)
    #
    #     result_validation_schema = validate_one_section_schema(section_text)
    #     print("\nresult_validation_schema: ", result_validation_schema)



    #     section_lines, section_indentation_number, section_format, section_name = section_splitlines(section_text)
    #     prepared_lines = prepare_section_lines(section_lines, section_indentation_number, section_format, section_name)
    #
    #
    #     for line in prepared_lines:
    #         print(line)

#     section_text = """___SECTION :: 4 :: LCONF :: Own Test Section
#
# # OWN COMMENT
# key1value_pair_name :: FRED
# key2value_pair_age :: 17
# ___END"""
#     validate_one_section_fast(section_text)

    sectionschema_text = """___SECTION :: 4 :: STRICT :: Team ranking
. Ranking | STRUCTURE_LIST
    ITEM :: OPTIONAL | TYPE_STRING
___END"""

    result_validation_schema = validate_one_section_schema(sectionschema_text)
    print("\nresult_validation_schema: ", result_validation_schema)


if __name__ == '__main__':

    TOOD_deletelater()
