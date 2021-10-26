import click
import logging

import ckan.plugins.toolkit as tk

from ckanext.harvest_tools import helpers

log = logging.getLogger(__name__)
config = tk.config
get_action = tk.get_action


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
        tk.get_action('clean_harvest_object_table')({'ignore_auth': True}, {})
        log.info('Completed `clean_harvest_object_table`')
    except Exception as e:
        log.error('Error running `clean_harvest_object_table`')
        tk.error_shout(e)
    return


@harvest_tools.command()
@click.pass_context
def check_harvest_object(ctx):
    try:
        flask_app = ctx.meta["flask_app"]
        with flask_app.test_request_context():
            report = get_action('harvest_object_report')({'ignore_auth': True}, {})

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
@click.pass_context
def long_running(ctx):
    urls = []

    try:
        flask_app = ctx.meta["flask_app"]
        with flask_app.test_request_context():
            report = get_action('long_running_harvest_jobs')({'ignore_auth': True}, {})

            for job in report.get('job_details', []) or []:
                urls.append(config.get('ckan.site_url') + '/harvest/' + job['source_id'] + '/job/' + job['id'])

            if report.get('alerts', []) or []:
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
