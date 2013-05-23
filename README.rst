======
conf_d
======

read configuration files, conf.d style

Requirements
============

* Python 2.6+

Installation
============

Using PIP:

From Github::

    pip install git+git://github.com/josegonzalez/conf_d.git#egg=conf_d

From PyPI::

    pip install conf_d==0.0.3

Usage
=====

usage::

    # in your /etc/derp/conf file
    [derp]
    no: sleep
    til: brooklyn

    [herp]
    sleep: 1
    wait: 5.0
    timeout: seventy

    # From your fictional derp module
    from conf_d import Configuration

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

    # All defaults must be strings
    conf = Configuration(
        name="derp",
        path="/etc/derp/conf",
        main_defaults={
            "no": "one",
            "expected": "the spanish inquisition",
            "cats": "1",
        },
        section_parser=digitize
    )

    what_not_to_do = conf.get(section='derp', key='no', default="jumping")
    # "sleep"

    until_when = conf.get(section='derp', key='til')
    # "brooklyn"

    cats = conf.get(section='derp', key='cats')
    # "1"

    dogs = conf.get(section='derp', key='dogs')
    # None

    sleep = conf.get(section='herp', key='sleep')
    # 1

    wait = conf.get(section='herp', key='wait')
    # 5.0

    timeout = conf.get(section='herp', key='timeout')
    # "seventy"

    section_exists = conf.has(section='derp')
    # True

    section_exists = conf.has(section='derp', key='no')
    # True

    raw_data = conf.raw()
    # {
    #    'sections': {
    #       'herp': {
    #          'sleep': 1,
    #          'wait': 5.0,
    #          'timeout': 'seventy'
    #       }
    #    },
    #    'derp': {
    #       'expected': 'the spanish inquisition',
    #       'til': 'brooklyn',
    #       'cats': '1',
    #       'no': 'sleep'
    #    }
    # }
