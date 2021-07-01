import unittest
import traceback
import requests
import json
import os
from program import main, get_headers, endpoints, EndpointTypes,\
    get_json_file, send_message_to_omf_endpoint, get_config


class ProgramTestCase(unittest.TestCase):
    def test_main(self):
        # Steps 1 to 7 - Run the main program
        sent_data = {}
        self.assertTrue(main(True, sent_data))
        # Step 8 - Check Creations
        self.assertTrue(check_creations(self, sent_data))
        # Step 9 - Cleanup
        self.assertTrue(cleanup(self))


def check_creations(self, sent_data):
    global endpoints

    endpoints = get_config()
    omf_types = get_json_file('OMF-Types.json')
    omf_containers = get_json_file('OMF-Containers.json')
    omf_data = get_json_file('OMF-Data.json')

    # Step 8 - Check Creations
    print('Check')
    success = True
    for endpoint in endpoints:
        try:
            endpoint_type = endpoint["endpoint-type"]

            if endpoint_type == EndpointTypes.PI.value:
                # get point URLs
                response = send_get_request_to_endpoint(
                    endpoint, path=f'/dataservers?name={endpoint["data-server-name"]}')
                points_url = response.json()["Links"]["Points"]

                # get point data and check response
                for omf_container in omf_containers:
                    response = send_get_request_to_endpoint(
                        endpoint, base=points_url, path=f'?nameFilter={omf_container["id"]}*')
                    # get end value URLs
                    for item in response.json()["Items"]:
                        end_value_url = item["Links"]["Value"]
                        # retrieve data
                        response = send_get_request_to_endpoint(
                            endpoint, base=end_value_url)
                        end_value = response.json()["Value"]
                        # check that the response was good and that data was written to the point
                        if response.status_code < 200 or response.status_code >= 300:
                            print(f'Unable to find item {item}')
                            success = False
                        elif isinstance(end_value, dict) and "Name" in end_value and end_value["Name"] == 'Pt Created':
                            print(f'Item {item} has no recorded data')
                            success = False
                        # compare the returned data to what was sent
                        if not compare_data(item["Name"], end_value, sent_data[omf_container["id"]]):
                            print(
                                f'Data in item {item} does match what was sent')
                            success = False

            else:
                # retrieve types and check response
                for omf_type in omf_types:
                    response = send_get_request_to_endpoint(
                        endpoint, path=f'/Types/{omf_type["id"]}')
                    if response.status_code < 200 or response.status_code >= 300:
                        print(f'Unable to find type {omf_type}')
                        success = False

                # retrieve containers and check response
                for omf_container in omf_containers:
                    response = send_get_request_to_endpoint(
                        endpoint, path=f'/Streams/{omf_container["id"]}')
                    if response.status_code < 200 or response.status_code >= 300:
                        print(f'Unable to find continer {omf_container}')
                        success = False

                # retrieve the most recent data, check the response, and compare the data to what was sent
                for omf_datum in omf_data:
                    response = send_get_request_to_endpoint(
                        endpoint, path=f'/Streams/{omf_datum["containerid"]}/Data/last')
                    if response.text == '' or (response.status_code < 200 or response.status_code >= 300):
                        print(f'Unable to find data {omf_datum}')
                        success = False
                    elif not compare_data('SDS', response.json(), sent_data[omf_datum["containerid"]]):
                        print(
                            f'Data in {omf_datum} does not match what was sent')
                        success = False

        except Exception as ex:
            print(f'Encountered Error: {ex}')
            print
            traceback.print_exc()
            print
            success = False
            raise ex

    return success


def cleanup(self):
    global endpoints

    endpoints = get_config()
    omf_types = get_json_file('OMF-Types.json')
    omf_containers = get_json_file('OMF-Containers.json')

    # Step 9 - Cleanup
    print('Deletes')
    success = True
    for endpoint in endpoints:
        try:
            # delete containers
            for omf_container in omf_containers:
                send_message_to_omf_endpoint(
                    endpoint, 'container', [omf_container], action='delete')

            # delete types
            for omf_type in omf_types:
                send_message_to_omf_endpoint(
                    endpoint, 'type', [omf_type], action='delete')

        except Exception as ex:
            print(f'Encountered Error: {ex}')
            print
            traceback.print_exc()
            print
            success = False
            raise ex

    return success


def send_get_request_to_endpoint(endpoint, path='', base=''):
    '''Sends the get request to the path relative to the base base and returns the response'''

    if base == '':
        base = endpoint["base-endpoint"]

    # Collect the message headers
    msg_headers = get_headers(endpoint)
    msg_headers.pop('omfversion')
    msg_headers["Accept-Verbosity"] = 'verbose'

    # Send message to base base
    endpoints_type = endpoint["endpoint-type"]
    response = {}
    # If the endpoint is OCS
    if endpoints_type == EndpointTypes.OCS.value:
        response = requests.get(
            base+path,
            headers=msg_headers,
            verify=endpoint["verify-ssl"],
            timeout=endpoint["web-request-timeout-seconds"]
        )
    # If the endpoint is EDS
    elif endpoints_type == EndpointTypes.EDS.value:
        response = requests.get(
            base+path,
            headers=msg_headers,
            timeout=endpoint["web-request-timeout-seconds"]
        )
    # If the endpoint is PI
    elif endpoints_type == EndpointTypes.PI.value:
        response = requests.get(
            base+path,
            headers=msg_headers,
            verify=endpoint["verify-ssl"],
            timeout=endpoint["web-request-timeout-seconds"],
            auth=(endpoint["username"], endpoint["password"])
        )

    return(response)


def compare_data(data_format, response, sent_data):
    '''A helper function for comparing the data returned by either the PI Web API or the SDS'''
    success = True
    if data_format == 'SDS':
        for key in sent_data["values"][0]:
            if key != "Timestamp" and sent_data["values"][0][key] != response[key]:
                success = False
    else:
        split = data_format.split('.')
        if len(split) == 2:
            prop = split[1]
            for key in sent_data["values"][0]:
                if key == prop and sent_data["values"][0][key] != response:
                    success = False
        else:
            for key in sent_data["values"][0]:
                if key != "Timestamp" and sent_data["values"][0][key] != response:
                    success = False

    return success


if __name__ == '__main__':
    unittest.main()
