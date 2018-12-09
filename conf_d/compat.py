# -*- coding: utf-8 -*-
from sys import version_info

if version_info[0] < 3:
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser
