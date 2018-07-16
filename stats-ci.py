#!/usr/bin/env python

import gspread
import argparse
import os
import yaml
import json
from oauth2client.service_account import ServiceAccountCredentials

def parse_args():
	parser = argparse.ArgumentParser(description='Stats CI helps you to track any measurable information you want to analyse of your project. To give this kind of flexibility, Stats CI allows you to pass a JSON value in input, that will be appended as a row into a Google Spreadsheet you define. In this way you can keep track of the informations of your specific build. The final goal is to compare data, create statistics and graphs on the project going on. The input of the program must be a JSON with the structure "column_name":"value"; column_name must be present in the first line (the header) of the Google Spreadsheet file. If it isn\'t, the entire operation will abort. The program is designed to work with Travis CI. For this reason it use a .yml settings file to set information related to the Spreadsheet to update.')

	parser.add_argument('--creds',
                    help='The credential file (json), if not specified the credentials will be recovered from env vars.')

	parser.add_argument('--workspace',
                    help='The workspace alias (ref. .stats.yml), if not present the default one will be used.')

	parser.add_argument('--sk',
                    help='The spreadsheet key, if this parameter is defined workspaces allready defined in .stats.yml will not be taken into consideration. A worksheet index must be present.')

	parser.add_argument('--wi', type=int,
                    help='The worksheet index, if this parameter is defined workspaces allready defined in .stats.yml will not be taken into consideration. A spreadsheet key must be present.')

	args = parser.parse_args()

	stream = open('.stats.yml', 'r')
	data = yaml.load(stream)

	if args.creds is not None:
		if os.path.isfile(args.creds) == False:
			print('[ERROR] Credential file {} not found!'.format(args.creds)); 	
			exit(-1)
		print('[INFO] Using credential from file: "{}".'.format(args.creds));
		creds_flag = 0
		json_creds = args.creds
	
	else:
		print('[INFO] Using credential from env var.');
		creds_flag = 1
		if 'CREDS' in os.environ:
			json_creds = os.environ['CREDS']
		else:
			print('[ERROR] Credentials not found in env var.')
			exit(-1)

	if args.workspace is not None and args.sk is not None or args.wi is not None:
		print('[ERROR] It is not possible to define both the workspace and the spreadsheet key and the worksheet index.');

	if args.workspace is None:
		if args.sk is None or args.wi is None:
			print('[INFO] Using default workspace.');
			sk = data["workspaces"]["default"]["-spreadsheet_key"];			
			wi = data["workspaces"]["default"]["-worksheet_index"];			

		else:
			print('[INFO] Using spreadsheet and worksheet defined.');
			sk = args.sk;
			wi = args.wi;

	else:
		for k, v in data["workspaces"].items():
			if data["workspaces"][k]["-alias"] == args.workspace:
				print('[INFO] Using spreadsheet and worksheet from settings.');
				sk = data["workspaces"][k]["-spreadsheet_key"];
				wi = data["workspaces"][k]["-worksheet_index"];

		if sk is None or wi is None:
			print("[ERROR] Workspace alias not found!");
			exit(-1);

	print('[INFO] spreadsheet key: {}'.format(sk))
	print('[INFO] worksheet index: {}'.format(wi))
	
	return creds_flag, json_creds, sk, wi;
	

if __name__ == '__main__':
	creds_flag, json_creds, sk, wi = parse_args();

	json_as_str = input()

	if isinstance(json_as_str, dict):
		json_obj = json_as_str;
	else:
		json_obj = json.loads(json_as_str)

	scope = ['https://spreadsheets.google.com/feeds']
	if creds_flag == 0:
		credentials = ServiceAccountCredentials.from_json_keyfile_name(json_creds, scope)
	else:
		dict_creds = json.loads(json_creds)
		credentials = ServiceAccountCredentials.from_json_keyfile_dict(dict_creds, scope)
	gc = gspread.authorize(credentials)

	sh = gc.open_by_key(sk)
	wsh = sh.get_worksheet(wi)

	n_cols = wsh.col_count
	
	headers = {}
	for i in range(1, n_cols):
		val = wsh.cell(1, i).value;
		if val == '':
			if i == 1:
				print('[ERROR] Header row is not present in the remote file.');
				exit(-1);
			break;
		else:
			headers[val] = i;

	row = {}
	for k,v in json_obj.items():
		if k in headers:
			row[headers[k]] = v;
		else:
			print('[ERROR] Column {} not present. Aborting.'.format(k));
			exit(-1);
	
	values = []
	for k in sorted(row.keys()):
		values.append(row[k])

	print('[INFO] Writing on remote file: ')
	print(values)
	wsh.insert_row(values, 2)
	print('[INFO] End of process')
