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

# The application path. This is used for loading in configuration files
app_path = None

# The configurations of the destinations to send to
destinations = None

# List of possible destination types
destination_types = ["OCS", "EDS", "PI"]

# ************************************************************************
# Specify options for sending web requests to the target PI System
# ************************************************************************

# The version of the OMFmessages
omfVersion = "1.1"

# Specify whether to compress OMF message before
# sending it to ingress endpoint
USE_COMPRESSION = False

# Set this to the path of the certificate pem file if you using a self signed cert.
# Set this to True if your cert is trusted by the Python certify.
# Set to False if you do not want to check the certificate (NOT RECOMMENDED)
VERIFY_SSL = True

# Specify the timeout, in seconds, for sending web requests
# (if it takes longer than this to send a message, an error will be thrown)
WEB_REQUEST_TIMEOUT_SECONDS = 30

# Token information
__expiration = 0
__token = ""

# Holders for data message values
boolean_value_1 = 0
boolean_value_2 = 1


def get_token(destination):
    '''Gets the token for the omfendpoint'''

    global __expiration, __token

    destination_type = destination["destination-type"]
    # return an empty string if the destination is not an OCS type
    if destination_type != destination_types[0]:
        return ""

    if ((__expiration - time.time()) > 5 * 60):
        return __token

    # we can't short circuit it, so we must go retreive it.

    discoveryUrl = requests.get(
        destination["resource"] + "/identity/.well-known/openid-configuration",
        headers={"Accept": "application/json"},
        verify=VERIFY_SSL)

    if discoveryUrl.status_code < 200 or discoveryUrl.status_code >= 300:
        discoveryUrl.close()
        print("Failed to get access token endpoint from discovery URL: {status}:{reason}".
              format(status=discoveryUrl.status_code, reason=discoveryUrl.text))
        raise ValueError

    tokenEndpoint = json.loads(discoveryUrl.content)["token_endpoint"]

    tokenInformation = requests.post(
        tokenEndpoint,
        data={"client_id": destination["client-id"],
              "client_secret": destination["client-secret"],
              "grant_type": "client_credentials"},
        verify=VERIFY_SSL)

    token = json.loads(tokenInformation.content)

    if token is None:
        raise Exception("Failed to retrieve Token")

    __expiration = float(token['expires_in']) + time.time()
    __token = token['access_token']
    return __token


# ************************************************************************
# Helper function: REQUIRED: wrapper function for sending an HTTPS message
# ************************************************************************

# Define a helper function to allow easily sending web request messages;
# this function can later be customized to allow you to port this script to other languages.
# All it does is take in a data object and a message type, and it sends an HTTPS
# request to the target OMF endpoint

def send_message_to_omf_endpoint(destination, message_type, message_omf_json, action='create'):
    '''Sends the request out to the preconfigured endpoint'''
    global destination_types

    # Compress json omf payload, if specified
    compression = 'none'
    if USE_COMPRESSION:
        msg_body = gzip.compress(bytes(json.dumps(message_omf_json), 'utf-8'))
        compression = 'gzip'
    else:
        msg_body = json.dumps(message_omf_json)

    # Collect the message headers
    msg_headers = getHeaders(destination, compression, message_type, action)

    # Send message to OMF endpoint
    destinations_type = destination["destination-type"]
    response = {}
    # If the destination is OCS
    if destinations_type == destination_types[0]:
        response = requests.post(
            destination["omf-endpoint"],
            headers=msg_headers,
            data=msg_body,
            verify=VERIFY_SSL,
            timeout=WEB_REQUEST_TIMEOUT_SECONDS
        )
    # If the destination is EDS
    elif destinations_type == destination_types[1]:
        response = requests.post(
            destination["omf-endpoint"],
            headers=msg_headers,
            data=msg_body,
            timeout=WEB_REQUEST_TIMEOUT_SECONDS
        )
    # If the destination is PI
    elif destinations_type == destination_types[2]:
        response = requests.post(
            destination["omf-endpoint"],
            headers=msg_headers,
            data=msg_body,
            verify=VERIFY_SSL,
            timeout=WEB_REQUEST_TIMEOUT_SECONDS,
            auth=(destination["username"], destination["password"])
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


def getHeaders(destination, compression="", message_type="", action=""):
    '''Assemble headers for sending to the destination's OMF endpoint'''
    global destination_types

    destination_type = destination["destination-type"]

    # If the destination is OCS
    if destination_type == destination_types[0]:
        msg_headers = {
            "Authorization": "Bearer %s" % get_token(destination),
            'producertoken': get_token(destination),
            'messagetype': message_type,
            'action': action,
            'messageformat': 'JSON',
            'omfversion': omfVersion,
            'compression': compression
        }
    # If the destination is EDS
    elif destination_type == destination_types[1]:
        msg_headers = {
            "Content-Type": "application/json",
            'messagetype': message_type,
            'action': action,
            'messageformat': 'JSON',
            'omfversion': omfVersion
        }
        if(compression == "gzip"):
            msg_headers["compression"] = "gzip"
    # If the destination is PI
    elif destination_type == destination_types[1]:
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

'''

def checkValueGone(url):
    # Sends the request out to the preconfigured endpoint..

    global producerToken, sendingToOCS, username, password

    # Assemble headers
    msg_headers = getHeaders()

    # Send the request, and collect the response
    if sendingToOCS:
        response = requests.get(
            url,
            headers=msg_headers,
            verify=VERIFY_SSL,
            timeout=WEB_REQUEST_TIMEOUT_SECONDS
        )
    else:
        response = requests.get(
            url,
            headers=msg_headers,
            verify=VERIFY_SSL,
            timeout=WEB_REQUEST_TIMEOUT_SECONDS,
            auth=(username, password)
        )

    # response code in 200s if the request was successful!
    if response.status_code >= 200 and response.status_code < 300:
        response.close()
        print('Value found.  This is unexpected.  "{0}"'.format(
            response.status_code))
        print()
        opId = response.headers["Operation-Id"]
        status = response.status_code
        reason = response.text
        url = response.url
        error = f"  {status}:{reason}.  URL {url}  OperationId {opId}"
        raise Exception(f"Check message was failed. {error}")
    return response.text


def checkValue(url):
    # Sends the request out to the preconfigured endpoint..

    global producerToken, sendingToOCS, username, password

    # Assemble headers
    msg_headers = getHeaders()

    # Send the request, and collect the response
    if sendingToOCS:
        response = requests.get(
            url,
            headers=msg_headers,
            verify=VERIFY_SSL,
            timeout=WEB_REQUEST_TIMEOUT_SECONDS
        )
    else:
        response = requests.get(
            url,
            headers=msg_headers,
            verify=VERIFY_SSL,
            timeout=WEB_REQUEST_TIMEOUT_SECONDS,
            auth=(username, password)
        )

    # response code in 200s if the request was successful!
    if response.status_code < 200 or response.status_code >= 300:
        response.close()
        print('Response from endpoint was bad.  "{0}"'.format(
            response.status_code))
        print()
        opId = response.headers["Operation-Id"]
        status = response.status_code
        reason = response.text
        url = response.url
        error = f"  {status}:{reason}.  URL {url}  OperationId {opId}"
        raise Exception(f"OMF message was unsuccessful. {error}")
    return response.text


def checkDeletes():
    global checkBase, dataServerName

    print("Check Deletes")
    time.sleep(2)

    if(sendingToOCS):
        checkValueGone(checkBase + '/Streams' + '/Container1')
    else:
        json1 = checkValue(checkBase + "/dataservers?name=" + dataServerName)
        pointsURL = json.loads(json1)['Links']['Points']
        json1 = checkValue(pointsURL + "?nameFilter=container1*")
        links = json.loads(json1)['Links']
        assert len(links) == 0


def checkSends(lastVal):
    global checkBase, dataServerName

    print("Checks")

    if(sendingToOCS):

        # just getting back the type or stream means that it worked
        json1 = checkValue(checkBase + '/Types' + '/FirstDynamicType')
        # print(json1)
        json1 = checkValue(checkBase + '/Streams' + '/Container1')
        # print(json1)
        json1 = checkValue(checkBase + '/Streams' +
                           '/Container1' + '/Data/last')

        # just checking to make sure some data made it it, could do a more comprhensive check but this is ok...
        assert lastVal[0]['values'][0]['IntegerProperty'] == json.loads(json1)[
            'IntegerProperty']

    else:
        # print(json1)
        json1 = checkValue(checkBase + "/dataservers?name=" + dataServerName)
        pointsURL = json.loads(json1)['Links']['Points']

        json1 = checkValue(pointsURL + "?nameFilter=container1*")
        endValueURL = json.loads(json1)['Items'][0]['Links']['Value']

        json1 = checkValue(endValueURL)

        # just checking to make sure some data made it it, could do a more comprhensive check but this is ok...
        assert lastVal[0]['values'][0]['IntegerProperty'] == json.loads(json1)[
            'Value']
'''

# ************************************************************************
# Helper functions: REQUIRED: create a JSON message that contains data values
# for all defined containerids
#
# Note: if you do not send one of the values for the container, Relay
# will emit the default value for missing property - it is the default
# behavior of JSON serialization; this might lead to undesireable
# results: for example, putting a value of zero into referenced PI
# point
# ************************************************************************


def get_current_time():
    ''' Returns the current time'''
    return datetime.datetime.utcnow().isoformat() + 'Z'


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


def get_json_file(filename):
    ''' Get a json file relative to the application's path'''
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
    ''' Return the config.json as a config file, while also populating check_base and omf_endpoint'''
    global destination_types

    # Try to open the configuration file
    destinations = get_json_file("config.json")

    # for each destination construct the check base and OMF endpoint
    for destination in destinations:
        destination_type = destination["destination-type"]

        # If the destination is OCS
        if destination_type == destination_types[0]:
            check_base = f"{destination['resource']}/api/{destination['api-version']}" + \
                f"/tenants/{destination['tenant']}/namespaces/{destination['namespace']}"

        # If the destination is EDS
        elif destination_type == destination_types[1]:
            check_base = f"{destination['resource']}/api/{destination['api-version']}" + \
                f"/tenants/default/namespaces/default"

        # If the destination is PI
        elif destination_type == destination_types[2]:
            check_base = destination["resource"]

        omf_endpoint = f"{check_base}/omf"

        # add the check_base and omf_endpoint to the destination configuration
        destination["check-base"] = check_base
        destination["omf-endpoint"] = omf_endpoint

    return destinations


# ************************************************************************
# Note: PI points will be created on the first data value message
# arrived for a given container
# ************************************************************************


def main(test=False):
    # Main program.  Seperated out so that we can add a test function and call this easily
    global app_path, destinations, destination_types

    success = True

    # get the app_path
    app_path = os.path.dirname(os.path.abspath(__file__))

    if not VERIFY_SSL:
        print("You are not verifying the certificate of the end point.  This is not advised for any system as there are security issues with doing this.")

    # Step 1 - Read destination configurations from config.json
    destinations = get_config()

    # Step 2 - Get OMF Types
    omf_types = get_json_file("OMF-Types.json")

    # Step 3 - Get OMF Containers
    omf_containers = get_json_file("OMF-Containers.json")

    # Step 4 - Get OMF Data
    omf_data = get_json_file("OMF-Data.json")

    # Send messages and check for each destination in config.json
    for destination in destinations:
        try:
            get_token(destination)

            # Step 5 - Send OMF Types
            for omf_type in omf_types:
                send_message_to_omf_endpoint(destination, "type", [omf_type])

            # Step 6 - Send OMF Containers
            for omf_container in omf_containers:
                send_message_to_omf_endpoint(
                    destination, "container", [omf_container])

            # Step 7 - Send OMF Data
            count = 0
            time.sleep(1)
            while count == 0 or ((not test) and count < 2):
                for omf_datum in omf_data:
                    # send the data
                    send_message_to_omf_endpoint(
                        destination, "data", [get_data(omf_datum)])
                time.sleep(1)
                count = count + 1
            
            # Step 8 - Check sends

        except Exception as ex:
            print(("Encountered Error: {error}".format(error=ex)))
            print
            traceback.print_exc()
            print
            success = False
            if test:
                raise ex

        finally:
            # Step 9 - Cleanup
            print('Deletes')

            # delete containers
            for omf_container in omf_containers:
                send_message_to_omf_endpoint(
                    destination, "container", [omf_container], action = 'delete')
            # delete types
            for omf_type in omf_types:
                send_message_to_omf_endpoint(destination, "type", [omf_type], action = 'delete')
            
            #checkDeletes()
            print

    return success


main()
print("done")

# Straightforward test to make sure program is working without an error in program.  Can run it yourself with pytest program.py

def test_main():
    # Tests to make sure the sample runs as expected
    main(True)
