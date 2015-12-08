# -------------------------------------------------------------------------------
# Name:        tools
# Purpose:     To provide miscellaneous functionality
#
# Author:      David Moses
#
# Created:     Dec 01, 2014 
# Copyright:   (c) David Moses 2014
#-------------------------------------------------------------------------------

def equal(a, b):
    """
    A custom object comparison method.
    """

    try:
        return all(a == b)
    except TypeError:
        return a == b
