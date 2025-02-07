# Building a Python client to send OMF to PI, EDS or Cds

**Version:** 2.2.0

| Cds Test Status                                                                                                                                                                                                                                                                                                                                                    | EDS Test Status                                                                                                                                                                                                                                                                                                                                                    | PI Test Status                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![Build Status](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_apis/build/status%2Fproduct-readiness%2FOMF%2FAVEVA.sample-omf-basic_api-python?branchName=main&jobName=Tests_ADH)](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_build/latest?definitionId=16160&branchName=main) | [![Build Status](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_apis/build/status%2Fproduct-readiness%2FOMF%2FAVEVA.sample-omf-basic_api-python?branchName=main&jobName=Tests_EDS)](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_build/latest?definitionId=16160&branchName=main) | [![Build Status](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_apis/build/status%2Fproduct-readiness%2FOMF%2FAVEVA.sample-omf-basic_api-python?branchName=main&jobName=Tests_OnPrem)](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_build/latest?definitionId=16160&branchName=main) |

The sample code in this topic demonstrates how to send OMF messages using Python to PI, Edge Data Store (EDS) or CONNECT data services (Cds).

The samples were built and tested against Python 3. If you are using a different version you might encounter errors or unexepected behavior.

## To run this sample:

1. Clone the GitHub repository
2. Install required modules: `pip install -r requirements.txt`
3. Open the folder with your favorite IDE
4. Rename the placeholder config file [appsettings.placeholder.json](appsettings.placeholder.json) to appsettings.json
5. Update appsettings.json with the credentials for the enpoint(s) you want to send to. See [Configure endpoints and authentication](#configure-endpoints-and-authentication) below for additional details
6. Run program.py

## To test this sample:

### Option 1

1. Run test.py

### Option 2

1. Install pytest `pip install pytest`
2. Run `pytest program.py`

## Customizing the application

This application can be customized to send your own custom types, containers, and data by modifying the [OMF-Types.json](OMF-Types.json) [OMF-Containers.json](OMF-Containers.json), and [OMF-Data.json](OMF-Data.json) files respectively. Each one of these files contains an array of OMF json objects, which are created in the endpoints specified in [appsettings.json](appsettings.placeholder.json) when the application is run. For more information on forming OMF messages, please refer to our [OMF version 1.2 documentation](https://docs.aveva.com/bundle/omf/page/1283983.html).

In addition to modifying the json files mentioned above, the get_data function in [program.py](program.py) should be updated to populate the OMF data messages specified in [OMF-Data.json](OMF-Data.json) with data from your data source. Finally, if there are any other activities that you would like to be running continuously, this logic can be added under the while loop in the main() function of [program.py](program.py).

## Configure endpoints and authentication

The sample is configured using the file [appsettings.placeholder.json](appsettings.placeholder.json). Before editing, rename this file to `appsettings.json`. This repository's `.gitignore` rules should prevent the file from ever being checked in to any fork or branch, to ensure credentials are not compromised.

The application can be configured to send to any number of endpoints specified in the endpoints array within appsettings.json. In addition, there are three types of endpoints: [(Cds)](#cds-endpoint-configuration), [EDS](#eds-endpoint-configuration), and [PI](#pi-endpoint-configuration). Each of the 3 types of enpoints are configured differently and their configurations are explained in the sections below.

### Cds endpoint configuration

An OMF ingress client must be configured. On our [Aveva PI System Learning](https://www.youtube.com/channel/UC333r4jIeHaY-rGgMjON54g) Channel on YouTube we have a video on [Creating an OMF Connection](https://www.youtube.com/watch?v=52lAnkGC1IM).

The format of the configuration for a Cds endpoint is shown below along with descriptions of each parameter. Replace all parameters with appropriate values.

```json
{
  "Selected": true,
  "EndpointType": "CDS",
  "Resource": "https://uswe.datahub.connect.aveva.com",
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
| EndpointType             | required | string  | The endpoint type. For Cds this will always be "CDS"                                                                                                             |
| Resource                 | required | string  | The endpoint for the Cds namespace. If the tenant/namespace is located in NA, it is https://uswe.datahub.connect.aveva.com and if in EMEA, it is https://euno.datahub.connect.aveva.com  |
| NamespaceID              | required | string  | The name of the namespace in Cds that is being sent to                                                                                                           |
| Tenant                   | required | string  | The Tenant ID of the Tenant in Cds that is being sent to                                                                                                         |
| ClientId                 | required | string  | The client ID that is being used for authenticating to Cds                                                                                                       |
| ClientSecret             | required | string  | The client secret that is being used for authenticating to Cds                                                                                                   |
| ApiVersion               | required | string  | The API version of the Cds endpoint                                                                                                                              |
| VerifySSL                | optional | boolean | A feature flag for verifying SSL when connecting to the Cds endpoint. By defualt this is set to true as it is strongly recommended that SSL be checked           |
| UseCompression           | optional | boolean | A feature flag for enabling compression on messages sent to the Cds endpoint                                                                                     |
| WebRequestTimeoutSeconds | optional | integer | A feature flag for changing how long it takes for a request to time out                                                                                          |

### EDS endpoint configurations

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
| UseCompression           | optional | boolean | A feature flag for enabling compression on messages sent to the Cds endpoint                                                                      |
| WebRequestTimeoutSeconds | optional | integer | A feature flag for changing how long it takes for a request to time out                                                                           |

### PI endpoint configuration

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
| UseCompression           | optional | boolean        | A feature flag for enabling compression on messages sent to the Cds endpoint                                                                                                                                                                                                            |
| WebRequestTimeoutSeconds | optional | integer        | A feature flag for changing how long it takes for a request to time out                                                                                                                                                                                                                 |

---

For the main OMF basic samples page [ReadMe](https://github.com/AVEVA/sample-omf-basic_api-python/blob/main/README.md)  
For the main OMF samples page [ReadMe](https://github.com/AVEVA/AVEVA-Samples-OMF)  
For the main AVEVA samples page [ReadMe](https://github.com/AVEVA)
