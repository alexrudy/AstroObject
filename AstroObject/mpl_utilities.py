# -*- coding: utf-8 -*-
# 
#  mpl_utilities.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5-b2
# 


import re
from matplotlib.ticker import LogFormatter

class LogFormatterTeXExponent(LogFormatter, object):
    """Extends pylab.LogFormatter to use
    tex notation for tick labels."""

    def __init__(self, *args, **kwargs):
        super(LogFormatterTeXExponent,
              self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Wrap call to parent class with
        change to tex notation."""
        label = super(LogFormatterTeXExponent,
                      self).__call__(*args, **kwargs)
        label = re.sub(r'e(\S)0?(\d+)',
                       r'\\times 10^{\1\2}',
                       str(label))
        label = "$" + label + "$"
        return label
