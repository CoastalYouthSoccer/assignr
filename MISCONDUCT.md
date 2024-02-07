# Misconduct Report

This tool checks for Misconducts in the Game reports the requested time frame sending an email to those interested in the information.

This tool is best scheduled so those interested don't need to run it.


## Setup

### Python setup
* create a virtualenv
    * `python3 -m venv <virtual env name> or
    * `virtualenv <virtual env name>
* source ./<virtual env name>/bin/activate (Linux/Mac)
* run `pip install -r requirements-misconduct.txt`

### Environment Setup
* copy `env.misconduct` to `.env`
* change variable values as needed.

| Environment Variable | Description |
| -------------------- | ----------- |
| `AUTH_URL`       | Assignr Authorization URL. Value is usually "https://app.assignr.com/oauth/token" |
| `BASE_URL`       | Base URL for Assignr API calls. Usually set to "https://api.assignr.com/api/v2" |
| `CLIENT_ID`      | Assignr client id used for API authentication. |
| `CLIENT_SECRET`  | Assignr client secret used for API authentication. |
| `CLIENT_SCOPE`   | Assignr scope assigned to the API. Valid values are 'read write and bank'. |
| `EMAIL_PASSWORD` | Password used to authenticate to the email server. |
| `EMAIL_PORT`     | Port used to connect to the email server. Default is '587'. |
| `EMAIL_SERVER`   | Email server host name or IP. Defaults to 'smtp.gmail.com'. |
| `EMAIL_TO`       | Email address(es) to send the report. Use commas to separate multiple email addresses. Email address format is "<Homer Simpson>homer@simpsons.com,<Marge Simpson>marge@simpsons.com". |
| `EMAIL_USERNAME` | User name used to authenticate to the email server. |
| `GOOGLE_APPLICATION_CREDENTIALS` | google json credential file location |
| `LOG_LEVEL`      | Logging Level, values are 10=Debug, 20=, 30=Info. Default is 30. |
| `REDIRECT_URI`   | Assignr uri. Default is "urn:ietf:wg:oauth:2.0:oob" |
| `SPREADSHEET_ID` | Google spreadsheet id containing Coach mappings. |
| `SPREADSHEET_RANGE` | Range for Coach mapping spreadsheet. Format is "<sheet name>!A:D" |

### Coach Mapping Spreadsheet

The Game Report includes who the coaches were. To fulfill this feature, the script reads a spreadsheet containing this information.

The spreadsheet format is: "Age Group	Gender	Team	Coaches"

## Script Execution
`python misconduct.py -s <start date> -e <end date>`

