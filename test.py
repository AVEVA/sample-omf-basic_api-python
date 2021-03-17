import unittest
import traceback
import requests
import json
import os
from program import main, get_headers, endpoint_types, app_path,\
    endpoints, get_json_file, send_message_to_omf_endpoint, get_config


class ProgramTestCase(unittest.TestCase):
    def test_main(self):
        success = True
        if not main(True):
            success = False
        if not check_creations(self):
            success = False
        if not cleanup(self):
            success = False

        self.assertTrue(success)


def check_creations(self):
    global endpoints, app_path

    app_path = os.path.dirname(os.path.abspath(__file__))
    endpoints = get_config()
    omf_types = get_json_file("OMF-Types.json")
    omf_containers = get_json_file("OMF-Containers.json")
    omf_data = get_json_file("OMF-Data.json")

    # Step 8 - Check Creations
    print('Check')
    success = True
    for endpoint in endpoints:
        try:
            endpoint_type = endpoint["endpoint-type"]

            if endpoint_type == endpoint_types[2]:
                # get point URLs
                response = send_get_request_to_endpoint(
                    endpoint, path=f"/dataservers?name={endpoint['data-server-name']}")
                points_URL = json.loads(response.text)['Links']['Points']

                # get point data and check response
                for omf_container in omf_containers:
                    response = send_get_request_to_endpoint(
                        endpoint, base=points_URL, path=f"?nameFilter={omf_container['id']}*")
                    # get end value URLs
                    end_value_URL = json.loads(response.text)[
                        'Items'][0]['Links']['Value']
                    # retrieve data
                    response = send_get_request_to_endpoint(
                        endpoint, base=end_value_URL)
                    end_value = json.loads(response.text)["Value"]
                    # check that the response was good and that data was written to the point
                    if response.status_code < 200 or response.status_code >= 300:
                        success = False
                    if isinstance(end_value, dict) and "Name" in end_value and end_value["Name"] == "Pt Created":
                        success = False

            else:
                # retrieve types and check response
                for omf_type in omf_types:
                    response = send_get_request_to_endpoint(
                        endpoint, path=f"/Types/{omf_type['id']}")
                    if response.status_code < 200 or response.status_code >= 300:
                        success = False

                # retrieve containers and check response
                for omf_container in omf_containers:
                    response = send_get_request_to_endpoint(
                        endpoint, path=f"/Streams/{omf_container['id']}")
                    if response.status_code < 200 or response.status_code >= 300:
                        success = False

                # retrieve the most recent data and check response
                for omf_datum in omf_data:
                    response = send_get_request_to_endpoint(
                        endpoint, path=f"/Streams/{omf_datum['containerid']}/Data/last")
                    if response.text == "":
                        success = False

        except Exception as ex:
            print(("Encountered Error: {error}".format(error=ex)))
            print
            traceback.print_exc()
            print
            success = False
            raise ex

    return success


def cleanup(self):
    global endpoints, app_path

    app_path = os.path.dirname(os.path.abspath(__file__))
    endpoints = get_config()
    omf_types = get_json_file("OMF-Types.json")
    omf_containers = get_json_file("OMF-Containers.json")

    # Step 9 - Cleanup
    print('Deletes')
    success = True
    for endpoint in endpoints:
        try:
            # delete containers
            for omf_container in omf_containers:
                send_message_to_omf_endpoint(
                    endpoint, "container", [omf_container], action='delete')

            # delete types
            for omf_type in omf_types:
                send_message_to_omf_endpoint(
                    endpoint, "type", [omf_type], action='delete')

        except Exception as ex:
            print(("Encountered Error: {error}".format(error=ex)))
            print
            traceback.print_exc()
            print
            success = False
            raise ex

    return success


def send_get_request_to_endpoint(endpoint, path="", base=""):
    '''Sends the get request to the path relative to the base base and returns the response'''
    global endpoint_types

    if base == "":
        base = endpoint["base-endpoint"]

    # Collect the message headers
    msg_headers = get_headers(endpoint)

    # Send message to base base
    endpoints_type = endpoint["endpoint-type"]
    response = {}
    # If the endpoint is OCS
    if endpoints_type == endpoint_types[0]:
        response = requests.get(
            base+path,
            headers=msg_headers,
            verify=endpoint["verify-ssl"],
            timeout=endpoint["web-request-timeout-seconds"]
        )
    # If the endpoint is EDS
    elif endpoints_type == endpoint_types[1]:
        response = requests.get(
            base+path,
            headers=msg_headers,
            timeout=endpoint["web-request-timeout-seconds"]
        )
    # If the endpoint is PI
    elif endpoints_type == endpoint_types[2]:
        response = requests.get(
            base+path,
            headers=msg_headers,
            verify=endpoint["verify-ssl"],
            timeout=endpoint["web-request-timeout-seconds"],
            auth=(endpoint["username"], endpoint["password"])
        )

    return(response)


if __name__ == "__main__":
    unittest.main()
