# Building a Python client to send OMF to PI or OCS

**Version:** 1.0.1

| OCS Test Status                                                                                                                                                                                                                                               | PI Test Status                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![Build Status](https://dev.azure.com/osieng/engineering/_apis/build/status/product-readiness/OMF/osisoft.sample-omf-basic_api-python?repoName=osisoft%2Fsample-omf-basic_api-python&branchName=master&jobName=Tests_OCS)](https://dev.azure.com/osieng/engineering/_build/latest?definitionId=2637&repoName=osisoft%2Fsample-omf-basic_api-python&branchName=master) | [![Build Status](https://dev.azure.com/osieng/engineering/_apis/build/status/product-readiness/OMF/osisoft.sample-omf-basic_api-python?repoName=osisoft%2Fsample-omf-basic_api-python&branchName=master&jobName=Tests_OnPrem)](https://dev.azure.com/osieng/engineering/_build/latest?definitionId=2637&repoName=osisoft%2Fsample-omf-basic_api-python&branchName=master) |

The sample code in this topic demonstrates how to send OMF messages using Python.

The samples were built and tested against Python 3. If you are using a different version you might encounter errors or unexepected behavior.


## To Run this Sample:

1. Clone the GitHub repository
1. Install required modules: `pip install -r requirements.txt`
1. Open the folder with your favorite IDE
1. Rename the placeholder config file [config-placeholder.json](config-placeholder.json) to config.json
1. Update config.json with the credentials for the enpoint(s) you want to send to. See [Configure endpoints and authentication](#configure-endpoints-and-authentication) below for additional details
1. Run program.py

## To test the sample after running it:

### Option 1
1. Run test.py

### Option 2

1. Install pytest `pip install pytest`
1. Run `pytest program.py`

## Configure endpoints and authentication

The sample is configured using the file [config-placeholder.json](config-placeholder.json). Before editing, rename this file to `config.json`. This repository's `.gitignore` rules should prevent the file from ever being checked in to any fork or branch, to ensure credentials are not compromised.

The application can be configured to send to any number of endpoints specified in the endpoints array within config.json. In addition, there are three types of endpoints: [OCS](#ocs-endpoint-configuration), [EDS](#eds-endpoint-configuration), and [PI](#pi-endpoint-configuration). Each of the 3 types of enpoints are configured differently and their configurations are explained in the sections below.

### OCS Endpoint Configuration
The format of the configuration for an OCS endpoint is shown below along with descriptions of each parameter. Replace all parameters with appropriate values.

```json
{
  "endpoint-type": "OCS",
  "resource": "https://dat-b.osisoft.com",
  "namespace": "REPLACE_WITH_NAMESPACE_NAME",
  "tenant": "RPLACE_WITH_TENANT_ID",
  "client-id": "REPLACE_WITH_APPLICATION_IDENTIFIER",
  "client-secret": "REPLACE_WITH_APPLICATION_SECRET",
  "api-version": "v1",
  "verify-ssl": true,
  "use-compression": false,
  "web-request-timeout-seconds": 30
}
```

| Parameters                  | Required | Type    | Description                                                                                                                                                      |
| --------------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| endpoint-type               | required | string  | The endpoint type. For OCS this will always be "OCS"                                                                                                             |
| resource                    | required | string  | The endpoint for OCS if the namespace. If the tenant/namespace is located in NA, it is https://dat-b.osisoft.com and if in EMEA, it is https://dat-d.osisoft.com |
| namespace                   | required | string  | The name of the Namespace in OCS that is being sent to                                                                                                           |
| tenant                      | required | string  | The Tenant ID of the Tenant in OCS that is being sent to                                                                                                         |
| client-id                   | required | string  | The client ID that is being used for authenticating to OCS                                                                                                       |
| client-secret               | required | string  | The client secret that is being used for authenticating to OCS                                                                                                   |
| api-version                 | required | string  | The API version of the OCS endpoint                                                                                                                              |
| verify-ssl                  | optional | boolean | A feature flag for verifying SSL when connecting to the OCS endpoint. By defualt this is set to true as it is strongly recommended that SSL be checked           |
| use-compression             | optional | boolean | A feature flag for enabling compression on messages sent to the OCS endpoint                                                                                      |
| web-request-timeout-seconds | optional | integer | An optional timeout setting for web requests                                                                                                                     |


### EDS Endpoint Configurations
The format of the configuration for an EDS endpoint is shown below along with descriptions of each parameter. Replace all parameters with appropriate values.

```json
{
  "endpoint-type": "EDS",
  "resource": "http://localhost:5590",
  "api-version": "v1",
  "use-compression": false,
  "web-request-timeout-seconds": 30
}
```

| Parameters                  | Required | Type    | Description                                                                                                                                       |
| --------------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| endpoint-type               | required | string  | The endpoint type. For EDS this will always be "EDS"                                                                                              |
| resource                    | required | string  | The endpoint for EDS if the namespace. If EDS is being run on your local machine with the default configuration, it will be http://localhost:5590 |
| api-version                 | required | string  | The API version of the EDS endpoint                                                                                                               |
| use-compression             | optional | boolean | A feature flag for enabling compression on messages sent to the OCS endpoint                                                                       |
| web-request-timeout-seconds | optional | integer | An optional timeout setting for web requests   


### PI Endpoint Configuration
The format of the configuration for a PI endpoint is shown below along with descriptions of each parameter. Replace all parameters with appropriate values.

```json
{
  "endpoint-type": "PI",
  "resource": "REPLACE_WITH_PI_WEB_API_URL",
  "data-server-name": "REPLACE_WITH_DATA_ARCHIVE_NAME",
  "username": "REPLACE_WITH_USERNAME",
  "password": "REPLACE_WITH_PASSWORD",
  "verify-ssl": "REPLACE",
  "use-compression": false,
  "web-request-timeout-seconds": 30
}
```

| Parameters                  | Required | Type           | Description                                                                                                                                                      |
| --------------------------- | -------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| endpoint-type               | required | string         | The endpoint type. For PI this will always be "PI"                                                                                                             |
| resource                    | required | string         | The URL of the PI Web API                                                                                                                                        |
| data-server-name            | required | string         | The name of the PI Data Archive that is being sent to                                                                                                           |
| username                    | required | string         | The username that is being used for authenticating to the PI Web API                                                                                                       |
| password                    | required | string         | The password that is being used for authenticating to the PI Web API                                                                                                                                                                                                                    |
| verify-ssl                  | optional | boolean        | A feature flag for verifying SSL when connecting to the PI Web API. Alternatively, this can specify the path to a .pem certificate file if a self-signed certificate is being used by the PI Web API. By defualt this is set to true as it is strongly recommended that SSL be checked. |
| use-compression             | optional | boolean/string | A feature flag for enabling compression on messages sent to the OCS endpoint                                                                                                               |
| web-request-timeout-seconds | optional | integer        | An optional timeout setting for web requests                                                                                                                     |


The SDS Service is secured by obtaining tokens from Azure Active Directory. Such clients provide a client application identifier and an associated secret (or key) that are authenticated against the directory. You must replace the placeholders in your `config.ini` file with the authentication-related values you received from OSIsoft.

The values to be replaced are in `config.ini`:

```ini
[Configurations]
Namespace = Samples

[Access]
Resource = https://dat-b.osisoft.com
Tenant = REPLACE_WITH_TENANT_ID
ApiVersion = v1

[Credentials]
ProducerToken = REPLACE_WITH_TOKEN_STRING
ClientId = REPLACE_WITH_APPLICATION_IDENTIFIER
ClientSecret = REPLACE_WITH_APPLICATION_SECRET
```

The PIServer will use the PI Web API as its OMF accepting endpoint. This is what the sample is tested against. Currently the only OMF supported endpoint for PI is the Connector Relay. These samples have not been tested against this.

To configure the sample to work against PI update the `config.ini` to have only these parameters and update that parameter values to what is being used.

Note: the tenantId is used to autodetect if you are going against OCS or PI, so make sure that is removed if going against PI.

```ini
[Configurations]
DataServerName = REPLACE_WITH_PI_DATA_ARCHIVE_NAME

[Access]
Resource = REPLACE_WITH_PI_WEB_API_URL
```

See the general readme for information on setting up your endpoint.

If your client computer Python does not trust the PI Web API certificate you will see an error like:

```shell
requests.exceptions.SSLError: HTTPSConnectionPool(host='...', port=443): Max retries exceeded with url: /piwebapi/omf (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate (_ssl.c:1051)')))
```

---

For the main OMF basic samples page on master [ReadMe](https://github.com/osisoft/OSI-Samples-OMF/blob/master/docs/OMF_BASIC_README.md)  
For the main OMF samples page on master [ReadMe](https://github.com/osisoft/OSI-Samples-OMF)  
For the main OSIsoft samples page on master [ReadMe](https://github.com/osisoft/OSI-Samples)
