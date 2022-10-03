import logging

from odoo.addons.web.controllers.main import DataSet
from odoo.http import request


class DataSetInh(DataSet):
    def do_search_read(self, model, fields=False, offset=0, limit=False, domain=None
                       , sort=None):
        """ Performs a search() followed by a read() (if needed) using the
        provided search criteria

        :param str model: the name of the model to search on
        :param fields: a list of the fields to return in the result records
        :type fields: [str]
        :param int offset: from which index should the results start being returned
        :param int limit: the maximum number of records to return
        :param list domain: the search domain for the query
        :param list sort: sorting directives
        :returns: A structure (dict) with two keys: ids (all the ids matching
                  the (domain, context) pair) and records (paginated records
                  matching fields selection set)
        :rtype: list
        """
        Model = request.env[model]

        records = Model.search_read(domain, fields,
                                    offset=offset or 0, limit=limit or False, order=sort or False)
        try:
            records = sorted(records, key=lambda record: record.name.lower() or record.number.lower())
        except Exception as e:
            logging.info(e.args)
        finally:
            if not records:
                return {
                    'length': 0,
                    'records': []
                }
            if limit and len(records) == limit:
                length = Model.search_count(domain)
            else:
                length = len(records) + (offset or 0)
            return {
                'length': length,
                'records': records
            }