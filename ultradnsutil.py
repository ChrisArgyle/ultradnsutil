import argparse
import sys
import os
import yaml

import ultra_rest_client

USER_NAME = "username"
PASSWORD = "password"
API_DOMAIN = "restapi.ultradns.com"


def print_json_result(json_result):
    """
    Print the json formatted result of an api query
    """
    print("result \"{}\"".format(json_result))


def delete_zone(client, zone_name):
    """
    Delete a zone 
    """
    try:
        json_result = client.delete_zone("{}.".format(zone_name))
    except Exception as e:
        errordie("Failed to delete zone '{}': {}".format(zone_name, e))

    print_json_result(json_result)


def add_secondary_zone(client, zone_name, primary_ns):
    """
    Add secondary zone to account (first account available to this client)
    """
    account_name = get_account_name(client)

    try:
        json_result = client.create_secondary_zone(account_name, zone_name, primary_ns)
    except Exception as e:
        errordie("failed to add secondary zone: {}".format(e))

    print_json_result(json_result)


def get_account_name(client):
    """
    Return UltraDNS account name (first account available to this client)
    """
    try:
        account_details = client.get_account_details()
        account_name = account_details['accounts'][0]['accountName']
    except Exception as e:
        errordie("could not get account name: {}".format(e))

    return(account_name)


def list_zone(client, zone_name, q):
    """
    Print names of all zones
    """
    try:
        account_name = get_account_name(client)
        zones = client.get_zones_of_account(account_name, q)
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
    parser.add_argument('-p', '--primary-ns', default=None,
            help="primary NS to receive zone xfer from")
    parser.add_argument('command',
            type=str,
            choices=[ 
                'list_primary_zone',
                'list_secondary_zone',
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

    if (args.command == 'add_secondary_zone' or
            args.command == 'delete_zone' or
            args.command == 'promote_zone'):
        if args.zone == None:
            errordie("Please specify zone to run query against")

    if args.command == 'add_secondary_zone' and getattr(args, 'primary_ns', None) == None:
        errordie("Please specify primary NS to receive zone xfer from")

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
    if args.command == 'list_primary_zone':
        list_zone(client, args.zone, {'zone_type':'PRIMARY'})
    elif args.command == 'list_secondary_zone':
        list_zone(client, args.zone, {'zone_type':'SECONDARY'})
    elif args.command == 'add_secondary_zone':
        add_secondary_zone(client, args.zone, args.primary_ns)
    elif args.command == 'delete_zone':
        delete_zone(client, args.zone)

if __name__ == "__main__":
    main()
