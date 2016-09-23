#!/usr/bin/python
import os
import re
import configparser
import utility

def get_config():

	config = configparser.ConfigParser();
	config.read("parser.config");
	
	try: 
		root_folder=config.get("parser config","Invoice_root_folder");
	except:
		print ("config file missed or format is not correct, can't continue processing the invoices!");
		exit(1);
	
	folders=("working","error","result","history");
	
	for i in range(0, len(folders)):
		if not os.path.exists(root_folder+"\\"+folders[i]):
			os.mkdir(root_folder+"\\"+folders[i]);
	
	return root_folder;

		
def main():

	parse_folder=get_config();
	
	#detect all the invoices in working folder
	invoices_list=[];
	for file in os.listdir(parse_folder+"\\\\working"):	
		if file.endswith(".txt"):
			invoices_list.append(file);
	
	for file in invoices_list: 
		source_file=parse_folder+"\\\\working\\\\"+file;
		output_file=parse_folder+"\\\\result\\\\"+file.replace('.txt','.csv');
		check_history=parse_folder+"\\\\history\\\\"+file;
		
		if os.path.isfile (check_history):
			overwriten = input("File:"+file+" founded in history folder, Do you want to overwrite and reprocess this file again? [yes/no]:")
			print ("\n");
			
			if overwriten != "yes":
				print ("skip processing invoice " +file);
				print ("\n");
				continue;
		
		print ("processing invoice file:"+file+".....");
		result=utility.analysis_invoice(source_file,output_file);
		print ("invoice file:"+ file +" processed ");
		
		if result == 0: 
			print ("converted result: SUCCESS.");
			try:
				os.rename(parse_folder+"\\\\working\\\\"+file,parse_folder+"\\\\history\\\\"+file);
			except:
				os.remove(parse_folder+"\\\\history\\\\"+file);
				os.rename(parse_folder+"\\\\working\\\\"+file,parse_folder+"\\\\history\\\\"+file);
		else: 
			print ("converted result: FAILED. Amount found in invoice and converted result are different");
			try:
				os.rename(parse_folder+"\\\\working\\\\"+file,parse_folder+"\\\\error\\\\"+file);
			except:
				os.remove(parse_folder+"\\\\error\\\\"+file);
				os.rename(parse_folder+"\\\\working\\\\"+file,parse_folder+"\\\\error\\\\"+file);
		
		print ("\n");
	

main()
	
	
