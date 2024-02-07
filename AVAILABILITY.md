# Get Availability

This tool extracts referee availability from Assignr, and repackages it for offline use.

This tool is meant for assignors who refuse to enter the 21st century preferring to use spreadsheets to assign games while avoiding the need to tracking referee availability via email.

Again, this offering is less than ideal as games scheduled outside of Assignr need to be imported into Assignr.


## Setup

### Python setup
* create a virtualenv
    * `python3 -m venv <virtual env name> or
    * `virtualenv <virtual env name>
* source ./<virtual env name>/bin/activate (Linux/Mac)
* run `pip install -r requirements-availability.txt`

### Environment Setup
* copy `env.availability` to `.env`
* change `FILE_NAME` to point to the csv file listing the referees to process.

The csv file used three columns: 'first name', 'last name', and 'id'. The 'id' is the Assignr id for the referee. It can be determined from the url of the user, or from official export.

| Environment Variable | Description |
| -------------------- | ----------- |
| `AUTH_URL`       | Assignr Authorization URL. Value is usually "https://app.assignr.com/oauth/token" |
| `BASE_URL`       | Base URL for Assignr API calls. Usually set to "https://api.assignr.com/api/v2" |
| `CLIENT_ID`      | Assignr client id used for API authentication. |
| `CLIENT_SECRET`  | Assignr client secret used for API authentication. |
| `CLIENT_SCOPE`   | Assignr scope assigned to the API. Valid values are 'read write and bank'. |
| `FILE_NAME`      | Location of referee csv file containing what referees to process. |
| `LOG_LEVEL`      | Logging Level, values are 10=Debug, 20=, 30=Info. Default is 30. |
| `REDIRECT_URI`   | Assignr uri. Default is "urn:ietf:wg:oauth:2.0:oob" |

**URL method:**

Select the referee from the user listing page. The numeric field at the end of the url is the 'id'. Example: 'https://cysl.assignr.com/users/1234567', id is 1234567.

**Official Report Export:** 

1. Scroll to the bottom of the user listing page.
1. Select Officials Only

The last column of the export contains the 'id' value.


## Script Execution
`python availability.py -s <start date> -e <end date>`

