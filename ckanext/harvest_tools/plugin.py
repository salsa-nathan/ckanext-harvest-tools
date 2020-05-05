import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.harvest_tools.logic.action import get
from ckanext.harvest_tools.logic.auth import get as auth_get


class HarvestToolsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')

    # IRoutes

    def before_map(self, map):
        map.connect('abort_harvest_job', '/harvest/abort_job/{harvest_job_id}',
                    controller='ckanext.harvest_tools.controller:HarvestToolsController',
                    action='abort_harvest_job')
        map.connect('harvest_table_report', '/harvest/table_report',
                    controller='ckanext.harvest_tools.controller:HarvestToolsController',
                    action='harvest_table_report')

        return map

    # IRoutes

    def get_auth_functions(self):
        return {
            'abort_harvest_job': auth_get.abort_harvest_job,
            'clean_harvest_object_table': auth_get.clean_harvest_object_table,
            'harvest_object_report': auth_get.harvest_object_report,
            'long_running_harvest_jobs': auth_get.long_running_harvest_jobs,
        }

    # IActions
    def get_actions(self):
        return {
            'harvest_object_report': get.harvest_object_report,
            'long_running_harvest_jobs': get.long_running_harvest_jobs,
            'clean_harvest_object_table': get.clean_harvest_object_table,
        }

