import unittest
import traceback
import requests
import json
import os
from program import main, get_headers, destination_types, app_path,\
    destinations, get_json_file, send_message_to_omf_endpoint, get_config


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
    global destinations, app_path

    app_path = os.path.dirname(os.path.abspath(__file__))
    destinations = get_config()
    omf_types = get_json_file("OMF-Types.json")
    omf_containers = get_json_file("OMF-Containers.json")
    omf_data = get_json_file("OMF-Data.json")

    # Step 8 - Check Creations
    print('Check')
    success = True
    for destination in destinations:
        try:
            destination_type = destination["destination-type"]

            if destination_type == destination_types[2]:
                # get point URLs
                response = send_get_request_to_endpoint(
                    destination, path=f"/dataservers?name={destination['data-server-name']}")
                points_URL = json.loads(response.text)['Links']['Points']

                # get point data and check response
                for omf_container in omf_containers:
                    response = send_get_request_to_endpoint(
                        destination, endpoint=points_URL, path=f"?nameFilter={omf_container['id']}*")
                    # get end value URLs
                    end_value_URL = json.loads(response.text)[
                        'Items'][0]['Links']['Value']
                    # retrieve data
                    response = send_get_request_to_endpoint(
                        destination, endpoint=end_value_URL)
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
                        destination, path=f"/Types/{omf_type['id']}")
                    if response.status_code < 200 or response.status_code >= 300:
                        success = False

                # retrieve containers and check response
                for omf_container in omf_containers:
                    response = send_get_request_to_endpoint(
                        destination, path=f"/Streams/{omf_container['id']}")
                    if response.status_code < 200 or response.status_code >= 300:
                        success = False

                # retrieve the most recent data and check response
                for omf_datum in omf_data:
                    response = send_get_request_to_endpoint(
                        destination, path=f"/Streams/{omf_datum['containerid']}/Data/last")
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
    global destinations, app_path

    app_path = os.path.dirname(os.path.abspath(__file__))
    destinations = get_config()
    omf_types = get_json_file("OMF-Types.json")
    omf_containers = get_json_file("OMF-Containers.json")

    # Step 9 - Cleanup
    print('Deletes')
    success = True
    for destination in destinations:
        try:
            # delete containers
            for omf_container in omf_containers:
                send_message_to_omf_endpoint(
                    destination, "container", [omf_container], action='delete')

            # delete types
            for omf_type in omf_types:
                send_message_to_omf_endpoint(
                    destination, "type", [omf_type], action='delete')

        except Exception as ex:
            print(("Encountered Error: {error}".format(error=ex)))
            print
            traceback.print_exc()
            print
            success = False
            raise ex

    return success


def send_get_request_to_endpoint(destination, path="", endpoint=""):
    '''Sends the get request to the path relative to the base endpoint and returns the response'''
    global destination_types

    if endpoint == "":
        endpoint = destination["base-endpoint"]

    # Collect the message headers
    msg_headers = get_headers(destination)

    # Send message to base endpoint
    destinations_type = destination["destination-type"]
    response = {}
    # If the destination is OCS
    if destinations_type == destination_types[0]:
        response = requests.get(
            endpoint+path,
            headers=msg_headers,
            verify=destination["verify-ssl"],
            timeout=destination["web-request-timeout-seconds"]
        )
    # If the destination is EDS
    elif destinations_type == destination_types[1]:
        response = requests.get(
            endpoint+path,
            headers=msg_headers,
            timeout=destination["web-request-timeout-seconds"]
        )
    # If the destination is PI
    elif destinations_type == destination_types[2]:
        response = requests.get(
            endpoint+path,
            headers=msg_headers,
            verify=destination["verify-ssl"],
            timeout=destination["web-request-timeout-seconds"],
            auth=(destination["username"], destination["password"])
        )

    return(response)


if __name__ == "__main__":
    unittest.main()
