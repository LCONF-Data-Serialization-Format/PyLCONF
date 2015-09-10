"""
### PyLCONF.lconf_schema

#### Overview

`validate_one_section_schema`: Validate one LCONF-Schema-Section raw string.
`validate_schemas_from_file`: Validates a LCONF-Schema-File containing one or more LCONF-Schema-Sections.
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
