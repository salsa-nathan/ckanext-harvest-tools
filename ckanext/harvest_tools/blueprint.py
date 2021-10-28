import logging
import ckan.plugins.toolkit as toolkit
from flask import Blueprint

from ckanext.harvest_tools.logic.action import get

log = logging.getLogger(__name__)
get_action = toolkit.get_action
h = toolkit.h
render = toolkit.render
get_action = toolkit.get_action
_ = toolkit._
redirect_to = toolkit.redirect_to
url_for = toolkit.url_for

harvest_tools = Blueprint('harvest_tools', __name__)


def harvest_table_report():
    vars = {}

    vars['tables'] = get.get_harvest_table_info()

    return render('harvest_tools/harvest_table_report.html',
                  extra_vars=vars)


def abort_harvest_job(harvest_job_id):
    try:
        result = get_action('harvest_job_abort')(None, {"id": harvest_job_id})
        h.flash_success(_('Harvest job ID %s - aborted' % harvest_job_id))
    except Exception as e:
        h.flash_error(_('ERROR aborting harvest job ID %s' % harvest_job_id))

    return redirect_to(url_for('harvest_job_show', source=result.get('source_id') if result else None, id=harvest_job_id))


harvest_tools.add_url_rule('/harvest/abort_job/<harvest_job_id>', methods=['GET', 'POST'], view_func=abort_harvest_job)
harvest_tools.add_url_rule('/harvest/table_report', view_func=harvest_table_report)
