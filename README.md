# ckanext-harvest-tools

Adds some useful tools for monitoring and managing harvest jobs.

## Installation

Clone this repository into your CKAN extensions directory, e.g.

    cd /app/src
    
    git clone ...

Install the extension:

    cd /app/src/ckanext-harvest-tools
    
    python setup.py develop

## Configuration

Enable the extension by adding `harvest_tools` to `ckan.plugins` in your CKAN `.ini` file:

    ckan.plugins = ... harvest_tools ... harvest

__Note:__ this extension needs to appear before the `ckanext-harvest` extensions as this extension extends some default harvest templates.

Set the email recipient of the alert email notifications (if not set, `email_to` is used):

    ckanext.harvest_tools.email_to = you@email.com

Set the database connections details as required (defaults shown below if not set):

    ckanext.harvest_tools.db_host = postgres
    ckanext.harvest_tools.db_port = 5432
    ckanext.harvest_tools.db_name = ckan
    ckanext.harvest_tools.db_user = ckan
    ckanext.harvest_tools.db_pass = ckan

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

### CLI commands

This extension introduces the following `paster` commands:

#### check_harvest_objects

    ckan harvest-tools check-harvest-object -c /app/ckan/default/ckan.ini

Queries the CKAN database for information about the `harvest_object` table and assesses if it is getting too big.

If the `harvest_object` table size is over a certain threshold (defined in the `harvest_object_report` action) an email alert will be sent.

#### clean_harvest_objects

    ckan harvest-tools clean-harvest-objects -c /app/ckan/default/ckan.ini

Paster command to run the `clean_harvest_object_table` action above.

#### long_running_jobs

    ckan harvest-tools long-running -c /app/ckan/default/ckan.ini

Attempts to detect any long running harvest jobs and send an email alert.