# Get Availbility

This tool extracts referee availability from Assignr, and repackages it for offline use. 

This tool is meant for assignors who refuse to enter the 21st century preferring to use spreadsheets to assign games while avoiding the need to tracking referee availability via email.

Again, this offering is less than ideal as games scheduled outside of Assignr need to be imported into Assignr.


## Setup

### Python setup
* create a virtualenv
    * `python3 -m venv <virtual env name> or
    * `virtualenv <virtual env name>
* source ./<virtual env name>/bin/activate (Linux/Mac)
* run `pip install -r requirements`

### Environment Setup
* copy `env.sample` to `.env`
* change to .