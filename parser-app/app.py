from flask import Flask, request, jsonify
import boto3
from pypdf import PdfReader
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/parse-pdf', methods=['POST'])
def parse_pdf():
    try:
        data = request.json
        file_id = data.get('fileId')
        print('file_id')
        pdf_content = retrieve_pdf_from_s3(file_id)
        print(type(pdf_content))
        # return pdf_content
        parsed_soft_data, parsed_technical_data = parse_pdf_content(pdf_content)

        return jsonify({'message': 'PDF parsed successfully', 'softskills': parsed_soft_data, 'technicalskills': parsed_technical_data})
    except Exception as e:
        print(f"Error parsing PDF: {str(e)}")
        return jsonify({'error': 'Error parsing PDF'}), 500

def retrieve_pdf_from_s3(file_id):
    s3_client = boto3.client('s3', aws_access_key_id='AKIAW6SIXMLJA6NASGPB', aws_secret_access_key='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')
    response = s3_client.get_object(Bucket='websitebucket0106', Key=file_id)
    # object_content = response['Body'].read().decode('utf-8')
    # return object_content
    fs = response['Body'].read()
    reader = PdfReader(BytesIO(fs))
    count = len(reader.pages)
    output = ""
    for i in range(count):
        page = reader.pages[i]
        output += page.extract_text()
    output = output.replace(',',"")
    output = output.strip()
    output = output.split('\n')
    for i in range(len(output)):
        output[i] = output[i].strip()
        output[i] = output[i].lower()
    
    return output

def intersection(lst1, lst2):
    print(lst1)
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def parse_pdf_content(pdf_content):
    softSkills = ["creative","adaptable", "professional", "diligent", "insightful", "resourceful", "productive", "teamwork", "mentoring"]
    technicalSkills = ["aws", "c#", ".net", "unity", "angular","html", "git", "sql", "react.js", "javascript", "typescript", "c++", "node.js", "php", "python", "docker", "postman", "excel"]
    intersectedSoftSkills = intersection(pdf_content,softSkills)
    intersectedTechnicalSkills = intersection(pdf_content,technicalSkills)
    return list(dict.fromkeys(intersectedSoftSkills)), list(dict.fromkeys(intersectedTechnicalSkills))

@app.route('/parsed-pdf/<file_id>')
def get_parsed_data(file_id):
    try:
        pdf_content = retrieve_pdf_from_s3(file_id)
        parsed_soft_data, parsed_technical_data = parse_pdf_content(pdf_content)
        return jsonify({'message': 'PDF parsed successfully', 'softskills': parsed_soft_data, 'technicalskills': parsed_technical_data})
    except Exception as e:
        print(f"Error parsing PDF: {str(e)}")
        return jsonify({'error': 'Error parsing PDF'}), 500


if __name__ == '__main__':
    app.run(debug=True)
