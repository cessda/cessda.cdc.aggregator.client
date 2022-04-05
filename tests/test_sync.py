# Copyright CESSDA ERIC 2021
#
# Licensed under the EUPL, Version 1.2 (the "License"); you may not
# use this file except in compliance with the License.
# You may obtain a copy of the License at
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path
import tempfile
from unittest import mock
from argparse import Namespace
from kuha_common.testing.testcases import KuhaUnitTestCase
from kuha_common.document_store.constants import (
    REC_STATUS_CREATED,
    REC_STATUS_DELETED,
    MDB_NOT_EQUAL,
    MDB_ELEM_MATCH
)
from kuha_common.cli_setup import (
    MOD_DS_CLIENT,
    MOD_DS_QUERY,
    MOD_LOGGING
)
from cdcagg_common.records import Study
from cdcagg_client import sync


def _testdata_path(path=''):
    if path:
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testdata', path)
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testdata')


def settings(paths, no_remove=False, file_cache='', **kw):
    return Namespace(paths=paths,
                     no_remove=no_remove,
                     file_cache=file_cache,
                     print_configuration=kw.get('print_configuration', False),
                     fail_on_parse=kw.get('fail_on_parse', False))


class TestConfigure(KuhaUnitTestCase):

    def setUp(self):
        super().setUp()
        self._mock_conf = self.init_patcher(mock.patch.object(sync, 'conf'))
        self._mock_setup_common_modules = self.init_patcher(mock.patch.object(
            sync.cli_setup, 'setup_common_modules'))

    def test_calls_conf_load(self):
        sync.configure()
        self._mock_conf.load.assert_called_once_with('cdcagg_client.sync',
                                                     package='cdcagg_client',
                                                     env_var_prefix='CDCAGG_')

    def test_calls_conf_add_print_arg(self):
        sync.configure()
        self._mock_conf.add_print_arg.assert_called_once_with()

    def test_calls_conf_add_config_arg(self):
        sync.configure()
        self._mock_conf.add_config_arg.assert_called_once_with()

    def test_calls_conf_add_correctly(self):
        sync.configure()
        self._mock_conf.add.assert_has_calls([
            mock.call('--file-cache', type=str, env_var='FILE_CACHE',
                      help='Path to a cache file. Leave unset to not use file caching.'),
            mock.call('--no-remove', action='store_true', env_var='NO_REMOVE',
                      help="Don't remove records that were not found in this batch."),
            mock.call('--fail-on-parse', action='store_true', env_var='FAIL_ON_PARSE',
                      help="Stop processing a batch when a file cannot be properly parsed. "
                      "Enabling this option makes the synchronization process less fault "
                      "tolerant. Note that if a file is not parsed properly it's records "
                      "are not stored correctly and the database content will not reflect "
                      "the batch of files that were being processed."),
            mock.call('paths', nargs='+',
                      help="Paths to files to synchronize. If path points to a folder, "
                      "it and its subfolders will be searched for '.xml'-suffixed files")])

    def test_calls_cli_setup_setup_common_modules(self):
        sync.configure()
        self._mock_setup_common_modules.assert_called_once_with(
            MOD_DS_CLIENT, MOD_LOGGING, MOD_DS_QUERY)

    def test_returns_setup_common_modules_rval(self):
        rval = sync.configure()
        self.assertEqual(rval, self._mock_setup_common_modules.return_value)


class TestStudyMethods(KuhaUnitTestCase):

    maxDiff = None

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
        new_rec_dict = new.export_dict(include_metadata=False, include_id=False)
        new_rec_dict[Study._aggregator_identifier.path] = old._aggregator_identifier.get_value()
        mock_send.assert_called_once_with(new.collection, new_rec_dict, 'some-id')
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

    @mock.patch.object(sync.kuha_client, 'send_update_record_request')
    def test_update_record_keeps_old_aggregator_identifier(self, mock_send):
        """Updating an old record must not change the old record's _aggregator_identifier.

        Tests fix for #19 at bitbucket.
        """
        old = Study()
        old.add_study_number('study_1')
        old.add_abstract('some abstract', 'en')
        new = Study()
        new.add_study_number('study_1')
        new.add_abstract('another abstract', 'en')
        self.assertNotEqual(old._aggregator_identifier.get_value,
                            new._aggregator_identifier.get_value())
        exp_rec_dict = new.export_dict(include_metadata=False, include_id=False)
        exp_rec_dict[Study._aggregator_identifier.path] = old._aggregator_identifier.get_value()
        self._loop.run_until_complete(self.await_and_store_result(
            self.studymeths.update_record(new, old)))
        calls = mock_send.call_args_list
        self.assertEqual(len(calls), 1)
        cargs, ckwargs = calls[0]
        self.assertEqual(ckwargs, {})
        carg_coll, carg_dict, carg_id = cargs
        self.assertEqual(carg_coll, 'studies')
        self.assertEqual(carg_dict, exp_rec_dict)
        mock_send.assert_called_once_with(new.collection, exp_rec_dict, old.get_id())


class TestCli(KuhaUnitTestCase):

    @mock.patch.object(sync, 'run')
    @mock.patch.object(sync, 'configure', return_value=settings([]))
    def test_calls_configure(self, mock_configure, mock_run):
        sync.cli()
        mock_configure.assert_called_once_with()

    @mock.patch.object(sync, 'run')
    @mock.patch.object(sync, 'configure', return_value=settings(['/some/path']))
    def test_calls_run(self, mock_configure, mock_run):
        sync.cli()
        mock_run.assert_called_once_with(settings(['/some/path']))

    @mock.patch.object(sync.conf, 'print_conf')
    @mock.patch.object(sync, 'run')
    @mock.patch.object(sync, 'configure', return_value=settings(['/some/path'], print_configuration=True))
    def test_prints_configuration(self, mock_configure, mock_run, mock_print_conf):
        sync.cli()
        mock_print_conf.assert_called_once_with()
        mock_run.assert_not_called()

    @mock.patch.object(sync, '_logger')
    @mock.patch.object(sync, 'run', side_effect=ValueError())
    @mock.patch.object(sync, 'configure', return_value=settings(['/some/path']))
    def logs_out_exceptions_from_run(self, mock_configure, mock_run, mock_logger):
        with self.assertRaises(ValueError):
            sync.cli()
        mock_logger.exception.assert_called_once_with('Unhandled exception')

    @mock.patch.object(sync.kuha_client, 'BatchProcessor')
    @mock.patch.object(sync, 'configure', return_value=settings(['/some/path']))
    def test_calls_BatchProcessor_with_default_args(self, mock_configure, mock_BatchProcessor):
        sync.cli()
        mock_BatchProcessor.assert_called_once_with([sync.StudyMethods],
                                                    parsers=[sync.DDI122NesstarRecordParser,
                                                             sync.DDI25RecordParser,
                                                             sync.DDI31RecordParser],
                                                    fail_on_parse=False)
        mock_BatchProcessor.return_value.upsert_run.assert_called_once_with(['/some/path'], remove_absent=True)

    @mock.patch.object(sync.kuha_client, 'FileLoggingCache')
    @mock.patch.object(sync.kuha_client, 'BatchProcessor')
    @mock.patch.object(sync, 'configure', return_value=settings(['/some/path'],
                                                                no_remove=True,
                                                                file_cache='/path/to/filecache',
                                                                fail_on_parse=True))
    def test_calls_BatchProcessor_with_altered_args(self, mock_configure, mock_BatchProcessor,
                                                    mock_FileLoggingCache):
        sync.cli()
        mock_FileLoggingCache.assert_called_once_with('/path/to/filecache')
        mock_BatchProcessor.assert_called_once_with([sync.StudyMethods],
                                                    parsers=[sync.DDI122NesstarRecordParser,
                                                             sync.DDI25RecordParser,
                                                             sync.DDI31RecordParser],
                                                    cache=mock_FileLoggingCache.return_value,
                                                    fail_on_parse=True)
        mock_BatchProcessor.return_value.upsert_run.assert_called_once_with(['/some/path'], remove_absent=False)


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

    def test_minimal_ddi122_calls_query_single_correctly(self):
        self._mock_query_single.return_value = None
        self._mock_configure.return_value = settings([_testdata_path('minimal_ddi122.xml')])
        # Call
        sync.cli()
        # Assert
        self._mock_query_single.assert_called_once_with(
            Study, _filter={
                Study._provenance: {
                    MDB_ELEM_MATCH: {
                        Study._provenance.attr_base_url: 'http://services.fsd.tuni.fi/v0/oai',
                        Study._provenance.attr_identifier: 'oai:fsd.uta.fi:FSD0115'}}})

    def test_minimal_ddi122_creates(self):
        self._mock_query_single.return_value = None
        self._mock_configure.return_value = settings([_testdata_path('minimal_ddi122.xml')])
        # Call
        sync.cli()
        # Assert
        self._mock_send_delete_record_request.assert_not_called()
        self._mock_send_update_record_request.assert_not_called()
        calls = self._mock_send_create_record_request.call_args_list
        self.assertEqual(len(calls), 1)
        cargs, ckwargs = calls.pop()
        self.assertEqual(ckwargs, {})
        self.assertEqual(len(cargs), 2)
        coll, rec_dict = cargs
        self.assertEqual(coll, Study.get_collection())
        self.assertEqual(rec_dict['identifiers'][0]['identifier'], 'study_1')
        self.assertEqual(rec_dict['study_titles'][0]['study_title'], 'some study')

    def test_minimal_ddi122_updates(self):
        self._mock_query_single.return_value = Study({'study_number': 'study_1',
                                                      'study_titles': [
                                                          {'study_title': 'old title',
                                                           'language': 'en'}],
                                                      '_id': 'some_id'})
        self._mock_configure.return_value = settings([_testdata_path('minimal_ddi122.xml')])
        # Call
        sync.cli()
        # Assert
        self._mock_send_delete_record_request.assert_not_called()
        self._mock_send_create_record_request.assert_not_called()
        calls = self._mock_send_update_record_request.call_args_list
        self.assertEqual(len(calls), 1)
        cargs, ckwargs = calls.pop()
        self.assertEqual(ckwargs, {})
        self.assertEqual(len(cargs), 3)
        coll, rec_dict, rec_id = cargs
        self.assertEqual(coll, Study.get_collection())
        self.assertEqual(rec_dict['identifiers'][0]['identifier'], 'study_1')
        self.assertEqual(rec_dict['study_titles'][0]['study_title'], 'some study')
        self.assertEqual(rec_id, 'some_id')

    def test_minimal_ddi122_calls_query_distinct_correctly(self):
        self._mock_query_single.return_value = None
        self._mock_configure.return_value = settings([_testdata_path('minimal_ddi122.xml')])
        sync.cli()
        self._mock_query_distinct.assert_called_once_with(
            Study, fieldname=Study._id, _filter={
                Study._metadata.attr_status: {MDB_NOT_EQUAL: REC_STATUS_DELETED}
            }
        )

    def test_minimal_ddi122_deletes(self):
        self._mock_query_single.return_value = None
        self._mock_query_distinct.return_value = {'_id': ['delete_me_1', 'delete_me_2']}
        self._mock_configure.return_value = settings([_testdata_path('minimal_ddi122.xml')])
        sync.cli()
        self._mock_send_delete_record_request.assert_has_calls([
            mock.call('studies', record_id='delete_me_1'),
            mock.call('studies', record_id='delete_me_2')
        ], any_order=True)

    def test_minimal_ddi122_with_file_log_calls_send_update_request_correctly(self):
        """First call with nonexistent file cache will call docstore normally. Second call
        with a up-to-date filelog will not consult document store at all."""
        self._mock_query_single.return_value = Study({'study_number': 'study_1',
                                                      '_id': 'some_id'})
        with tempfile.TemporaryDirectory() as dirname:
            cache_path = os.path.join(dirname, 'filelog')
            self._mock_configure.return_value = settings([_testdata_path('minimal_ddi122.xml')],
                                                         file_cache=cache_path)
            # FIRST CALL
            sync.cli()
            self._mock_query_single.assert_called_once_with(
                Study, _filter={
                    Study._provenance: {
                        MDB_ELEM_MATCH: {
                            Study._provenance.attr_base_url: 'http://services.fsd.tuni.fi/v0/oai',
                            Study._provenance.attr_identifier: 'oai:fsd.uta.fi:FSD0115'}}})
            calls = self._mock_send_update_record_request.call_args_list
            self.assertEqual(len(calls), 1)
            cargs, ckwargs = calls.pop()
            self.assertEqual(ckwargs, {})
            self.assertEqual(len(cargs), 3)
            coll, rec_dict, rec_id = cargs
            self.assertEqual(coll, Study.get_collection())
            self.assertEqual(rec_dict['identifiers'][0]['identifier'], 'study_1')
            self.assertEqual(rec_dict['study_titles'][0]['study_title'], 'some study')
            self.assertEqual(rec_id, 'some_id')
            # SECOND CALL
            self._mock_send_update_record_request.reset_mock()
            self._mock_query_single.reset_mock()
            sync.cli()
            # ASSERT
            self._mock_send_update_record_request.assert_not_called()
            self._mock_query_single.assert_not_called()

    def test_batch_with_invalid_ddi_does_not_raise(self):
        """Test against #11 at Bitbucket"""
        self._mock_query_single.return_value = None
        self._mock_configure.return_value = settings([_testdata_path('minimal_ddi122.xml'),
                                                      _testdata_path('invalid_ddi25.xml')])
        # If the following does not raise we're good.
        sync.cli()

    def test_batch_with_invalid_ddi_creates(self):
        """Test against #11 at Bitbucket"""
        self._mock_query_single.return_value = None
        self._mock_configure.return_value = settings([_testdata_path('minimal_ddi122.xml'),
                                                      _testdata_path('invalid_ddi25.xml')])
        calls = self._mock_send_create_record_request.call_args_list
        sync.cli()
        self.assertEqual(len(calls), 1)
        cargs, ckwargs = calls.pop()
        self.assertEqual(ckwargs, {})
        self.assertEqual(len(cargs), 2)
        coll, rec_dict = cargs
        self.assertEqual(coll, Study.get_collection())
        self.assertEqual(rec_dict['identifiers'][0]['identifier'], 'study_1')
        self.assertEqual(rec_dict['study_titles'][0]['study_title'], 'some study')

    @mock.patch.object(sync.kuha_client._logger, 'exception')
    def test_batch_with_invalid_ddi_logs_exception(self, mock_exception):
        """Test against #11 at Bitbucket"""
        self._mock_query_single.return_value = None
        inv_path = _testdata_path('invalid_ddi25.xml')
        self._mock_configure.return_value = settings([_testdata_path('minimal_ddi122.xml'), inv_path])
        sync.cli()
        mock_exception.assert_called_once_with("Unable to parse file '%s'. Is the file valid?", inv_path)
