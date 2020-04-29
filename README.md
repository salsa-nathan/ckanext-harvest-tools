# ckanext-harvest-tools

Adds some useful tools for monitoring and managing harvest jobs.

## Installation

Clone this repository into your CKAN extensions directory, e.g.

    cd /app/src
    
    git clone ...

Install the extension:

    cd /app/src/ckanext-harvest-tools
    
    python setup.py develop

Enable the extension by adding `harvest_tools` to `ckan.plugins` in your CKAN `.ini` file:

    ckan.plugins = ... harvest_tools ... harvest

__Note:__ this extension needs to appear before the `ckanext-harvest` extensions in order for the template overrides to work.

## Added functionality

### Controller actions

#### harvest_table_report

Visit `https://yourdomain/harvest/table_report` URL to view details about the harvest related database tables.

#### abort_harvest_job

Adds an `Abort job` button to any long running harvest job detail page.

### API endpoints

__NOTE:__ the following API endpoints are all restricted to `sysadmin` users.

#### harvest_object_report

    https://yourdomain/api/action/harvest_object_report

Returns details of the `harvest_object` database table for analysis.

#### long_running_harvest_jobs

    https://yourdomain/api/action/long_running_harvest_jobs

Returns details of long running harvest jobs (those running longer than 2 hours).

#### clean_harvest_object_table

Cleans the `harvest_object` by deleting any rows that are not "current".

    https://yourdomain/api/action/clean_harvest_object_table

__WARNING:__ only call this if you are absolutely sure you want to take this action!

Performs the following:

    DELETE FROM harvest_object_error WHERE harvest_object_id IN (SELECT id FROM harvest_object WHERE current != 't');
    DELETE FROM harvest_object WHERE current != 't';
    VACUUM(FULL, ANALYZE) harvest_object;
    REINDEX TABLE harvest_object;

