# Assignr Tools

This repo hosts CYSL tools specific to the Assignr SAAS product.

Each tool is defined and described in their respective directory.

## Available Tools

[Delete Games in Bulk](delete_games/README.md)

[Referee Availability](availability/README.md)

## Setup

These tools leverage Assignr's API thus requiring API Keys issued by Assignr. Entering user credentials (user id, and password) won't work. You must request developer API keys from Assignr support.

[Assignr API Documentation](https://assignr-api.readme.io/reference/access-to-the-api)

Each tool directory includes a `sample.env`with the environment variables needed to properly run the code. Most of the variables relate to connecting to Assignr's API.

Protect the values of `CLIENT_SECRET` and `CLIENT_ID`. **DO NOT** save these in a public place such as Github.

The steps below are generic and apply to most tools since tools are written in Python. 

### Python Setup
* change directory to the desired tool
* create a virtualenv
 
 ```
 
 Most    * `python3 -m venv <virtual env name> or
    * `virtualenv <virtual env name>
* source ./<virtual env name>/bin/activate (Linux/Mac)
* run `pip install -r requirements`

### Environment Setup
* copy `sample.env` to `.env`
* replace sample values with proper values.

Sample .env file:
```bash
CLIENT_SECRET="client secret"
CLIENT_ID="client id"
# Valid values are 'read write and bank'
CLIENT_SCOPE="separate multiple scopes with a space"
AUTH_URL="https://app.assignr.com/oauth/token"
BASE_URL="https://api.assignr.com/api/v2"
REDIRECT_URI="urn:ietf:wg:oauth:2.0:oob"
LOG_LEVEL=20
```

`CLIENT_SECRET` and `CLIENT_ID` are considered secrets and shouldn't be shared, or publicly published.

`CLIENT_SCOPE` defines access level of the script. Valid values are 'read', 'write', and 'bank'. They can be combined by separating the scopes with a space. Example: 'read write'.

The scope should be limited to what's required. Limit scope to what's required to complete the task.

`LOG_LEVEL` provides the level of logging. The default, 30, equates to logging 'WARNING's and higher. The lower the number, the more information appears in the logs.

| Value |   Level  |
| ----- | -------- |
| 50    | CRITICAL |
| 40    | ERROR    |
| 30    | WARNING  |
| 20    | INFO     |
| 10    | DEBUG    |


## TO DO
[X] Create Sonarcloud Project

[X] Setup CI Pipeline

[ ] Write Delete Games logic

[ ] Write Unit Tests

    [ ] Get Availability

    [ ] Delete Games

    [X] Helpers