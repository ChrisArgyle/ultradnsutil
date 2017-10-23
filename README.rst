============
ultradnsutil
============
Use this utility to manage DNS zones and records on UltraDNS managed DNS. This utility can list, create, delete and promote zones but also delete A records.

How do I use it?
================
**First, create a credentials file**

  *For example*::

    $ cat ~/ultracreds.yml
    ---
    username: exampleuser
    password: examplepass

**Next, issue a command**

* *Listing zones*::

    $ python ultradnsutil.py -c ~/ultracreds.yml list_primary_zone
    example.com

    $ python ultradnsutil.py -c ~/ultracreds.yml list_secondary_zone
    contoso.com

* *Creating secondary zones*::

    $ python ultradnsutil.py -c ~/ultracreds.yml add_secondary_zone -z contoso.com -p 8.8.8.8
    result "{u'message': u'Pending', 'task_id': 'bc6a724a-9d2a-4cc8-8462-f7ccc189a532'}"

* *Promoting secondary zones to master*::

    $ python ultradnsutil.py -c ~/ultracreds.yml promote_zone -z contoso.com
    result "{u'message': u'Successful'}"

* *Deleting zones*::

    $ python ultradnsutil.py -c ~/ultracreds.yml delete_zone -z contoso.org
    result "{}"

* *Deleting A records*::

    $ python ultradnsutil.py -c ~/ultracreds.yml delete_a -z contoso.org -a www
    result "{}"

Detailed command usage info
===========================
  ::

    usage: ultradnsutil.py [-h] [-z ZONE] [-a A_RECORD] [-p PRIMARY_NS]
                           [-c CREDS_FILE]
                           {list_primary_zone,list_secondary_zone,add_secondary_zone,delete_zone,promote_zone,delete_a}

    positional arguments:
      {list_primary_zone,list_secondary_zone,add_secondary_zone,delete_zone,promote_zone,delete_a}
                            command: list/add/delete/promote zone, delete A record

    optional arguments:
      -h, --help            show this help message and exit
      -z ZONE, --zone ZONE  Specify zone to use in query
      -a A_RECORD, --a-record A_RECORD
                            Specify A record to use in query. Can be relative (ex
                            'foo') or absolute (ex 'foo.example.com')
      -p PRIMARY_NS, --primary-ns PRIMARY_NS
                            primary NS to receive zone xfer from

    required arguments:
      -c CREDS_FILE, --creds-file CREDS_FILE
                            API credentials yaml file: contains username and
                            password
