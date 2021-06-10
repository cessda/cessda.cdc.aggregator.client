import os.path
from unittest import (
    TestCase,
    mock
)
from argparse import Namespace
from kuha_common.testing.testcases import KuhaUnitTestCase
from kuha_common.document_store.constants import (
    REC_STATUS_CREATED,
    REC_STATUS_DELETED
)
from cdcagg_common.records import Study
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


class TestStudyMethods(KuhaUnitTestCase):

    def setUp(self):
        super().setUp()
        self.studymeths = sync.StudyMethods(mock.Mock())

    @mock.patch.object(sync.kuha_client, 'send_update_record_request')
    def test_update_record_with_matching_records(self, mock_send):
        """If records match and old record is not deleted, do nothing."""
        old = Study()
        new = Study(old.export_dict())
        # Call
        self._loop.run_until_complete(self.await_and_store_result(
            self.studymeths.update_record(new, old)))
        # assert
        mock_send.assert_not_called()
        self.assertEqual(self._stored_result, False)

    @mock.patch.object(sync.kuha_client, 'send_update_record_request')
    def test_update_record_with_differing_records(self, mock_send):
        """If records don't match, send the new one to docstore."""
        old = Study()
        old.add_study_number('study_1')
        old.add_abstract('some abstract', 'en')
        old._id.set_value('some-id')
        new = Study()
        new.add_study_number('study_1')
        new.add_abstract('another abstract', 'en')
        new._provenance.add_value('some harvestdate')
        # Call
        self._loop.run_until_complete(self.await_and_store_result(
            self.studymeths.update_record(new, old)))
        # Assert
        mock_send.assert_called_once_with(
            new.collection, new.export_dict(include_provenance=True, include_metadata=False, include_id=False),
            'some-id')
        self.assertEqual(self._stored_result, True)

    @mock.patch.object(sync.kuha_client, 'send_update_record_request')
    def test_update_record_matching_records_old_record_is_deleted(self, mock_send):
        """If records match, but older is deleted, change the metadata accordingly and send to docstore"""
        old = Study()
        old.add_study_number('study_1')
        old.add_abstract('some abstract', 'en')
        old._id.set_value('some-id')
        new = Study(old.export_dict())
        old.set_created('2000-01-01T00:00:00Z')
        old.set_deleted()
        old.set_status(REC_STATUS_DELETED)
        exp_dict = old.export_dict(include_metadata=True, include_id=False)
        exp_dict['_metadata']['status'] = REC_STATUS_CREATED
        exp_dict['_metadata']['deleted'] = None
        # Call
        self._loop.run_until_complete(self.await_and_store_result(
            self.studymeths.update_record(new, old)))
        # Assert
        mock_send.assert_called_once_with(new.collection, exp_dict, 'some-id')
        self.assertEqual(self._stored_result, True)


def _testdata_path(path=''):
    if path:
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testdata', path)
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testdata')


class TestIntegration(KuhaUnitTestCase):
    """Test from cli to http requests"""

    def setUp(self):
        super().setUp()
        self._mock_query_single = self.init_patcher(mock.patch.object(sync.QueryController, 'query_single'))
        self._mock_query_distinct = self.init_patcher(mock.patch.object(sync.QueryController, 'query_distinct'))
        self._mock_send_delete_record_request = self.init_patcher(
            mock.patch.object(sync.kuha_client, 'send_delete_record_request'))
        self._mock_send_update_record_request = self.init_patcher(
            mock.patch.object(sync.kuha_client, 'send_update_record_request'))
        self._mock_send_create_record_request = self.init_patcher(mock.patch('kuha_client.send_create_record_request'))
        self._mock_configure = self.init_patcher(mock.patch.object(sync, 'configure'))

    def test_minimal_ddi122(self):
        self._mock_query_single.return_value = None
        self._mock_configure.return_value = Namespace(paths=[_testdata_path('minimal_ddi122.xml')],
                                                      no_remove=False,
                                                      file_cache='')
        # Call
        sync.cli()
        # Assert
        calls = self._mock_send_create_record_request.call_args_list
        self.assertEqual(len(calls), 1)
        cargs, ckwargs = calls.pop()
        self.assertEqual(ckwargs, {})
        self.assertEqual(len(cargs), 2)
        coll, rec_dict = cargs
        self.assertEqual(coll, Study.get_collection())
        self.assertEqual(rec_dict['study_number'], 'study_1')
        self.assertEqual(rec_dict['study_titles'][0]['study_title'], 'some study')
