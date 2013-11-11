# -*- coding: utf-8 -*-
import ConfigParser
import unittest

from conf_d import Configuration

class TestConfigParser(ConfigParser.ConfigParser):
    def read(self, path):
        raise NotImplementedError('Catch this')

class ConfigurationTests(unittest.TestCase):

    def test_invalid_path(self):
        conf = Configuration(
            name='invalid_path',
            path='/dev/null',
            parse=False
        )
        self.assertRaises(IOError, lambda: conf._parse_section(path=''))
        self.assertRaises(IOError, lambda: conf._parse_section(path=None))
        self.assertRaises(IOError, lambda: conf._parse_section(path='.'))
        self.assertRaises(IOError, lambda: conf._parse_section(path='/non-existent/path'))

    def test_parse(self):
        conf = Configuration(
            name='invalid_path',
            path='/dev/null',
            parse=False
        )

        expected = {}
        actual = conf._parse_section(path='./data/empty.ini')
        self.assertEqual(expected, actual)

        expected = {'section': {'key': 'value'}}
        actual = conf._parse_section(path='./data/single_section.ini')
        self.assertEqual(expected, actual)

        expected = {'section': {'key': 'value', 'key_two': 'other_value'}}
        actual = conf._parse_section(path='./data/single_section.ini', defaults={'key_two': 'other_value'})
        self.assertEqual(expected, actual)

        expected = {'section': {'key': 'value', 'key_two': 'other_value'}}
        actual = conf._parse_section(path='./data/single_section.ini', defaults={'key_two': 'other_value'}, only_section='section')
        self.assertEqual(expected, actual)

        expected = {}
        actual = conf._parse_section(path='./data/single_section.ini', defaults={'key_two': 'other_value'}, remove_section='section')
        self.assertEqual(expected, actual)

        expected = {
            'derp': {'cats': '1', 'expected': 'the spanish inquisition', 'no': 'sleep', 'til': 'brooklyn'},
            'multiple_sections': {'cats': '1', 'expected': 'the spanish inquisition', 'no': 'one'},
            'section': {'cats': '1', 'expected': 'the spanish inquisition', 'key': 'value', 'no': 'one'}
        }
        actual = conf._parse_section(path='./data/multiple_sections.ini', defaults={
            'no': 'one',
            'expected': 'the spanish inquisition',
            'cats': '1',
        })
        self.assertEqual(expected, actual)

        expected = {
            'multiple_sections': {'cats': '1', 'expected': 'the spanish inquisition', 'no': 'one'},
        }
        actual = conf._parse_section(path='./data/multiple_sections.ini', only_section='multiple_sections', defaults={
            'no': 'one',
            'expected': 'the spanish inquisition',
            'cats': '1',
        })
        self.assertEqual(expected, actual)

        expected = {
            'multiple_sections': {'cats': '1', 'expected': 'the spanish inquisition', 'no': 'one'},
            'section': {'cats': '1', 'expected': 'the spanish inquisition', 'key': 'value', 'no': 'one'}
        }
        actual = conf._parse_section(path='./data/multiple_sections.ini', remove_section='derp', defaults={
            'no': 'one',
            'expected': 'the spanish inquisition',
            'cats': '1',
        })
        self.assertEqual(expected, actual)

    def test_get(self):
        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
        )

        self.assertEqual({}, conf.get('multiple_sections'))
        self.assertEqual({'til': 'brooklyn', 'no': 'sleep'}, conf.get('derp'))
        self.assertEqual('brooklyn', conf.get('derp', 'til'))
        self.assertEqual(None, conf.get('derp', 'missing_key'))
        self.assertEqual('1', conf.get('derp', 'missing_key_with_default', '1'))

    def test_has_section(self):
        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
        )
        self.assertEqual(True, conf.has('multiple_sections'))
        self.assertEqual(True, conf.has('derp'))
        self.assertEqual(True, conf.has('derp', 'no'))

    def test_defaults(self):
        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            main_defaults={'main_key': 'main_value'}
        )

        self.assertEqual({'main_key': 'main_value'}, conf.get('multiple_sections'))
        self.assertEqual({'til': 'brooklyn', 'no': 'sleep'}, conf.get('derp'))
        self.assertEqual('main_value', conf.get('multiple_sections', 'main_key'))
        self.assertEqual('brooklyn', conf.get('derp', 'til'))
        self.assertEqual(None, conf.get('derp', 'missing_key'))
        self.assertEqual(None, conf.get('derp', 'main_key'))
        self.assertEqual('1', conf.get('derp', 'missing_key_with_default', '1'))

        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            section_defaults={'section_key': 'section_value'}
        )

        self.assertEqual({}, conf.get('multiple_sections'))
        self.assertEqual({'no': 'sleep', 'section_key': 'section_value', 'til': 'brooklyn'}, conf.get('derp'))
        self.assertEqual(None, conf.get('multiple_sections', 'main_key'))
        self.assertEqual('brooklyn', conf.get('derp', 'til'))
        self.assertEqual(None, conf.get('derp', 'missing_key'))
        self.assertEqual(None, conf.get('derp', 'main_key'))
        self.assertEqual('1', conf.get('derp', 'missing_key_with_default', '1'))
        self.assertEqual('section_value', conf.get('derp', 'section_key'))
        self.assertEqual(None, conf.get('multiple_sections', 'section_key'))

        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            main_defaults={'main_key': 'main_value'},
            section_defaults={'section_key': 'section_value'}
        )

        self.assertEqual({'main_key': 'main_value'}, conf.get('multiple_sections'))
        self.assertEqual({'no': 'sleep', 'section_key': 'section_value', 'til': 'brooklyn'}, conf.get('derp'))
        self.assertEqual('brooklyn', conf.get('derp', 'til'))
        self.assertEqual(None, conf.get('derp', 'missing_key'))
        self.assertEqual(None, conf.get('derp', 'main_key'))
        self.assertEqual('1', conf.get('derp', 'missing_key_with_default', '1'))
        self.assertEqual('section_value', conf.get('derp', 'section_key'))
        self.assertEqual(None, conf.get('multiple_sections', 'section_key'))

    def test_raw(self):
        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            main_defaults={'main_key': 'main_value'},
            section_defaults={'section_key': 'section_value'}
        )
        self.assertEqual({'main_key': 'main_value'}, conf.raw('multiple_sections'))
        self.assertEqual({'key': 'value', 'section_key': 'section_value'}, conf.raw('section'))
        self.assertEqual({'no': 'sleep', 'section_key': 'section_value', 'til': 'brooklyn'}, conf.raw('derp'))

        expected = {
            'multiple_sections': {'main_key': 'main_value'},
            'sections': {
                'derp': {'no': 'sleep', 'section_key': 'section_value', 'til': 'brooklyn'},
                'section': {'key': 'value', 'section_key': 'section_value'}
            }
        }
        self.assertEqual(expected, conf.raw())

    def test_confd(self):
        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            confd_path='./data/conf.d',
            main_defaults={'main_key': 'main_value'}
        )

        self.assertEqual({'main_key': 'main_value'}, conf.get('multiple_sections'))
        self.assertEqual({'til': 'brooklyn', 'no': 'sleep'}, conf.get('derp'))
        self.assertEqual('main_value', conf.get('multiple_sections', 'main_key'))
        self.assertEqual('brooklyn', conf.get('derp', 'til'))
        self.assertEqual(None, conf.get('derp', 'missing_key'))
        self.assertEqual(None, conf.get('derp', 'main_key'))
        self.assertEqual('1', conf.get('derp', 'missing_key_with_default', '1'))

        expected = {
            'multiple_sections': {'main_key': 'main_value'},
            'sections': {
                'another/conf': {'sleep': '1', 'wait': '15'},
                'derp': {'no': 'sleep', 'til': 'brooklyn'},
                'section': {'key': 'value'},
                'test': {'conf': 'path/to/another/conf', 'sleep': '15'}
            }
        }
        self.assertEqual(expected, conf.raw())

        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            confd_path='./data/conf.d',
            section_defaults={'sleep': '2', 'wait': '30'}
        )

        self.assertEqual({}, conf.get('multiple_sections'))
        self.assertEqual({'no': 'sleep', 'sleep': '2', 'til': 'brooklyn', 'wait': '30'}, conf.get('derp'))
        self.assertEqual(None, conf.get('multiple_sections', 'main_key'))
        self.assertEqual('brooklyn', conf.get('derp', 'til'))
        self.assertEqual(None, conf.get('derp', 'missing_key'))
        self.assertEqual(None, conf.get('derp', 'main_key'))
        self.assertEqual('1', conf.get('derp', 'missing_key_with_default', '1'))

        expected = {
            'multiple_sections': {},
            'sections': {
                'another/conf': {'sleep': '1', 'wait': '15'},
                'derp': {'no': 'sleep', 'sleep': '2', 'til': 'brooklyn', 'wait': '30'},
                'section': {'key': 'value', 'sleep': '2', 'wait': '30'},
                'test': {'conf': 'path/to/another/conf', 'sleep': '15', 'wait': '30'}
            }
        }
        self.assertEqual(expected, conf.raw())

        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            confd_path='./data/conf.d',
            main_defaults={'main_key': 'main_value'},
            section_defaults={'sleep': '2', 'wait': '30'}
        )

        self.assertEqual({'main_key': 'main_value'}, conf.get('multiple_sections'))
        self.assertEqual({'no': 'sleep', 'sleep': '2', 'til': 'brooklyn', 'wait': '30'}, conf.get('derp'))
        self.assertEqual('main_value', conf.get('multiple_sections', 'main_key'))
        self.assertEqual('brooklyn', conf.get('derp', 'til'))
        self.assertEqual(None, conf.get('derp', 'missing_key'))
        self.assertEqual(None, conf.get('derp', 'main_key'))
        self.assertEqual('1', conf.get('derp', 'missing_key_with_default', '1'))

        expected = {
            'multiple_sections': {'main_key': 'main_value'},
            'sections': {
                'another/conf': {'sleep': '1', 'wait': '15'},
                'derp': {'no': 'sleep', 'sleep': '2', 'til': 'brooklyn', 'wait': '30'},
                'section': {'key': 'value', 'sleep': '2', 'wait': '30'},
                'test': {'conf': 'path/to/another/conf', 'sleep': '15', 'wait': '30'}
            }
        }
        self.assertEqual(expected, conf.raw())

        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            confd_path='./data/conf.d',
            conf_ext='conf',
            main_defaults={'main_key': 'main_value'},
            section_defaults={'sleep': '2', 'wait': '30'}
        )

        self.assertEqual({'main_key': 'main_value'}, conf.get('multiple_sections'))
        self.assertEqual({'no': 'sleep', 'sleep': '2', 'til': 'brooklyn', 'wait': '30'}, conf.get('derp'))
        self.assertEqual('main_value', conf.get('multiple_sections', 'main_key'))
        self.assertEqual('brooklyn', conf.get('derp', 'til'))
        self.assertEqual(None, conf.get('derp', 'missing_key'))
        self.assertEqual(None, conf.get('derp', 'main_key'))
        self.assertEqual('1', conf.get('derp', 'missing_key_with_default', '1'))

        expected = {
            'multiple_sections': {'main_key': 'main_value'},
            'sections': {
                'derp': {'no': 'sleep', 'sleep': '2', 'til': 'brooklyn', 'wait': '30'},
                'section': {'key': 'value', 'sleep': '2', 'wait': '30'},
            }
        }
        self.assertEqual(expected, conf.raw())

        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            confd_path='./data/conf.d',
            conf_ext='.conf',
            main_defaults={'main_key': 'main_value'},
            section_defaults={'sleep': '2', 'wait': '30'}
        )

        self.assertEqual({'main_key': 'main_value'}, conf.get('multiple_sections'))
        self.assertEqual({'no': 'sleep', 'sleep': '2', 'til': 'brooklyn', 'wait': '30'}, conf.get('derp'))
        self.assertEqual('main_value', conf.get('multiple_sections', 'main_key'))
        self.assertEqual('brooklyn', conf.get('derp', 'til'))
        self.assertEqual(None, conf.get('derp', 'missing_key'))
        self.assertEqual(None, conf.get('derp', 'main_key'))
        self.assertEqual('1', conf.get('derp', 'missing_key_with_default', '1'))

        expected = {
            'multiple_sections': {'main_key': 'main_value'},
            'sections': {
                'derp': {'no': 'sleep', 'sleep': '2', 'til': 'brooklyn', 'wait': '30'},
                'section': {'key': 'value', 'sleep': '2', 'wait': '30'},
            }
        }
        self.assertEqual(expected, conf.raw())

    def test_parser(self):
        def safe_cast(val):
            try:
                return int(val)
            except ValueError:
                return val

        def all_as_bool(config):
            for key in config:
                config[key] = bool(config[key])
            return config

        def all_as_int(config):
            for key in config:
                try:
                    config[key] = int(config[key])
                except ValueError:
                    pass

            return config

        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            confd_path='./data/conf.d',
            main_defaults={'main_key': 'main_value'},
            section_defaults={'sleep': '2', 'wait': '30'},
            main_parser=all_as_bool
        )

        self.assertEqual({'main_key': True}, conf.get('multiple_sections'))
        self.assertEqual(True, conf.get('multiple_sections', 'main_key'))
        self.assertEqual('1', conf.get('another/conf', 'sleep'))

        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            confd_path='./data/conf.d',
            main_defaults={'main_key': 'main_value'},
            section_defaults={'sleep': '2', 'wait': '30'},
            section_parser=all_as_bool
        )

        self.assertEqual({'main_key': 'main_value'}, conf.get('multiple_sections'))
        self.assertEqual('main_value', conf.get('multiple_sections', 'main_key'))
        self.assertEqual(1, conf.get('another/conf', 'sleep'))

        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            confd_path='./data/conf.d',
            main_defaults={'main_key': 'main_value'},
            section_defaults={'sleep': '2', 'wait': '30'},
            main_parser=all_as_bool,
            section_parser=all_as_int
        )

        self.assertEqual({'main_key': True}, conf.get('multiple_sections'))
        self.assertEqual(True, conf.get('multiple_sections', 'main_key'))
        self.assertEqual(None, conf.get('derp', 'missing_key'))
        self.assertEqual(1, conf.get('another/conf', 'sleep'))

    def test_custom_config_parser(self):
        conf = Configuration(
            name='multiple_sections',
            path='./data/multiple_sections.ini',
            config_parser=TestConfigParser,
            parse=False
        )

        self.assertRaises(NotImplementedError, lambda: conf._parse_section(path='./data/multiple_sections.ini'))

    def test_readme(self):
        def digitize(config):
            for key in config:
                if not config[key].isdigit():
                    try:
                        config[key] = float(config[key])
                    except ValueError:
                        pass
                else:
                    try:
                        config[key] = int(config[key])
                    except ValueError:
                        pass

            return config

        conf = Configuration(
            name='derp',
            path='./data/conf',
            main_defaults={
                'no': 'one',
                'expected': 'the spanish inquisition',
                'cats': '1',
            },
            section_parser=digitize
        )
        expected = {
            'sections': {'herp': {'sleep': 1, 'wait': 5.0, 'timeout': 'seventy'}},
            'derp': {'expected': 'the spanish inquisition', 'til': 'brooklyn', 'cats': '1', 'no': 'sleep'}
        }
        self.assertEqual(expected, conf.raw())

        actual = conf.get(section='derp', key='no', default="jumping")
        self.assertEqual('sleep', actual)

        actual = conf.get(section='derp', key='til')
        self.assertEqual('brooklyn', actual)

        actual = conf.get(section='derp', key='cats')
        self.assertEqual('1', actual)

        actual = conf.get(section='derp', key='dogs')
        self.assertEqual(None, actual)

        actual = conf.get(section='herp', key='sleep')
        self.assertEqual(1, actual)

        actual = conf.get(section='herp', key='wait')
        self.assertEqual(5.0, actual)

        actual = conf.get(section='herp', key='timeout')
        self.assertEqual('seventy', actual)

        actual = conf.has(section='derp')
        self.assertEqual(True, actual)

        actual = conf.has(section='derp', key='no')
        self.assertEqual(True, actual)

        expected = {
            'sections': {
                'herp': {
                    'sleep': 1,
                    'wait': 5.0,
                    'timeout': 'seventy'
                }
            },
            'derp': {
                'expected': 'the spanish inquisition',
                'til': 'brooklyn',
                'cats': '1',
                'no': 'sleep'
            }
        }
        self.assertEqual(expected, conf.raw())
