#!/usr/bin/python
import os
import re

# To fiter all the header not related to the records #
# add at 14/06 to find the payment ref and total_amount from invoice first #
def find_first_invoice_entry(line_no, recs):
	global Payment_Ref;
	global total;
	entry = -1;
	
	for i in range (0, line_no):
		if "Payment Ref" in recs[i]:
			Payment_Ref=recs[i].split(':')[1].replace(' ','').replace('\n','');
		if "Amount" in recs[i]:
			i=i+1;
			entry = i;
		if "TOTAL PAID" in recs[i]:
			total=recs[i].split("$",1)[1].replace('\n','');
	return entry;


# consolidate each invoice from multiple lines into 1 single entry					#
# global variable used to traverse the document and pass the value to each function	#
def invoice_rec_finder(recs):

	global invoice_entry;
	invoice="";
	
	try: 
		while True:
			rec=recs[invoice_entry];
			invoice_entry=invoice_entry+1;	
			if "----------------" in rec:
				return invoice;
			invoice=invoice + rec.replace('\n',' ');
	except:
		return "error";
		
def invoice_analysis(content):
	details={};
	details['InvoiceNo']="";
	details['REF']="";
	details['PAX']="";
	details['Date']="";
	details['JOB_No']="";
	details['NOTE1']="";
	details['NOTE2']="";
	
	contents=content.split();
	
	# Due to different formats exist in the invoice, find the Amount column first #
	# Then find the distance between invoice number and Column Amount to determine if rest of the columns exist or not #
	
	for i in range (0,len(contents)):
		value = contents[i].replace('-','').replace(',','').replace('.','');
		regex ="^\$\d+$";
		if re.search(regex, value):
			details['Amount']=contents[i].replace(',','');
			break;		
						
	# This part extract column INV,REF,PAX NAME,TRAVEL DATE,AMT First
	#Handle special case if there is only invoice number and Amount E.g
	#------------------------
    #00051353-OH $2,265.53
	#------------------------
	# i is the array pointer to the column AMT
	if i == 1:
		details['InvoiceNo']=contents[0];
	else:
		PAX_NAME_start=0;
		PAX_NAME_end=0;
		if contents[1] == 'CN':
			details['InvoiceNo']=contents[0] + " " + contents[1];
			details['REF']=contents[2];	
			PAX_NAME_start=3;
		else: 
			details['InvoiceNo']=contents[0];
			details['REF']=contents[1];
			PAX_NAME_start=2;
	
		Date_finder=False;
		MonList = ["^Jan$","^Feb$","^Mar$","^Apr$","^May$","^Jun$","^Jul$","^Aug$","^Sep$","^Oct$","^Nov$","^Dec$"];
		for j in range (0,(i-1)):
			for Mon in MonList:
				if re.search(Mon, contents[j]):
					Date_finder=True;
					details['Date']= contents[j-1] + ' ' + contents[j] + ' ' + contents[j+1];
					PAX_NAME_end=j-1;
					break;	
		
		if Date_finder == False:
			details['Date']="";
			PAX_NAME_end=i;
			
		details['PAX']="";
		for j in range (PAX_NAME_start, PAX_NAME_end):
			details['PAX']=details['PAX']+ " " + contents[j];
		details['PAX'] = details['PAX'][1:]
	
	
	# Start to handle note1 note2 and job_Number, 
	# case 1 there is nothing after amount
	# case 2 there is note 1 only
	# case 3 there is note 1 and note 2
	
	if (i+1) != len(contents):
	# find job number as a flag column
		for j in range (i+1,len(contents)):
			regex ="^\d{7}$";
			job_finder=False;
			if re.search(regex, contents[j]):
				details['JOB_No']=contents[j];
				for k in range (i+1, j): details['NOTE1']=details['NOTE1']+ " " + contents[k];
				details['NOTE1']=details['NOTE1'][1:]
				for k in range (j+1, len(contents)):  details['NOTE2']=details['NOTE2']+ " " + contents[k];
				details['NOTE2']=details['NOTE2'][1:]
				job_finder=True;
				break;			
		
		if job_finder==False: 
			for j in range (i+1, len(contents)): details['NOTE1']=details['NOTE1']+ " " + contents[j];
			details['NOTE1']=details['NOTE1'][1:]
			
	return details;
		
# using "TOTAL PAID" character find the end of the invoice file to stop whole transform process #
def eof_invoice(recs): 

	global invoice_entry;
	global total_paid;
	
	if "TOTAL PAID" in recs[invoice_entry]:
		amount=recs[invoice_entry].split("$",1)[1].replace(',','');
		total_paid=float(amount);
		return True;
		
def analysis_invoice(invoice_file,result_file):
	
	# read raw file into an array #
	total_amount=float(0);
	invoice = open(invoice_file, "r");
	lines = invoice.readlines();
	invoice.close();
	
	# global variable used to traverse the document #
	# and pass the value to each function			#
	# create a output handler 						#
	global invoice_entry;
	global total_paid;
	global total;
	global Payment_Ref;
	
	outfile = open(result_file,'w');
	total_line = len(lines);
	outfile.write("INV,REF,PAX NAME,TRAVEL DATE,AMT,JOB No.,NOTE1,NOTE2,Payment_Ref,Total Paid\n");
	
	invoice_entry=find_first_invoice_entry(total_line,lines);	
	if invoice_entry == -1:
		outfile.close();
		print ("CONVERT ERROR: Header line doesn't match with pre-defined format, please check invoice header\n");
		return 0;
	
	# start processing the raw file using all the functions designed above #
	while True:
		invoice_content=invoice_rec_finder(lines);
		if invoice_content == 'error': 
			outfile.close();
			return 2;
		
		invoice_result=invoice_analysis(invoice_content);
		outfile.write('"'+invoice_result['InvoiceNo'] + '","' + invoice_result['REF'] + '","' + invoice_result['PAX'] + '","' + invoice_result['Date'] + '","' + invoice_result['Amount'] + '","' + invoice_result['JOB_No'] + '","' + invoice_result['NOTE1'] + '","' + invoice_result['NOTE2']+'","'+Payment_Ref+'","'+total+'"\n');
		total_amount = total_amount + float(invoice_result['Amount'].replace('$',''));
		if eof_invoice(lines):
			break;
			
	outfile.close();
	print ("converted invoice amount:" + str(round(total_amount,2)));
	print ("Amount found from invoice:" + str(total_paid));
	if str(total_paid) == str(round(total_amount,2)): return 0;
	else: return 1;
	

