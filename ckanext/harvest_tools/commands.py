from ckan.lib.cli import CkanCommand
# No other CKAN imports allowed until _load_config is run,
# or logging is disabled


class Clean(CkanCommand):
    """
    Cleans the `harvest_object` and `harvest_object_error` tables
    """
    summary = __doc__.split('\n')[0]

    def __init__(self,name):

        super(Clean, self).__init__(name)

    def command(self):
        self._load_config()

        import ckan.plugins.toolkit as toolkit

        log = __import__('logging').getLogger(__name__)

        try:
            toolkit.get_action('clean_harvest_object_table')(None, {})
            log.info('Completed `clean_harvest_object_table`')
        except Exception, e:
            log.error('Error running `clean_harvest_object_table`')
            log.error(str(e))

        return
