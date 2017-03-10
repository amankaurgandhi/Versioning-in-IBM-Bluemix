####################################
#Name : Aman Kaur Gandhi           #
#Student Id : 1001164326           #
#Section : CSE-6331-001            #
#Reference: Code provided in class #
####################################

import os
import swiftclient
import pyDes
import operator
import hashlib
import datetime
from flask import Flask, request, redirect, url_for, render_template ,  make_response
from werkzeug.utils import secure_filename
from cloudant.client import Cloudant
from flask import Markup, flash
app = Flask(__name__)





	

## method for uploading a file to bluemix container
@app.route('/upload', methods=['GET', 'POST'])
def upload():
	
        # check if the post request has the file part
	
	f = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename

	if f.filename == '':
		print('No selected file')
		return redirect(request.url)
	docs= [document['file_name'] for document in my_database]	
	f_contents = [document['hashed_value'] for document in my_database]
	file_content = f.read().decode("utf-8")
	filecontent_hash = file_content.encode("utf-8")
	hashed_content = hashlib.sha224(filecontent_hash).hexdigest()
	
	
	file_name = f.filename
	#if filename already exists
	if file_name in docs:
		#if hashed contents are same
		if hashed_content in f_contents :
			msg ="File not uploaded as the contents are same"
			return msg
			
		else:
			max_version = [int(document['version']) for document in my_database if file_name == document['file_name']]
			version = [max(max_version) + 1 for document in my_database if file_name == document['file_name']]	
			data = {'file_name': file_name, 
				'version' : str(version[0]),
				'last_modified_date': str(datetime.datetime.now()),
				'content': file_content,
				'hashed_value': hashed_content}
			doc = my_database.create_document(data)
			msg ="File Uploaded"
	else :
		version =  1
		data = {'file_name': file_name, 
			'version' : str(version),
			'last_modified_date': str(datetime.datetime.now()),
			'content': file_content,
			'hashed_value': hashed_content}
		doc = my_database.create_document(data)
		msg ="File Uploaded"
	return render_template('index.html', message= msg)
	
## method for deleting the file from the object store at bluemix 
@app.route('/delete', methods=['GET', 'POST'])
def delete():
	for document in my_database:
		if (document['file_name'] == request.form['filenm'] and document['version']== request.form['version_no']):
			print("File found and deleted")
			document.delete()
			#document.delete_attachment(file_name)
		else:
			print ('File not found')
	
	return render_template('index.html')

## method for downloading the file from the object store  
@app.route('/download', methods=['GET', 'POST'])
def download():
	flag = False
	filen = request.form['filename']
	ver = request.form['version_num']
	for document in my_database:
		if (document['file_name'] == filen and document['version']== ver):
			response = make_response(document['content'])
			response.headers["Content-Disposition"] = "attachment; filename="+ filen
			flag = True
	if flag == False:
		response = 'File not found'
	return response

@app.route('/list_files',  methods=['GET', 'POST'])
def list_files():
		#opening database
	my_database = client['cloud_database']
	number_of_docs = 0
		#list documents in the database
	#for document in my_database:
	
	doc={}
	for document in my_database:
		number_of_docs = number_of_docs + 1
		doc[number_of_docs]= document
		
	return render_template('index.html', result = doc)
	
@app.route('/')
def index():
	#opening database
	my_database = client['cloud_database']
	#list documents in the database
	for document in my_database:
		print (document['file_name'])
	return render_template('index.html')

port = os.getenv('PORT', '5000')

client = Cloudant("ed998709-0916-4fbf-9184-fecc00382533-bluemix", "212078a0cf2cd8d727bad88de0ede80e29a52a296d49434485ebc8ee1e42dd37", url="https://ed998709-0916-4fbf-9184-fecc00382533-bluemix:212078a0cf2cd8d727bad88de0ede80e29a52a296d49434485ebc8ee1e42dd37@ed998709-0916-4fbf-9184-fecc00382533-bluemix.cloudant.com")
# Connect to the server
client.connect()

# Perform client tasks...
session = client.session()
if 'cloud_database' not in client.all_dbs():
	my_database = client.create_database('cloud_database')
else:
	my_database = client['cloud_database']
print( 'Username: {0}'.format(session['userCtx']['name']))
print ('Databases: {0}'.format(client.all_dbs()))






if __name__ == '__main__':
	app.run(host='0.0.0.0', port=int(port))
