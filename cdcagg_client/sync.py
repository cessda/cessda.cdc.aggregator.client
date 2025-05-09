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

"""Synchronize records to CESSDA Metadata Aggregator DocStore.

This module provides an entry point used for syncronizing records
found from XML files to the DocStore.

Synchronization dedulicates records based on provenance
information. If two records share the same baseUrl + identifier
combination in one of their provenance items, they are considered to
be the same record. In that case the new record always overwrites the
old one.

Deduplication is implemented in :class:`StudyMethods`.
"""
import sys
import logging
from kuha_common.query import QueryController
from kuha_common import (
    conf,
    cli_setup
)
from kuha_common.document_store.constants import REC_STATUS_DELETED
import kuha_client
from cdcagg_common.records import Study
from cdcagg_common.mappings import (
    DDI122NesstarRecordParser,
    DDI25RecordParser,
    DDI31RecordParser,
    DDI32RecordParser,
    DDI33RecordParser
)


_logger = logging.getLogger(__name__)


class StudyMethods(kuha_client.CollectionMethods):
    """Implement StudyMethods subclass of CollectionMethods

    Implement methods :meth:`query_record` and :meth:`query_distinct_ids` that
    are abstract in base class.
    Override method :meth:`update_record` to correctly handle provenance info.
    """

    collection = Study.get_collection()

    async def query_record(self, record):
        """Query record from Document Store.

        This method is called from upsert() method. If this method
        returns None, then the upsert() will never call
        update_record(), but will call create_record() instead.

        This query uses elemMatch to look for the identifier and
        base_url from within the same provenance item. It loops
        throught all provenance items of `record` to query for a
        record with matching provenance base_url + identifier
        combination. If a match is found, it is returned.

        :param record: Study to query for.
        :type record: :obj:`cdcagg_common.records.Study`
        :returns: Result of the query.
        :rtype: Instance of Study or None.
        """
        # This query uses elemMatch to make sure the identifier and base_url are
        # within the same provenance item. Direct attribute here is not needed
        # since we're interested in indirect records as well.

        # Loop throught all provenance items to query for a record with matching
        # provenance base_url + identifier combination.
        rec = None
        for prov in record._provenance:
            rec = await QueryController().query_single(Study, _filter={
                Study._provenance: {
                    QueryController.fk_constants.elem_match: {
                        Study._provenance.attr_base_url: prov.attr_base_url.get_value(),
                        Study._provenance.attr_identifier: prov.attr_identifier.get_value()}}})
            if rec:
                break
        return rec

    async def query_distinct_ids(self):
        """Query distinct IDs from collection that are not deleted.

        :returns: Distinct ids
        :rtype: set
        """
        ids = await QueryController().query_distinct(
            Study, fieldname=Study._id,
            _filter={Study._metadata.attr_status:
                     {QueryController.fk_constants.not_equal: REC_STATUS_DELETED}})
        return set(ids[Study._id.path])

    async def update_record(self, new, old):
        """Update existing Document Store record.

        Override :meth:`kuha_client.CollectionMethods.update_record`
        to handle provenance data correctly.

        :param new: New record.
        :type new: :obj:`cdcagg_common.records.Study`
        :param old: Old record.
        :type old: :obj:`cdcagg_common.records.Study`
        :returns: False if record does not need updating.
        :rtype: bool
        """
        new_dict = new.export_dict(include_provenance=False, include_metadata=False, include_id=False)
        old_dict = old.export_dict(include_provenance=False, include_metadata=False, include_id=False)
        if new_dict != old_dict:
            # Records differ. Send new record to docstore
            new_dict.update(new.export_provenance_dict())
            # Use old aggregator identifier.
            # Disabling pylint protected access -rule for the next row.
            # Attribute _aggregator_identifier is prefixed with a single
            # underscore since it reflects the underlying payload schema.
            # pylint: disable-next=protected-access
            new_dict.update(old._aggregator_identifier.export_dict())
            await kuha_client.send_update_record_request(new.get_collection(),
                                                         new_dict, old.get_id())
        elif await self._update_metadata_if_deleted(old) is True:
            # Records match, but old record is deleted. Update metadata to docstore.
            await kuha_client.send_update_record_request(new.get_collection(),
                                                         old.export_dict(include_provenance=True,
                                                                         include_metadata=True,
                                                                         include_id=False),
                                                         old.get_id())
        else:
            # Records match. No need to update.
            return False
        return True


def configure():
    """Declare configuration options and load settings.

    :returns: Loaded settings.
    :rtype: :obj:`argparse.Namespace`
    """
    conf.load('cdcagg_client.sync', package='cdcagg_client', env_var_prefix='CDCAGG_')
    conf.add_print_arg()
    conf.add_config_arg()
    conf.add('--file-cache', type=str, env_var='FILE_CACHE',
             help='Path to a cache file. Leave unset to not use file caching.')
    conf.add('--no-remove', action='store_true', env_var='NO_REMOVE',
             help="Don't remove records that were not found in this batch.")
    conf.add('--fail-on-parse', action='store_true', env_var='FAIL_ON_PARSE',
             help="Stop processing a batch when a file cannot be properly parsed. "
             "Enabling this option makes the synchronization process less fault tolerant. "
             "Note that if a file is not parsed properly it's records are not stored "
             "correctly and the database content will not reflect the batch of files "
             "that were being processed.")
    conf.add('paths', nargs='+', help="Paths to files to synchronize. If path points to a folder, it and its "
             "subfolders will be searched for '.xml'-suffixed files")
    settings = cli_setup.setup_common_modules(cli_setup.MOD_DS_CLIENT,
                                              cli_setup.MOD_LOGGING,
                                              cli_setup.MOD_DS_QUERY)
    return settings


def run(settings):
    """Run the program with 'settings'.

    Load :class:`BatchProcessor` and call :meth:`BatchProcessor.upsert_run`

    :param :obj:`argparse.Namespace` settings: Use settings to run the program.
    """
    remove_absent = settings.no_remove is False
    parsers = [DDI122NesstarRecordParser, DDI25RecordParser,
               DDI31RecordParser, DDI32RecordParser, DDI33RecordParser]
    collections_methods = [StudyMethods]
    if settings.file_cache:
        with kuha_client.open_file_logging_cache(settings.file_cache) as cache:
            proc = kuha_client.BatchProcessor(collections_methods,
                                              parsers=parsers,
                                              cache=cache,
                                              fail_on_parse=settings.fail_on_parse)
            proc.upsert_run(settings.paths, remove_absent=remove_absent)
        return
    proc = kuha_client.BatchProcessor(collections_methods,
                                      parsers=parsers,
                                      fail_on_parse=settings.fail_on_parse)
    proc.upsert_run(settings.paths, remove_absent=remove_absent)


def cli():
    """Start the program from command line.

    Load configuration, run program, log and
    re-raise propagated exceptions.
    """
    settings = configure()
    if settings.print_configuration:
        print('Print active configuration and exit\n')
        conf.print_conf()
        return
    try:
        run(settings)
    except KeyboardInterrupt:
        _logger.warning('Shutdown by CTRL + C', exc_info=True)
    except Exception:
        _logger.exception('Unhandled exception')
        raise


if __name__ == '__main__':
    sys.exit(cli())
