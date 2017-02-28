import argparse
import sys
import os
import yaml

import ultra_rest_client

USER_NAME = "username"
PASSWORD = "password"
API_DOMAIN = "restapi.ultradns.com"

def get_account_name(client):
    """
    Return UltraDNS account name (of the first account available to this client)
    """
    try:
        account_details = client.get_account_details()
        account_name = account_details['accounts'][0]['accountName']
    except Exception as e:
        errordie("could not get account name: {}".format(e))

    return(account_name)


def list_zone(client, zone_name):
    """
    Print names of a zone or all zones
    """
    try:
        account_name = get_account_name(client)
        if zone_name == None:
            zones = client.get_zones_of_account(account_name)
        else:
            zones = []
    except Exception as e:
        errordie("failed to get zone(s): {}".format(e))

    for zone in zones['zones']:
        # UltraDNS appends a '.' to each zone so we remove it before printing
        print(zone['properties']['name'][:-1])

def errordie(message):
    """
    Print error message then quit with exit code 1
    """
    prog = os.path.basename(sys.argv[0])
    sys.stderr.write("{}: error: {}\n".format(prog, message))
    sys.exit(1)

def main():
    """
    Handle command line and do API requests
    """
    # parse command line args
    parser = argparse.ArgumentParser()
    parser.add_argument('-z', '--zone', default=None, help="zone to run query against")
    parser.add_argument('command',
            type=str,
            choices=[ 
                'list_zone',
                'add_secondary_zone',
                'delete_zone',
                'promote_zone',
                'delete_a',
                'add_web',
                'add_slb',
                'add_tc',
                ],
            help="command: list/add/delete/promote zone, delete A record, add Web Forwarding/Simple Load Balancer/Traffic Controller entry")
    parser_required = parser.add_argument_group('required arguments')
    parser_required.add_argument('-c', '--creds-file',
            help="API credentials yaml file: contains {} and {}".format(USER_NAME, PASSWORD))

    args = parser.parse_args()

    # validate args
    if getattr(args, 'creds_file', None) == None:
        errordie("Please specify API credentials file")

    # validate creds yaml file
    try:
        creds_file = open(args.creds_file, "r")
        creds = yaml.load(creds_file)
        creds_file.close()
    except Exception as e:
        errordie("Could not load API credentials yaml file: {}".format(e))

    if USER_NAME not in creds:
        errordie("API credentials file does not specify '{}'".format(USER_NAME))
    if PASSWORD not in creds:
        errordie("API credentials file does not specify '{}'".format(PASSWORD))

    # create authenticated session
    try:
        client = ultra_rest_client.RestApiClient(creds[USER_NAME], creds[PASSWORD], False,
                API_DOMAIN)
    except Exception as e:
        errordie("could not authenticate: {}".format(e))

    # do query
    if args.command == 'list_zone':
        list_zone(client, args.zone)

if __name__ == "__main__":
    main()
