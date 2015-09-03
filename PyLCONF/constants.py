### Single Characters
LCONF_SPACE          = '\u0020'
LCONF_NUMBER_SIGN    = '\u0023'
LCONF_ASTERISK       = '\u002a'
LCONF_PLUS           = '\u002b'
LCONF_COMMA          = '\u002c'
LCONF_MINUS          = '\u002d'
LCONF_PERIOD         = '\u002e'
LCONF_SLASH          = '\u002f'
LCONF_COLON          = '\u003a'
LCONF_EQUALS_SIGN    = '\u003d'
LCONF_UNDERSCORE     = '\u005f'
LCONF_VERTICAL_LINE  = '\u007c'

### Character Group
#
# LCONF_DIGITS:          DIGIT ZERO through DIGIT NINE                         | ASCII: 48 through 57
# LCONF_CAPITAL_LETTERS: LATIN CAPITAL LETTER A through LATIN CAPITAL LETTER Z | ASCII: 65 through 90
# LCONF_SMALL_LETTERS:   LATIN SMALL LETTER A through LATIN SMALL LETTER Z     | ASCII: 97 through 122
LCONF_DIGITS          = set(['\u0030', '\u0031', '\u0032', '\u0033', '\u0034',
                             '\u0035', '\u0036', '\u0037', '\u0038', '\u0039'])
LCONF_CAPITAL_LETTERS = set(['\u0041', '\u0042', '\u0043', '\u0044', '\u0045', '\u0046', '\u0047', '\u0048', '\u0049',
                             '\u004a', '\u004b', '\u004c', '\u004d', '\u004e', '\u004f', '\u0050', '\u0051', '\u0052',
                             '\u0053', '\u0054', '\u0055', '\u0056', '\u0057', '\u0058', '\u0059', '\u005a'])
LCONF_SMALL_LETTERS   = set(['\u0061', '\u0062', '\u0063', '\u0064', '\u0065', '\u0066', '\u0067', '\u0068', '\u0069',
                             '\u006a', '\u006b', '\u006c', '\u006d', '\u006e', '\u006f', '\u0070', '\u0071', '\u0072',
                             '\u0073', '\u0074', '\u0075', '\u0076', '\u0077', '\u0078', '\u0079', '\u007a'])

### Literal Name Tokens
LCONF_SECTION_START = "\u005f\u005f\u005f\u0053\u0045\u0043\u0054\u0049\u004f\u004e"        # `___SECTION`
LCONF_SECTION_END   = "\u005f\u005f\u005f\u0045\u004e\u0044"                                # `___END`
LCONF_TRUE          = "\u0074\u0072\u0075\u0065"                                            # `true`
LCONF_FALSE         = "\u0066\u0061\u006c\u0073\u0065"                                      # `false`
LCONF_VALUE_NOTSET  = "\u004e\u004f\u0054\u0053\u0045\u0054"                                # `NOTSET`
LCONF_FORCE         = "\u0046\u004f\u0052\u0043\u0045"                                      # `FORCE`

### Structural Tokens
LCONF_COMMENT_LINE_IDENTIFIER   = LCONF_NUMBER_SIGN
LCONF_KEY_VALUE_SEPARATOR       = LCONF_COLON * 2                    # DOUBLE LCONF_COLON `::`
LCONF_TABLE_IDENTIFIER          = LCONF_VERTICAL_LINE
LCONF_TABLE_VALUE_SEPARATOR     = LCONF_VERTICAL_LINE
LCONF_LIST_IDENTIFIER           = LCONF_MINUS
LCONF_LIST_VALUE_SEPARATOR      = LCONF_COMMA
LCONF_SINGLE_BLOCK_IDENTIFIER   = LCONF_PERIOD
LCONF_REPEATED_BLOCK_IDENTIFIER = LCONF_ASTERISK
LCONF_SINGLE_BLOCK_REUSE        = LCONF_EQUALS_SIGN * 2             # DOUBLE LCONF_EQUALS_SIGN  `==`

### Value Types
LCONF_Comment              = "LCONF_Comment"
LCONF_String               = "LCONF_String"
LCONF_Boolean              = "LCONF_Boolean"
LCONF_Integer              = "LCONF_Integer"
LCONF_Single_Block         = "LCONF_Single_Block"
LCONF_UnNamed_Single_Block = "LCONF_UnNamed_Single_Block"
LCONF_Repeated_Block       = "LCONF_Repeated_Block"

# =================================================================================================================== #

# LCONF-Integer: 64 bit (signed long) range expected (-9223372036854775808 to 9223372036854775807)
LCONF_INTEGER_LOWEST  = -9223372036854775808
LCONF_INTEGER_HIGHEST = +9223372036854775807

# LCONF-EMPTY-String: A sequence of zero Unicode characters.
LCONF_EMPTY_STRING = ""

LCONF_BLANK_COMMENT_LINE = LCONF_EMPTY_STRING

LCONF_DEFAULT_SINGLE_BLOCK = "LCONF_DEFAULT_SINGLE_BLOCK"
LCONF_EMPTY_REPEATED_BLOCK = "LCONF_EMPTY_REPEATED_BLOCK"

# LCONF-Section-Item-Requirement-Option
# * OPTIONAL
#
#     * Item is NOT REQUIRED be defined in a LCONF-Section
#     * Item COULD be defined but set `NOTSET`
#     * Item COULD be defined and set empty (which will overwrite any defaults)
#     * Item COULD be defined and have set a value in accordance to the expected LCONF-Value-Type
#
# * REQUIRED (this can also be an empty value)
#
#     * Item MUST be defined in a LCONF-Section and MUST NOT be set `NOTSET`
#     * Item MUST be defined and can be set empty (which will overwrite any defaults)
#     * Item MUST be defined and can set a value in accordance to the expected LCONF-Value-Type
#         (which will overwrite any defaults)
#
# * REQUIRED_NOT_EMPTY (this MUST NOT be an empty value)
#
#     * Item MUST be defined in a LCONF-Section and MUST NOT be set `NOTSET` and MUST NOT be set empty
#     * Item MUST be defined and MUST set a value in accordance to the expected LCONF-Value-Type
#
# * COMMENT_DUMMY (Dummy for LCONF-Default-Comment-Lines)

ITEM_OPTIONAL           = "ITEM_OPTIONAL"
ITEM_REQUIRED           = "ITEM_REQUIRED"
ITEM_REQUIRED_NOT_EMPTY = "ITEM_REQUIRED_NOT_EMPTY"

COMMENT_DUMMY = "#"  # used for Default-Comment-Lines: Item-Requirement-Option, Empty-Replacement-Value

# EMIT Default-Comment Options
EMIT_NO_COMMENTS          = "EMIT_NO_COMMENTS"           # NO Comments at all
EMIT_ONLY_MANUAL_COMMENTS = "EMIT_ONLY_MANUAL_COMMENTS"  # Only Manual Default Comments
EMIT_ALL_COMMENTS         = "EMIT_ALL_COMMENTS"          # Auto Comments and Manual Default Comments
