"""
### PyLCONF.lconf_classes

#### Overview

Most of the code in `lconf_classes.py` is based on the [ReOBJ package](<https://github.com/peter1000/ReOBJ)
by the same author: `The BSD 3-Clause License`.

These Classes are used for the final default/parsed LCONF object.

#### Features

`LconfRoot`: LCONF-Section Main/Root obj class (dict).
"""

# =================================================================================================================== #

def _deactivated(*args, **kwargs):
    raise MethodDeactivatedErr()


# === === === `LCONF-Template-Structure` Classes === === === #
#
# | **Name**             | **Definition**                                                              |
# |:---------------------|:----------------------------------------------------------------------------|
# | LCONF-Key-Value-Pair | Associates a LCONF-Key-Name with one data value.                            |
# | LCONF-Table          | Associates a LCONF-Key-Name with ordered tabular-data (columns and rows).   |
# | LCONF-List           | Associates a LCONF-Key-Name with an ordered sequence (list) of data values. |
# | LCONF-Single-Block   | A collection of any of the five LCONF-Structures.                           |
# | LCONF-Repeated-Block | A collection of repeated LCONF-Single-Blocks.                               |

class LconfRoot(dict):
    """
    #### structure_classes.LconfRoot

    LCONF-Section Main/Root obj class (dict).

    `LconfRoot(default_indentation_per_level, default_section_name, key_value_list)`

    **Parameters:**

    * `key_value_list`: (list) of tuples: FORMAT:
        ('Key-Name', 'Default-Value', Value-Type, Item-Requirement-Option, Empty-Replacement-Value)

    **Has Additional Attributes:**

    * `data`: (dict) key - values
    * `key_order_list`: (list) the keys in order as initialized
    * `section_name`: (str) defaults to 'missing section name'
    * `indentation_per_level`: (int) defaults to -1
    * `is_parsed`: (bool) defaults to False
    * `has_comments`: (bool) defaults to False

        * this must be set to True: if it is init with comments: this helps that one does not need to check for
            comments later on
    """

    def __init__(self, data, key_order_list):
        dict.__init__(self, data)
        self.__dict__['key_order'] = key_order_list
        self.__dict__['section_name'] = 'missing section name'
        self.__dict__['indentation_per_level'] = -1
        self.__dict__['is_parsed'] = False
        self.__dict__['has_comments'] = False

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
    #__setitem__ = _deactivated
    __setattr__ = _deactivated
    __reduce__ = _deactivated
    setdefault = _deactivated
    pop = _deactivated
    popitem = _deactivated
    update = _deactivated
    get = _deactivated
    fromkeys = _deactivated
