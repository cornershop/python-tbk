from __future__ import unicode_literals

import os
try:
    from unittest import mock  # noqa
except ImportError:
    import mock  # noqa

import lxml.etree

HERE = os.path.abspath(os.path.dirname(__file__))
FIXTURES_DIR = os.path.join(HERE, 'fixtures')


def get_fixture_filepath(filename):
    return os.path.join(FIXTURES_DIR, filename)


def get_fixture_url(filename):
    return 'file://{}'.format(get_fixture_filepath(filename))


def get_fixture_data(filename):
    with open(get_fixture_filepath(filename), 'r') as file:
        return file.read()


def assert_equal_xml(first, second):
    first = lxml.etree.tostring(lxml.etree.fromstring(first))
    second = lxml.etree.tostring(lxml.etree.fromstring(second))
    assert first == second


def get_xml_envelope(filename):
    return lxml.etree.fromstring(get_fixture_data(filename).encode('utf-8'))
