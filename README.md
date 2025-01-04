# fingal

Automation tool to track my expenses.  

Parses credit card transaction history file, automatically infers expenditure categories based on the transaction metadata, and uses the Google API Client to update a Google spreadsheet. 

## Usage

To make a Google spreadsheet bot, you need to create a Google Workspace project.

```shell
conda create -n fingal python=3.11 -y
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```