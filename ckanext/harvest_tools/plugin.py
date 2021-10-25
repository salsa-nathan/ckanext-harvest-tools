import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.harvest_tools.logic.action import get
from ckanext.harvest_tools.logic.auth import get as auth_get
import ckanext.harvest_tools.blueprint as blueprint
import ckanext.harvest_tools.cli as cli


class HarvestToolsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')


    # IAuthFunctions
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
    
    # IBlueprint
    def get_blueprint(self):
        return blueprint.harvest_tools

    # IClick
    def get_commands(self):
        return cli.get_commands()


