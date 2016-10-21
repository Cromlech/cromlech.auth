# -*- coding: utf-8 -*-
"""
Code forked from barrel
Copyright (C) 2006-2008 Luke Arno - http://lukearno.com/
Luke Arno can be found at http://lukearno.com/
"""

from .basic import BasicAuth


def decorize(middleware):
    """Return customizable middleware decorator factory.
    
    Returns a decorator factory function that will return
    decorators that apply the given middleware then assign
    any keyword args to corresponding attributes of the result.
    """
    classname = middleware.__class__
    def metadeco(config=None, *args, **kwargs):
        """Decorate with middleware then set attribs."""
        stringkwargs = ["%s=%s" % (key, repr(val)) 
                        for (key, val) in kwargs.iteritems()]
        def deco(app):
            """Decorated with middleware and attribs set."""
            newapp = middleware(app)
            for key, value in kwargs.iteritems():
                try:
                    setattr(newapp, key, value)
                except AttributeError:
                    pass
            return newapp
        deco.__doc__ = """Decorate given app with %s
        
        Sets attributes on the resulting object (if it can):
        
        %s
        """ % (middleware.__name__, "\n      ".join(stringkwargs))
        return deco
    metadeco.__doc__ = ("Create decorator that will use %s "
                        "with given attributes.") % classname
    return metadeco


basicauth = decorize(BasicAuth)
