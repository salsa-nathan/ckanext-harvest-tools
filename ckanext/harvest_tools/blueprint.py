import logging
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from flask import Blueprint

from ckanext.harvest_tools.logic.action import get

harvest_tools = Blueprint('harvest_tools', __name__)

def harvest_table_report():
        vars = {}

        vars['tables'] = get.get_harvest_table_info()

        return toolkit.render('harvest_tools/harvest_table_report.html',
                           extra_vars=vars)


def abort_harvest_job( harvest_job_id):
    try:
        toolkit.get_action('harvest_job_abort')(None, {"id": harvest_job_id})
        toolkit.h.flash_success(_('Harvest job ID %s - aborted' % harvest_job_id))
    except Exception as e:
        toolkit.h.flash_error(_('ERROR aborting harvest job ID %s' % harvest_job_id))

    toolkit.h.redirect_to('/harvest/data-directory/job/%s' % harvest_job_id)


harvest_tools.add_url_rule('/harvest/abort_job/<harvest_job_id>', view_func=abort_harvest_job)
harvest_tools.add_url_rule('/harvest/table_report', view_func=harvest_table_report)


