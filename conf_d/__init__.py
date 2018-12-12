# -*- coding: utf-8 -*-
import os

from conf_d.compat import ConfigParser

__version__ = '0.1.0'


class Configuration():

    def __init__(self, name, path, parse=True, confd_path=None, conf_ext=None, main_defaults={}, section_defaults={}, main_parser=None, section_parser=None, path_from_main=None, config_parser=ConfigParser):
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
        self._config_parser = config_parser

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
        config_parser = self._config_parser(defaults)

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
