import sys
from py12flogging.log_formatter import setup_app_logging
from kuha_common.query import (
    QueryController,
    FilterKeyConstants
)
from kuha_common import conf
import kuha_client
from cdcagg_common.records import Study
from cdcagg_common.mappings import (
    DDI122NesstarRecordParser,
    DDI25RecordParser,
    DDI31RecordParser
)


class StudyMethods(kuha_client.CollectionMethods):

    collection = Study.get_collection()

    async def query_record(self, record):
        return await QueryController().query_single(Study, _filter={
            FilterKeyConstants.and_: [
                {Study._provenance.attr_direct: True},
                {Study._provenance.attr_identifier: record._provenance[-1].attr_identifier.get_value()},
                {Study._provenance.attr_base_url: record._provenance[-1].attr_base_url.get_value()}]})

    async def query_distinct_ids(self):
        ids = await QueryController().query_distinct(Study, fieldname=Study._id)
        return set(ids[Study._id.path])

    async def remove_record_by_id(self, _id):
        return await kuha_client.send_delete_record_request(Study.get_collection(),
                                                            record_id=_id)

    async def update_record(self, new, old):
        new_dict = new.export_dict(include_provenance=False, include_metadata=False, include_id=False)
        old_dict = old.export_dict(include_provenance=False, include_metadata=False, include_id=False)
        if new_dict != old_dict:
            # Records differ. Send new record to docstore
            new_dict.update(new.export_provenance_dict())
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
    conf.load(prog='cdcagg_client.sync', package='cdcagg_client', env_var_prefix='CDCAGG_')
    conf.add_print_arg()
    conf.add_config_arg()
    conf.add_loglevel_arg()
    conf.add('--document-store-url', type=str)
    conf.add('--no-remove', action='store_true')
    conf.add('--file-cache', type=str)
    conf.add('paths', nargs='+')
    settings = conf.get_conf()
    setup_app_logging(conf.get_package(), loglevel=settings.loglevel)
    return settings


def cli():
    settings = configure()
    remove_absent = settings.no_remove is False
    parsers = [DDI122NesstarRecordParser, DDI25RecordParser, DDI31RecordParser]
    collections_methods = [StudyMethods]
    if settings.file_cache:
        with kuha_client.open_file_logging_cache(settings.file_cache) as cache:
            proc = kuha_client.BatchProcessor(collections_methods, parsers=parsers, cache=cache)
            proc.upsert_run(settings.paths, remove_absent=remove_absent)
        return 0
    proc = kuha_client.BatchProcessor(collections_methods, parsers=parsers)
    proc.upsert_run(settings.paths, remove_absent=remove_absent)


if __name__ == '__main__':
    sys.exit(cli())
