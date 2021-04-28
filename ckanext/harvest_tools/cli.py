import click
import logging

import ckan.plugins.toolkit as tk

from ckanext.harvest_tools import helpers

log = logging.getLogger(__name__)


def get_commands():
    return [
        harvest_tools
    ]

@click.group(short_help="Harvest Tools CLI")
def harvest_tools():
    pass

@harvest_tools.command()
def clean():
    try:
        tk.get_action('clean_harvest_object_table')(None, {})
        log.info('Completed `clean_harvest_object_table`')
    except Exception as e:
        log.error('Error running `clean_harvest_object_table`')
        tk.error_shout(e)
    return

@harvest_tools.command()
def check_harvest_object():
    try:
        report = tk.get_action('harvest_object_report')(None, {})

        if 'alerts' in report and len(report['alerts']) > 0:
            helpers.send_notification_email(
                template='notification-harvest-object-table',
                extra_vars={
                    "alerts": report['alerts'],
                    "url": config.get('ckan.site_url') + '/harvest/table_report'
                }
            )
    except Exception as e:
            log.error('Error calling `harvest_object_report`')
            tk.error_shout(e)

    return

@harvest_tools.command()
def long_running():
    urls = []

    try:
        report = tk.get_action('long_running_harvest_jobs')(None, {})

        for job in report['job_details']:
            urls.append(config.get('ckan.site_url') + '/harvest/' + job['source_id'] + '/job/' + job['id'])

        if report['alerts']:
            helpers.send_notification_email(
                template='notification-long-running-job',
                extra_vars={
                    "alerts": report['alerts'],
                    "urls": urls
                }
            )
    except Exception as e:
        log.error('Error calling `long_running_harvest_jobs`')
        tk.error_shout(e)
    return

