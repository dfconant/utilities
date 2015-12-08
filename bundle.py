#-------------------------------------------------------------------------------
# Name:        Bundle
# Purpose:     To create a small light-weight object capable of storing
#              multiple attributes (similar to a dict in many ways)
#
# Author:      David Moses
#
# Created:     Jan 16, 2014
# Copyright:   (c) David Moses 2013
# References:  http://code.activestate.com/recipes/52308-the-simple-but-handy-
#              collector-of-a-bunch-of-named/?in=user-97991
#-------------------------------------------------------------------------------

import tools

class Bundle(object):
    __init__ = lambda self, **kwargs: setattr(self, '__dict__', kwargs)

    def __eq__(self, other):
        if not set(self.__dict__.keys()) == set(other.__dict__.keys()):
            return False
        return all([tools.equal(v, getattr(other, k))
                    for k, v in self.__dict__.items()])

#===============================================================================
#    End of class Bundle
#===============================================================================
