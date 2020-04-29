import ckan.lib.base as base
import ckanapi

from ckan.lib.base import BaseController, c, h, _
from ckan.plugins import toolkit
from ckanext.harvest_tools.logic.action import get


class HarvestToolsController(base.BaseController):
    def index(self):
        vars = {}

        ckan = ckanapi.RemoteCKAN('https://ckan-datavic-ckan-odp-develop.au.amazee.io', apikey='MY-SECRET-API-KEY')

        try:
            sources = ckan.action.harvest_source_list()
            vars['sources'] = sources
        except Exception, e:
            vars['errors'] = str(e)

        return base.render('harvest_tools/index.html',
                           extra_vars=vars)

    def harvest_table_report(self):
        vars = {}

        vars['tables'] = get.get_harvest_table_info()

        return base.render('harvest_tools/harvest_table_report.html',
                           extra_vars=vars)

    def abort_harvest_job(self, harvest_job_id):
        try:
            toolkit.get_action('harvest_job_abort')(None, {"id": harvest_job_id})
            h.flash_success(_('Harvest job ID %s - aborted' % harvest_job_id))
        except Exception, e:
            h.flash_error(_('ERROR aborting harvest job ID %s' % harvest_job_id))

        h.redirect_to('/harvest/data-directory/job/%s' % harvest_job_id)
