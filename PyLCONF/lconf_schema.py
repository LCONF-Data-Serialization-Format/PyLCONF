"""
### PyLCONF.lconf_schema

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



# =====================================================================================================================
def TOOD_deletelater():
    print("\n\nTOOD_deletelater\n\n")


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
