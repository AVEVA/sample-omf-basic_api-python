# Building a Python client to send OMF to PI or OCS

**Version:** 2.0.6

| OCS Test Status                                                                                                                                                                                                                                                                                                                                                    | EDS Test Status                                                                                                                                                                                                                                                                                                                                                    | PI Test Status                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![Build Status](https://dev.azure.com/osieng/engineering/_apis/build/status/product-readiness/OMF/osisoft.sample-omf-basic_api-python?repoName=osisoft%2Fsample-omf-basic_api-python&branchName=main&jobName=Tests_OCS)](https://dev.azure.com/osieng/engineering/_build/latest?definitionId=2637&repoName=osisoft%2Fsample-omf-basic_api-python&branchName=main) | [![Build Status](https://dev.azure.com/osieng/engineering/_apis/build/status/product-readiness/OMF/osisoft.sample-omf-basic_api-python?repoName=osisoft%2Fsample-omf-basic_api-python&branchName=main&jobName=Tests_EDS)](https://dev.azure.com/osieng/engineering/_build/latest?definitionId=2637&repoName=osisoft%2Fsample-omf-basic_api-python&branchName=main) | [![Build Status](https://dev.azure.com/osieng/engineering/_apis/build/status/product-readiness/OMF/osisoft.sample-omf-basic_api-python?repoName=osisoft%2Fsample-omf-basic_api-python&branchName=main&jobName=Tests_OnPrem)](https://dev.azure.com/osieng/engineering/_build/latest?definitionId=2637&repoName=osisoft%2Fsample-omf-basic_api-python&branchName=main) |

The sample code in this topic demonstrates how to send OMF messages using Python.

The samples were built and tested against Python 3. If you are using a different version you might encounter errors or unexepected behavior.

## To Run this Sample:

1. Clone the GitHub repository
1. Install required modules: `pip install -r requirements.txt`
1. Open the folder with your favorite IDE
1. Rename the placeholder config file [appsettings.placeholder.json](appsettings.placeholder.json) to appsettings.json
1. Update appsettings.json with the credentials for the enpoint(s) you want to send to. See [Configure endpoints and authentication](#configure-endpoints-and-authentication) below for additional details
1. Run program.py

## To Test this Sample:

### Option 1

1. Run test.py

### Option 2

1. Install pytest `pip install pytest`
1. Run `pytest program.py`

## Customizing the Application

This application can be customized to send your own custom types, containers, and data by modifying the [OMF-Types.json](OMF-Types.json) [OMF-Containers.json](OMF-Containers.json), and [OMF-Data.json](OMF-Data.json) files respectively. Each one of these files contains an array of OMF json objects, which are created in the endpoints specified in [appsettings.json](appsettings.placeholder.json) when the application is run. For more information on forming OMF messages, please refer to our [OMF version 1.1 documentation](https://omf-docs.osisoft.com/documentation_v11/Whats_New.html).

In addition to modifying the json files mentioned above, the get_data function in [program.py](program.py) should be updated to populate the OMF data messages specified in [OMF-Data.json](OMF-Data.json) with data from your data source. Finally, if there are any other activities that you would like to be running continuously, this logic can be added under the while loop in the main() function of [program.py](program.py).

## Configure Endpoints and Authentication

The sample is configured using the file [appsettings.placeholder.json](appsettings.placeholder.json). Before editing, rename this file to `appsettings.json`. This repository's `.gitignore` rules should prevent the file from ever being checked in to any fork or branch, to ensure credentials are not compromised.

The application can be configured to send to any number of endpoints specified in the endpoints array within appsettings.json. In addition, there are three types of endpoints: [OCS](#ocs-endpoint-configuration), [EDS](#eds-endpoint-configuration), and [PI](#pi-endpoint-configuration). Each of the 3 types of enpoints are configured differently and their configurations are explained in the sections below.

### OCS Endpoint Configuration

An OMF ingress client must be configured. On our [OSIsoft Learning](https://www.youtube.com/channel/UC333r4jIeHaY-rGgMjON54g) Channel on YouTube we have a video on [Ceating an OMF Connection](https://www.youtube.com/watch?v=52lAnkGC1IM).

The format of the configuration for an OCS endpoint is shown below along with descriptions of each parameter. Replace all parameters with appropriate values.

```json
{
  "Selected": true,
  "EndpointType": "OCS",
  "Resource": "https://dat-b.osisoft.com",
  "NamespaceId": "PLACEHOLDER_REPLACE_WITH_NAMESPACE_ID",
  "Tenant": "PLACEHOLDER_REPLACE_WITH_TENANT_ID",
  "clientId": "PLACEHOLDER_REPLACE_WITH_CLIENT_ID",
  "ClientSecret": "PLACEHOLDER_REPLACE_WITH_CLIENT_SECRET",
  "ApiVersion": "v1",
  "VerifySSL": true,
  "UseCompression": false,
  "WebRequestTimeoutSeconds": 30
}
```

| Parameters               | Required | Type    | Description                                                                                                                                                      |
| ------------------------ | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Selected                 | required | boolean | Tells the application if the endpoint should be sent to                                                                                                          |
| EndpointType             | required | string  | The endpoint type. For OCS this will always be "OCS"                                                                                                             |
| Resource                 | required | string  | The endpoint for OCS if the namespace. If the tenant/namespace is located in NA, it is https://dat-b.osisoft.com and if in EMEA, it is https://dat-d.osisoft.com |
| NamespaceID              | required | string  | The name of the Namespace in OCS that is being sent to                                                                                                           |
| Tenant                   | required | string  | The Tenant ID of the Tenant in OCS that is being sent to                                                                                                         |
| ClientId                 | required | string  | The client ID that is being used for authenticating to OCS                                                                                                       |
| ClientSecret             | required | string  | The client secret that is being used for authenticating to OCS                                                                                                   |
| ApiVersion               | required | string  | The API version of the OCS endpoint                                                                                                                              |
| VerifySSL                | optional | boolean | A feature flag for verifying SSL when connecting to the OCS endpoint. By defualt this is set to true as it is strongly recommended that SSL be checked           |
| UseCompression           | optional | boolean | A feature flag for enabling compression on messages sent to the OCS endpoint                                                                                     |
| WebRequestTimeoutSeconds | optional | integer | A feature flag for changing how long it takes for a request to time out                                                                                          |

### EDS Endpoint Configurations

The format of the configuration for an EDS endpoint is shown below along with descriptions of each parameter. Replace all parameters with appropriate values.

```json
{
  "Selected": true,
  "EndpointType": "EDS",
  "Resource": "http://localhost:5590",
  "ApiVersion": "v1",
  "UseCompression": false
}
```

| Parameters               | Required | Type    | Description                                                                                                                                       |
| ------------------------ | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Selected                 | required | boolean | Tells the application if the endpoint should be sent to                                                                                           |
| EndpointType             | required | string  | The endpoint type. For EDS this will always be "EDS"                                                                                              |
| Resource                 | required | string  | The endpoint for EDS if the namespace. If EDS is being run on your local machine with the default configuration, it will be http://localhost:5590 |
| ApiVersion               | required | string  | The API version of the EDS endpoint                                                                                                               |
| UseCompression           | optional | boolean | A feature flag for enabling compression on messages sent to the OCS endpoint                                                                      |
| WebRequestTimeoutSeconds | optional | integer | A feature flag for changing how long it takes for a request to time out                                                                           |

### PI Endpoint Configuration

The format of the configuration for a PI endpoint is shown below along with descriptions of each parameter. Replace all parameters with appropriate values.

```json
{
  "Selected": true,
  "EndpointType": "PI",
  "Resource": "PLACEHOLDER_REPLACE_WITH_PI_WEB_API_URL",
  "DataArchiveName": "PLACEHOLDER_REPLACE_WITH_DATA_ARCHIVE_NAME",
  "Username": "PLACEHOLDER_REPLACE_WITH_USERNAME",
  "Password": "PLACEHOLDER_REPLACE_WITH_PASSWORD",
  "VerifySSL": true,
  "UseCompression": false
}
```

| Parameters               | Required | Type           | Description                                                                                                                                                                                                                                                                             |
| ------------------------ | -------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Selected                 | required | boolean        | Tells the application if the endpoint should be sent to                                                                                                                                                                                                                                 |
| EndpointType             | required | string         | The endpoint type. For PI this will always be "PI"                                                                                                                                                                                                                                      |
| Resource                 | required | string         | The URL of the PI Web API                                                                                                                                                                                                                                                               |
| DataArchiveName          | required | string         | The name of the PI Data Archive that is being sent to                                                                                                                                                                                                                                   |
| Username                 | required | string         | The username that is being used for authenticating to the PI Web API                                                                                                                                                                                                                    |
| Password                 | required | string         | The password that is being used for authenticating to the PI Web API                                                                                                                                                                                                                    |
| VerifySSL                | optional | boolean/string | A feature flag for verifying SSL when connecting to the PI Web API. Alternatively, this can specify the path to a .pem certificate file if a self-signed certificate is being used by the PI Web API. By defualt this is set to true as it is strongly recommended that SSL be checked. |
| UseCompression           | optional | boolean        | A feature flag for enabling compression on messages sent to the OCS endpoint                                                                                                                                                                                                            |
| WebRequestTimeoutSeconds | optional | integer        | A feature flag for changing how long it takes for a request to time out                                                                                                                                                                                                                 |

---

For the main OMF basic samples page [ReadMe](https://github.com/osisoft/OSI-Samples-OMF/blob/main/docs/OMF_BASIC_README.md)  
For the main OMF samples page [ReadMe](https://github.com/osisoft/OSI-Samples-OMF)  
For the main OSIsoft samples page [ReadMe](https://github.com/osisoft/OSI-Samples)
