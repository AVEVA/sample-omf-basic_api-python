# NOTE: this script was designed using the v1.1
# version of the OMF specification, as outlined here:
# https://omf-docs.osisoft.com/documentation_v11/Whats_New.html
# *************************************************************************************

# ************************************************************************
# Import necessary packages
# ************************************************************************

import enum
import json
import time
import datetime
import gzip
import random
import requests
import traceback
import os
from urllib.parse import urlparse

# ************************************************************************
# Global Variables
# ************************************************************************

# The version of the OMFmessages
omfVersion = '1.1'

# The number of seconds to sleep before sending another round of messages
sleep_time = 1

# The configurations of the endpoints to send to
endpoints = None

# Holders for data message values
boolean_value_1 = 0
boolean_value_2 = 1

# List of possible endpoint types


class EndpointTypes(enum.Enum):
    OCS = 'OCS'
    EDS = 'EDS'
    PI = 'PI'

# ************************************************************************
# REQUIRED: generates a bearer token for authentication
# ************************************************************************


def get_token(endpoint):
    '''Gets the token for the omfendpoint'''

    endpoint_type = endpoint["EndpointType"]
    # return an empty string if the endpoint is not an OCS type
    if endpoint_type != EndpointTypes.OCS.value:
        return ''

    if (('expiration' in endpoint) and (endpoint["expiration"] - time.time()) > 5 * 60):
        return endpoint["token"]

    # we can't short circuit it, so we must go retreive it.

    discovery_url = requests.get(
        endpoint["Resource"] + '/identity/.well-known/openid-configuration',
        headers={'Accept': 'application/json'},
        verify=endpoint["VerifySSL"])

    if discovery_url.status_code < 200 or discovery_url.status_code >= 300:
        discovery_url.close()
        raise Exception(f'Failed to get access token endpoint from discovery URL: {discovery_url.status_code}:{discovery_url.text}')

    token_endpoint = json.loads(discovery_url.content)["token_endpoint"]
    token_url = urlparse(token_endpoint)
    # Validate URL
    assert token_url.scheme == 'https'
    assert token_url.geturl().startswith(endpoint["Resource"])

    token_information = requests.post(
        token_url.geturl(),
        data={'client_id': endpoint["ClientId"],
              'client_secret': endpoint["ClientSecret"],
              'grant_type': 'client_credentials'},
        verify=endpoint["VerifySSL"])

    token = json.loads(token_information.content)

    if token is None:
        raise Exception('Failed to retrieve Token')

    __expiration = float(token["expires_in"]) + time.time()
    __token = token["access_token"]

    # cache the results
    endpoint["expiration"] = __expiration
    endpoint["token"] = __token

    return __token


# ************************************************************************
# REQUIRED: wrapper function for sending an HTTP message
# ************************************************************************


def send_message_to_omf_endpoint(endpoint, message_type, message_omf_json, action='create'):
    '''Sends the request out to the preconfigured endpoint'''

    # Compress json omf payload, if specified
    compression = 'none'
    if endpoint["UseCompression"]:
        msg_body = gzip.compress(bytes(json.dumps(message_omf_json), 'utf-8'))
        compression = 'gzip'
    else:
        msg_body = json.dumps(message_omf_json)

    # Collect the message headers
    msg_headers = get_headers(endpoint, compression, message_type, action)

    # Send message to OMF endpoint
    endpoints_type = endpoint["EndpointType"]
    response = {}
    # If the endpoint is OCS
    if endpoints_type == EndpointTypes.OCS.value:
        response = requests.post(
            endpoint["OmfEndpoint"],
            headers=msg_headers,
            data=msg_body,
            verify=endpoint["VerifySSL"],
            timeout=endpoint["WebRequestTimeoutSeconds"]
        )
    # If the endpoint is EDS
    elif endpoints_type == EndpointTypes.EDS.value:
        response = requests.post(
            endpoint["OmfEndpoint"],
            headers=msg_headers,
            data=msg_body,
            timeout=endpoint["WebRequestTimeoutSeconds"]
        )
    # If the endpoint is PI
    elif endpoints_type == EndpointTypes.PI.value:
        response = requests.post(
            endpoint["OmfEndpoint"],
            headers=msg_headers,
            data=msg_body,
            verify=endpoint["VerifySSL"],
            timeout=endpoint["WebRequestTimeoutSeconds"],
            auth=(endpoint["Username"], endpoint["Password"])
        )

    # Check for 409, which indicates that a type with the specified ID and version already exists.
    if response.status_code == 409:
        return

    # response code in 200s if the request was successful!
    if response.status_code < 200 or response.status_code >= 300:
        print(msg_headers)
        response.close()
        print(
            f'Response from relay was bad. {message_type} message: {response.status_code} {response.text}.  Message holdings: {message_omf_json}')
        print()
        raise Exception(f'OMF message was unsuccessful, {message_type}. {response.status_code}:{response.text}')


# ************************************************************************
# REQUIRED: retrieves headers for HTTP request to the specified endpoint
# ************************************************************************


def get_headers(endpoint, compression='', message_type='', action=''):
    '''Assemble headers for sending to the endpoint's OMF endpoint'''

    endpoint_type = endpoint["EndpointType"]

    msg_headers = {
        'messagetype': message_type,
        'action': action,
        'messageformat': 'JSON',
        'omfversion': omfVersion
    }

    if(compression == 'gzip'):
        msg_headers["compression"] = 'gzip'

    # If the endpoint is OCS
    if endpoint_type == EndpointTypes.OCS.value:
        msg_headers["Authorization"] = f'Bearer {get_token(endpoint)}'
    # If the endpoint is PI
    elif endpoint_type == EndpointTypes.PI.value:
        msg_headers["x-requested-with"] = 'xmlhttprequest'

    # validate headers to prevent injection attacks
    validated_headers = {}

    for key in msg_headers:
        if key in {'Authorization', 'messagetype', 'action', 'messageformat', 'omfversion', 'x-requested-with', 'compression'}:
            validated_headers[key] = msg_headers[key]

    return validated_headers


# ************************************************************************
# This function will need to be customized to populate the OMF data
# message passed.
# ************************************************************************


def get_data(data):
    ''' Get data to be sent to EDS'''
    global boolean_value_1, boolean_value_2

    if data["containerid"] == 'FirstContainer' or data["containerid"] == 'SecondContainer':
        data["values"][0]["Timestamp"] = get_current_time()
        data["values"][0]["IntegerProperty"] = int(100*random.random())

    elif data["containerid"] == 'ThirdContainer':
        boolean_value_2 = (boolean_value_2 + 1) % 2
        data["values"][0]["Timestamp"] = get_current_time()
        data["values"][0]["NumberProperty1"] = 100*random.random()
        data["values"][0]["NumberProperty2"] = 100*random.random()
        data["values"][0]["StringEnum"] = str(bool(boolean_value_2))

    elif data["containerid"] == 'FourthContainer':
        boolean_value_1 = (boolean_value_1 + 1) % 2
        data["values"][0]["Timestamp"] = get_current_time()
        data["values"][0]["IntegerEnum"] = boolean_value_1

    else:
        print(f'Container {data["containerid"]} not recognized')

    return data


def get_current_time():
    ''' Returns the current time'''
    return datetime.datetime.utcnow().isoformat() + 'Z'


def get_json_file(filename):
    ''' Get a json file by the path specified relative to the application's path'''

    # Try to open the configuration file
    try:
        with open(
            filename,
            'r',
        ) as f:
            loaded_json = json.load(f)
    except Exception as error:
        print(f'Error: {str(error)}')
        print(f'Could not open/read file: {filename}')
        exit()

    return loaded_json


def get_config():
    ''' Return the config.json as a config file, while also populating base_endpoint, omf_endpoint, and default values'''

    # Try to open the configuration file
    endpoints = get_json_file('appsettings.json')["Endpoints"]

    # for each endpoint construct the check base and OMF endpoint and populate default values
    for endpoint in endpoints:
        endpoint_type = endpoint["EndpointType"]

        # If the endpoint is OCS
        if endpoint_type == EndpointTypes.OCS.value:
            base_endpoint = f'{endpoint["Resource"]}/api/{endpoint["ApiVersion"]}' + \
                f'/tenants/{endpoint["TenantId"]}/namespaces/{endpoint["NamespaceId"]}'

        # If the endpoint is EDS
        elif endpoint_type == EndpointTypes.EDS.value:
            base_endpoint = f'{endpoint["Resource"]}/api/{endpoint["ApiVersion"]}' + \
                f'/tenants/default/namespaces/default'

        # If the endpoint is PI
        elif endpoint_type == EndpointTypes.PI.value:
            base_endpoint = endpoint["Resource"]

        else:
            raise ValueError('Invalid endpoint type')

        omf_endpoint = f'{base_endpoint}/omf'

        # add the base_endpoint and omf_endpoint to the endpoint configuration
        endpoint["BaseEndpoint"] = base_endpoint
        endpoint["OmfEndpoint"] = omf_endpoint

        # check for optional/nullable parameters
        if 'VerifySSL' not in endpoint or endpoint["VerifySSL"] == None:
            endpoint["VerifySSL"] = True

        if 'UseCompression' not in endpoint or endpoint["UseCompression"] == None:
            endpoint["UseCompression"] = True

        if 'WebRequestTimeoutSeconds' not in endpoint or endpoint["WebRequestTimeoutSeconds"] == None:
            endpoint["WebRequestTimeoutSeconds"] = 30

    return endpoints


def main(test=False, last_sent_values={}):
    # Main program.  Seperated out so that we can add a test function and call this easily
    global endpoints

    success = True

    # Step 1 - Read endpoint configurations from config.json
    endpoints = get_config()

    # Step 2 - Get OMF Types
    omf_types = get_json_file('OMF-Types.json')

    # Step 3 - Get OMF Containers
    omf_containers = get_json_file('OMF-Containers.json')

    # Step 4 - Get OMF Data
    omf_data = get_json_file('OMF-Data.json')

    # Send messages and check for each endpoint in config.json

    try:
        # Send out the messages that only need to be sent once
        for endpoint in endpoints:
            if not endpoint["Selected"]:
                continue

            if not endpoint["VerifySSL"]:
                print('You are not verifying the certificate of the end point.  This is not advised for any system as there are security issues with doing this.')

            # Step 5 - Send OMF Types
            for omf_type in omf_types:
                send_message_to_omf_endpoint(endpoint, 'type', [omf_type])

            # Step 6 - Send OMF Containers
            for omf_container in omf_containers:
                send_message_to_omf_endpoint(
                    endpoint, 'container', [omf_container])

        # Step 7 - Send OMF Data
        count = 0
        # send data to all endpoints forever if this is not a test
        while not test or count < 2:

            '''This is where custom loop logic should go. 
            The get_data call should also be customized to populate omf_data with relevant data.'''

            for omf_datum in omf_data:
                data_to_send = get_data(omf_datum)
                for endpoint in endpoints:
                    if not endpoint["Selected"]:
                        continue
                    
                    # send the data
                    send_message_to_omf_endpoint(
                        endpoint, 'data', [data_to_send])

                # record the values sent if this is a test
                if test and count == 1:
                    last_sent_values.update(
                        {omf_datum["containerid"]: data_to_send})

            time.sleep(sleep_time)
            count = count + 1

    except Exception as ex:
        print(f'Encountered Error: {ex}')
        print
        traceback.print_exc()
        print
        success = False
        if test:
            raise ex

    print('Done')
    return success


if __name__ == '__main__':
    main()
