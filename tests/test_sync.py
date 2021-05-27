from unittest import (
    TestCase,
    mock
)
from argparse import Namespace
from cdcagg_client import sync


class TestConfigure(TestCase):

    @mock.patch.object(sync.conf, 'get_conf')
    @mock.patch.object(sync.conf, 'get_package')
    @mock.patch.object(sync.conf, 'add_loglevel_arg')
    @mock.patch.object(sync.conf, 'add')
    @mock.patch.object(sync.conf, 'load')
    def test_calls_conf_load(self, mock_load, mock_add, mock_add_loglevel_arg, mock_get_package, mock_get_conf):
        mock_get_package.return_value = 'cdcagg_client'
        mock_get_conf.return_value = Namespace(loglevel='INFO')
        sync.configure()
