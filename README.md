# Google Spreadsheets updates in Python

## Dependences
- [gspread](https://github.com/burnash/gspread)


## Basic Usage
Before using the script in it necessary to obtain the OAuth2 credentials from the Google Developer Console (take a look at the [gspread documentation](http://gspread.readthedocs.io/en/latest/oauth2.html).

Remember, that you have to share the file you would like to modify with the email address specify in the credential json file (`client_email` field).

1. Modify the settings.yml file.
2. Start the program with an alias referred to a file described in the settings.yml file or with the spreadsheet key and the worksheet index, otherwise the default workspace will be used.
3. Input the json referred to the new row to add, with the schema:
'''
"column name": "cell value"
'''
4. If a column name is not present on the spreadsheet the value will be ignored.
