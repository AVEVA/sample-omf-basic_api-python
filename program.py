# NOTE: this script was designed using the v1.1
# version of the OMF specification, as outlined here:
# https://omf-docs.osisoft.com/documentation_v11/Whats_New.html
# *************************************************************************************

# ************************************************************************
# Import necessary packages
# ************************************************************************

import configparser
import json
import time
import datetime
import platform
import socket
import gzip
import random
import requests
import traceback
import base64
import os

# ************************************************************************
# Global Variables
# ************************************************************************

# The version of the OMFmessages
omfVersion = "1.1"

# The application path. This is used for loading in configuration files
app_path = None

# The configurations of the endpoints to send to
endpoints = None

# List of possible endpoint types
endpoint_types = ["OCS", "EDS", "PI"]

# Holders for data message values
boolean_value_1 = 0
boolean_value_2 = 1

# ************************************************************************
# REQUIRED: generates a bearer token for authentication
# ************************************************************************


def get_token(endpoint):
    '''Gets the token for the omfendpoint'''

    endpoint_type = endpoint["endpoint-type"]
    # return an empty string if the endpoint is not an OCS type
    if endpoint_type != endpoint_types[0]:
        return ""

    if (("expiration" in endpoint) and (endpoint["expiration"] - time.time()) > 5 * 60):
        return endpoint["token"]

    # we can't short circuit it, so we must go retreive it.

    discoveryUrl = requests.get(
        endpoint["resource"] + "/identity/.well-known/openid-configuration",
        headers={"Accept": "application/json"},
        verify=endpoint["verify-ssl"])

    if discoveryUrl.status_code < 200 or discoveryUrl.status_code >= 300:
        discoveryUrl.close()
        print("Failed to get access token endpoint from discovery URL: {status}:{reason}".
              format(status=discoveryUrl.status_code, reason=discoveryUrl.text))
        raise ValueError

    tokenEndpoint = json.loads(discoveryUrl.content)["token_endpoint"]

    tokenInformation = requests.post(
        tokenEndpoint,
        data={"client_id": endpoint["client-id"],
              "client_secret": endpoint["client-secret"],
              "grant_type": "client_credentials"},
        verify=endpoint["verify-ssl"])

    token = json.loads(tokenInformation.content)

    if token is None:
        raise Exception("Failed to retrieve Token")

    __expiration = float(token['expires_in']) + time.time()
    __token = token['access_token']

    # cache the results
    endpoint["expiration"] = __expiration
    endpoint["token"] = __token
    
    return __token


# ************************************************************************
# REQUIRED: wrapper function for sending an HTTP message
# ************************************************************************


def send_message_to_omf_endpoint(endpoint, message_type, message_omf_json, action='create'):
    '''Sends the request out to the preconfigured endpoint'''
    global endpoint_types

    # Compress json omf payload, if specified
    compression = 'none'
    if endpoint["use-compression"]:
        msg_body = gzip.compress(bytes(json.dumps(message_omf_json), 'utf-8'))
        compression = 'gzip'
    else:
        msg_body = json.dumps(message_omf_json)

    # Collect the message headers
    msg_headers = get_headers(endpoint, compression, message_type, action)

    # Send message to OMF endpoint
    endpoints_type = endpoint["endpoint-type"]
    response = {}
    # If the endpoint is OCS
    if endpoints_type == endpoint_types[0]:
        response = requests.post(
            endpoint["omf-endpoint"],
            headers=msg_headers,
            data=msg_body,
            verify=endpoint["verify-ssl"],
            timeout=endpoint["web-request-timeout-seconds"]
        )
    # If the endpoint is EDS
    elif endpoints_type == endpoint_types[1]:
        response = requests.post(
            endpoint["omf-endpoint"],
            headers=msg_headers,
            data=msg_body,
            timeout=endpoint["web-request-timeout-seconds"]
        )
    # If the endpoint is PI
    elif endpoints_type == endpoint_types[2]:
        response = requests.post(
            endpoint["omf-endpoint"],
            headers=msg_headers,
            data=msg_body,
            verify=endpoint["verify-ssl"],
            timeout=endpoint["web-request-timeout-seconds"],
            auth=(endpoint["username"], endpoint["password"])
        )

    # Check the response
    if response.status_code == 409:
        return

    # response code in 200s if the request was successful!
    if response.status_code < 200 or response.status_code >= 300:
        print(msg_headers)
        response.close()
        print('Response from relay was bad.  "{0}" message: {1} {2}.  Message holdings: {3}'.format(
            message_type, response.status_code, response.text, message_omf_json))
        print()
        raise Exception("OMF message was unsuccessful, {message_type}. {status}:{reason}".format(
            message_type=message_type, status=response.status_code, reason=response.text))


# ************************************************************************
# REQUIRED: retrieves headers for HTTP request to the specified endpoint
# ************************************************************************


def get_headers(endpoint, compression="", message_type="", action=""):
    '''Assemble headers for sending to the endpoint's OMF endpoint'''
    global endpoint_types

    endpoint_type = endpoint["endpoint-type"]

    # If the endpoint is OCS
    if endpoint_type == endpoint_types[0]:
        msg_headers = {
            "Authorization": "Bearer %s" % get_token(endpoint),
            'messagetype': message_type,
            'action': action,
            'messageformat': 'JSON',
            'omfversion': omfVersion,
            'compression': compression
        }
    # If the endpoint is EDS
    elif endpoint_type == endpoint_types[1]:
        msg_headers = {
            "Content-Type": "application/json",
            'messagetype': message_type,
            'action': action,
            'messageformat': 'JSON',
            'omfversion': omfVersion
        }
        if(compression == "gzip"):
            msg_headers["compression"] = "gzip"
    # If the endpoint is PI
    elif endpoint_type == endpoint_types[2]:
        msg_headers = {
            "x-requested-with": "xmlhttprequest",
            'messagetype': message_type,
            'action': action,
            'messageformat': 'JSON',
            'omfversion': omfVersion
        }
        if(compression == "gzip"):
            msg_headers["compression"] = "gzip"

    return msg_headers


# ************************************************************************
# This function will need to be customized to populate the OMF data
# message passed.
# ************************************************************************


def get_data(data):
    ''' Get data to be sent to EDS'''
    global boolean_value_1, boolean_value_2

    if data["containerid"] == "Container1" or data["containerid"] == "Container2":
        data["values"][0]["timestamp"] = get_current_time()
        data["values"][0]["IntegerProperty"] = int(100*random.random())

    elif data["containerid"] == "Container3":
        boolean_value_2 = (boolean_value_2 + 1) % 2
        data["values"][0]["timestamp"] = get_current_time()
        data["values"][0]["NumberProperty1"] = 100*random.random()
        data["values"][0]["NumberProperty2"] = 100*random.random()
        data["values"][0]["StringEnum"] = str(bool(boolean_value_2))

    elif data["containerid"] == "Container4":
        boolean_value_1 = (boolean_value_1 + 1) % 2
        data["values"][0]["timestamp"] = get_current_time()
        data["values"][0]["IntegerEnum"] = boolean_value_1

    else:
        print(f"Container {data['containerid']} not recognized")

    return data


def get_current_time():
    ''' Returns the current time'''
    return datetime.datetime.utcnow().isoformat() + 'Z'


def get_json_file(filename):
    ''' Get a json file by the path specified relative to the application's path'''
    global app_path

    # Try to open the configuration file
    try:
        with open(
            f"{app_path}/{filename}",
            "r",
        ) as f:
            loaded_json = json.load(f)
    except Exception as error:
        print(f"Error: {str(error)}")
        print(f"Could not open/read file: {filename}")
        exit()

    return loaded_json


def get_config():
    ''' Return the config.json as a config file, while also populating base_endpoint, omf_endpoint, and default values'''
    global endpoint_types

    # Try to open the configuration file
    endpoints = get_json_file("config.json")["endpoints"]

    # for each endpoint construct the check base and OMF endpoint and populate default values
    for endpoint in endpoints:
        endpoint_type = endpoint["endpoint-type"]

        # If the endpoint is OCS
        if endpoint_type == endpoint_types[0]:
            base_endpoint = f"{endpoint['resource']}/api/{endpoint['api-version']}" + \
                f"/tenants/{endpoint['tenant']}/namespaces/{endpoint['namespace']}"

        # If the endpoint is EDS
        elif endpoint_type == endpoint_types[1]:
            base_endpoint = f"{endpoint['resource']}/api/{endpoint['api-version']}" + \
                f"/tenants/default/namespaces/default"

        # If the endpoint is PI
        elif endpoint_type == endpoint_types[2]:
            base_endpoint = endpoint["resource"]

        omf_endpoint = f"{base_endpoint}/omf"

        # add the base_endpoint and omf_endpoint to the endpoint configuration
        endpoint["base-endpoint"] = base_endpoint
        endpoint["omf-endpoint"] = omf_endpoint

        # check for optional/nullable parameters
        if "verify-ssl" not in endpoint or endpoint["verify-ssl"] == None:
            endpoint["verify-ssl"] = True

        if "use-compression" not in endpoint or endpoint["use-compression"] == None:
            endpoint["use-compression"] = False

        if "web-request-timeout-seconds" not in endpoint or endpoint["web-request-timeout-seconds"] == None:
            endpoint["web-request-timeout-seconds"] = 30

    return endpoints


def main(test=False):
    # Main program.  Seperated out so that we can add a test function and call this easily
    global app_path, endpoints, endpoint_types

    success = True

    # get the app_path
    app_path = os.path.dirname(os.path.abspath(__file__))

    # Step 1 - Read endpoint configurations from config.json
    endpoints = get_config()

    # Step 2 - Get OMF Types
    omf_types = get_json_file("OMF-Types.json")

    # Step 3 - Get OMF Containers
    omf_containers = get_json_file("OMF-Containers.json")

    # Step 4 - Get OMF Data
    omf_data = get_json_file("OMF-Data.json")

    # Send messages and check for each endpoint in config.json

    try:
        # Send out the messages that only need to be sent once
        for endpoint in endpoints:
            if not endpoint["verify-ssl"]:
                print("You are not verifying the certificate of the end point.  This is not advised for any system as there are security issues with doing this.")

            get_token(endpoint)

            # Step 5 - Send OMF Types
            for omf_type in omf_types:
                send_message_to_omf_endpoint(endpoint, "type", [omf_type])

            # Step 6 - Send OMF Containers
            for omf_container in omf_containers:
                send_message_to_omf_endpoint(
                    endpoint, "container", [omf_container])

        # Step 7 - Send OMF Data
        count = 0
        time.sleep(1)
        # send data to all endpoints forever if this is not a test
        while not test or count < 2:

            '''This is where custom loop logic should go. 
            The get_data call should also be customized to populate omf_data with relevant data.'''

            for omf_datum in omf_data:
                data_to_send = get_data(omf_datum)
                for endpoint in endpoints:
                    # send the data
                    send_message_to_omf_endpoint(
                        endpoint, "data", [data_to_send])
            time.sleep(1)
            count = count + 1

    except Exception as ex:
        print(("Encountered Error: {error}".format(error=ex)))
        print
        traceback.print_exc()
        print
        success = False
        if test:
            raise ex

    print("Done")
    return success


if __name__ == '__main__':
    main()
