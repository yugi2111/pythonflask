from flask import Flask, render_template, url_for, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2
import boto3
import json

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():

    if(request.method == 'POST'):
        redshift_name = request.form['select_redshift']
        query = request.form['select_query']

        try:
            session = boto3.session.Session()
            client = session.client(
                                    service_name='secretsmanager',
                                    region_name='ap-south-1',
                                    aws_access_key_id = "AKIAUCRDAP5RKYFYABYS",
                                    aws_secret_access_key = "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"
                                    )
            response = client.get_secret_value(SecretId=redshift_name)
            data = json.loads(response['SecretString'])
            connection=psycopg2.connect(dbname = data['dbname'], host=data['host'], port= data['port'], user=data['user'], password= data['password'])
            cursor = connection.cursor()
            if query == "select-pb-user":
                # cursor.execute("SELECT * from pg_user;")
                cursor.execute(open("pg_user.sql",'r').read())
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                # for i in column_names:
                #     print(i)
                return render_template('result.html', result=results, col_name=column_names)
            else:
                return render_template('error.html')
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to Redshift", error)
        finally:
            #closing database connection.
            if(connection):
                cursor.close()
                connection.close()
    else:
        return render_template('index.html')

if __name__  == "__main__":
    app.run(debug=True)
