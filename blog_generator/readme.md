# Llama2 Blog Generator

## Overview

This project leverages AWS API Gateway, AWS Bedrock, Lambda with Llama2 Foundation Model, and Streamlit to create an intelligent web application. The application processes user inputs to generate blog content using a machine learning model and displays the results in a user-friendly web interface.

## Architecture

The project architecture includes the following components:

- **AWS API Gateway**: Acts as the entry point for API requests.
- **AWS Bedrock**: Provides the foundation model (Llama2) for processing data.
- **AWS Lambda**: Executes the inference logic using the Llama2 model.
- **Streamlit**: Serves as the front-end web application framework to create an interactive user interface.

## Prerequisites

Before you begin, ensure you have the following:

- AWS account with necessary permissions for API Gateway, Lambda, and Bedrock.
- Python 3.7+ installed on your local machine.
- AWS CLI configured with your credentials.
- Node.js and npm installed for Streamlit deployment.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```
### 2. Set Up AWS Resources

#### Create Lambda Layer for Latest boto3
1. Create a new directory for the Lambda layer:
```
mkdir python
cd python
```
2. Install boto3 and botocore into this directory:
```
pip install boto3 botocore -t .
```
3. Zip the directory:
```
cd ..
zip -r boto3-layer.zip python
```
4. Upload the layer to AWS Lambda:
  - Go to the AWS Lambda console.
  - Navigate to "Layers" and click "Create layer".
  - Upload the boto3-layer.zip file.
  - Specify a name for the layer and select the appropriate runtime (e.g., Python 3.8).
#### Create Lambda Function
1. Navigate to the AWS Lambda console.
2. Create a new Lambda function.
4. Configure your function to use the Llama2 model from AWS Bedrock.
5. Upload the lambda_function.py file to your Lambda function.

#### Create API Gateway
1. Navigate to the AWS API Gateway console.
2. Create a new REST API.
3. Define a new resource and method (POST).
4. Integrate the POST method with your Lambda function.

### 3. Local Development
#### Install Dependencies
```
pip install -r requirements.txt
```
#### Set Up Environment Variables
Create a .env file in the project root and add the following:

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_aws_region
API_GATEWAY_URL=your_api_gateway_url
```
### 4. Run Streamlit Application
```
streamlit run app.py
```

## Usage
1. Open your web browser and navigate to the URL provided by Streamlit (usually http://localhost:8501).
2. Enter the blog topic in the web interface.
3. Click the "Generate Blog" button to see the results processed by the Llama2 model via the Lambda function.

### License
This project is licensed under the MIT License.