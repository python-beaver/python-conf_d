# -*- coding: utf-8 -*-
import ConfigParser
import os
import re

__version__ = '0.0.3'

class GlobSafeConfigParser(ConfigParser.RawConfigParser):

    OPTCRE = re.compile(
        r'(?P<option>[^:=\s][^:=]*)' # very permissive!
        r'\s*(?P<vi>[:=])\s*'        # any number of space/tab,
                                     # followed by separator
                                     # (either : or =), followed
                                     # by any # space/tab
        r'(?P<value>.*)$'            # everything up to eol
        )

    def _read(self, fp, fpname):
        """Parse a sectioned setup file.

        The sections in setup file contains a title line at the top,
        indicated by a name in square brackets (`[]'), plus key/value
        options lines, indicated by `name: value' format lines.
        Continuations are represented by an embedded newline then
        leading whitespace. Blank lines, lines beginning with a '#',
        and just about everything else are ignored.

        Copied from python 2.7 source and modified so that globs in
        sections work properly for beaver
        """
        cursect = None # None, or a dictionary
        optname = None
        lineno = 0
        e = None # None, or an exception
        while True:
            line = fp.readline()
            if not line:
                break
            lineno = lineno + 1
            # comment or blank line?
            if line.strip() == '' or line[0] in '#;':
                continue
            if line.split(None, 1)[0].lower() == 'rem' and line[0] in "rR":
                # no leading whitespace
                continue
            # continuation line?
            if line[0].isspace() and cursect is not None and optname:
                value = line.strip()
                if value:
                    cursect[optname] = "%s\n%s" % (cursect[optname], value)
            # a section header or option header?
            else:
                # is it a section header?
                try:
                  value = line[:line.index(';')].strip()
                except ValueError: #no semicolon so no comments to strip off
                  value = line.strip()

                if  value[0]=='[' and value[-1]==']' and len(value)>2:
                    sectname = value[1:-1]
                    if sectname in self._sections:
                        cursect = self._sections[sectname]
                    elif sectname == "DEFAULT":
                        cursect = self._defaults
                    else:
                        cursect = self._dict()
                        cursect['__name__'] = sectname
                        self._sections[sectname] = cursect
                    # So sections can't start with a continuation line
                    optname = None
                # no section header in the file?
                elif cursect is None:
                    raise MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                else:
                    mo = self.OPTCRE.match(line)
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        if vi in ('=', ':') and ';' in optval:
                            # ';' is a comment delimiter only if it follows
                            # a spacing character
                            pos = optval.find(';')
                            if pos != -1 and optval[pos-1].isspace():
                                optval = optval[:pos]
                        optval = optval.strip()
                        # allow empty values
                        if optval == '""':
                            optval = ''
                        optname = self.optionxform(optname.rstrip())
                        cursect[optname] = optval
                    else:
                        # a non-fatal parsing error occurred. set up the
                        # exception but keep going. the exception will be
                        # raised at the end of the file and will contain a
                        # list of all bogus lines
                        if not e:
                            e = ParsingError(fpname)
                        e.append(lineno, repr(line))
        # if any parsing errors occurred, raise an exception
        if e:
            raise e

class Configuration():

    def __init__(self, name, path, parse=True, confd_path=None, conf_ext=None, main_defaults={}, section_defaults={}, main_parser=None, section_parser=None, path_from_main=None):
        self._conf_ext = conf_ext
        self._config_sections = {}
        self._confd_path = confd_path
        self._path_from_main = path_from_main
        self._main_config = {}
        self._main_defaults = main_defaults
        self._main_parser = main_parser
        self._name = name
        self._path = path
        self._section_defaults = section_defaults
        self._section_parser = section_parser

        if self._conf_ext:
            self._conf_ext = '.' + conf_ext.strip(".")

        if parse:
            self.parse()

    def get(self, section, key=None, default=None):
        if section == self._name:
            if key is None:
                return self._main_config
            return self._main_config.get(key, default)

        if section in self._config_sections:
            if key is None:
                return self._config_sections[section]
            return self._config_sections[section].get(key, default)

        raise KeyError("Invalid section")

    def has(self, section, key=None):
        if section in self._config_sections:
            if key is None:
                return True

            return key in self._config_sections[section]

        if section == self._name:
            if key is None:
                return True

            return key in self._main_config

        return False

    def raw(self, section=None):
        if section:
            if not self.has(section):
                raise KeyError("Invalid section")

            if section == self._name:
                return self._main_config

            return self._config_sections[section]

        return {
            self._name: self._main_config,
            'sections': self._config_sections
        }

    def parse(self):
        configs = self._parse_section(path=self._path, defaults=self._main_defaults, parser=self._main_parser, only_section=self._name)
        self._main_config = configs.get(self._name)

        self._config_sections = self._parse_section(path=self._path, defaults=self._section_defaults, parser=self._section_parser, remove_section=self._name)

        if self._path_from_main:
            self._confd_path = self._main_config.get(self._path_from_main, self._confd_path)

        if self._confd_path:
            try:
                paths = os.listdir(self._confd_path)
            except OSError:
                paths = None

            if not paths:
                return

            for f in sorted(paths):
                path = os.path.realpath(os.path.join(self._confd_path, f))
                if not os.path.isfile(path):
                    continue

                if self._conf_ext and not path.endswith(self._conf_ext):
                    continue

                configs = self._parse_section(path=path, defaults=self._section_defaults, parser=self._section_parser, remove_section=self._name)
                self._config_sections.update(configs)

    def _parse_section(self, path, defaults={}, parser=None, only_section=None, remove_section=None):
        config_parser = GlobSafeConfigParser(defaults)

        if not path:
            raise IOError('No path specified: "%s"' % path)

        path = os.path.realpath(path)

        if len(config_parser.read(path)) != 1:
            raise IOError('Could not parse config file "%s"' % path)

        configs = {}
        for section in config_parser.sections():
            if remove_section and remove_section == section:
                continue

            if only_section and only_section != section:
                continue

            config = dict((x[0], x[1]) for x in config_parser.items(section))
            if hasattr(parser, '__call__'):
                config = parser(config)

            configs[section] = config

        if only_section and len(configs) == 0:
            if hasattr(parser, '__call__'):
                configs[only_section] = parser(defaults)
            else:
                configs[only_section] = defaults

        return configs
