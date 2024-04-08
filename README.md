# Project: MERN Application Deployment on AWS

This guide covers the deployment of a MERN (MongoDB, Express, React, Node.js) application on AWS, including CI/CD, IaC, and monitoring.

## Step 1: Set Up the AWS Environment

### 1.1 AWS CLI and Boto3
- Install and configure the AWS CLI:
  ```bash
  aws configure
  ```
- Install Boto3 for Python:
  ```bash
  pip install boto3
  ```

## Step 2: Prepare the MERN Application

### 2.1 Containerize the Application
- Create Dockerfiles for each component (frontend, backend).
- Build Docker images:
  ```bash
  cd frontend
  docker build -t smm-frontend .

  cd backend/helloService
  docker build -t smm-hello-service .

  cd backend/profileService
  docker build -t smm-profile-service .
  ```

### 2.2 Push Docker Images to Amazon ECR
- Create ECR repositories and push images:
  ```bash
  aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 160472638876.dkr.ecr.us-east-2.amazonaws.com
  
  docker tag smm-frontend:latest 160472638876.dkr.ecr.us-east-2.amazonaws.com/smm-frontend:latest
  docker push 160472638876.dkr.ecr.us-east-2.amazonaws.com/smm-frontend:latest

  docker tag smm-hello-service:latest 160472638876.dkr.ecr.us-east-2.amazonaws.com/smm-hello-service:latest
  docker push 160472638876.dkr.ecr.us-east-2.amazonaws.com/smm-hello

  docker tag smm-profile-service:latest 160472638876.dkr.ecr.us-east-2.amazonaws.com/smm-profile-service:latest
  docker push 160472638876.dkr.ecr.us-east-2.amazonaws.com/smm-profile-service:latest
  ```

## Step 3: Version Control

### 3.1 AWS CodeCommit
- Create a CodeCommit repository and push code:
  ```bash
  git clone https://git-codecommit.us-east-2.amazonaws.com/v1/repos/SampleMERNwithMicroservices
  git add .
  git commit -m "Initial commit"
  git push origin main
  ```

## Step 4: Continuous Integration with Jenkins

### 4.1 Set Up Jenkins (Jenkinsfile)
- Install Jenkins on an EC2 instance.
- Configure Jenkins with the necessary plugins.

### 4.2 Create Jenkins Jobs
- Set up Jenkins jobs to build and push Docker images to ECR on commits.

## Step 5: Infrastructure as Code (IaC)

### 5.1 Define Infrastructure with `iac.py`
- Run the Boto3 script to create AWS resources:
  ```bash
  python iac.py
  ```

## Step 6: Deploying Backend Services

### 6.1 Deploy Backend on EC2 with ASG
- Execute Boto3 script in `iac.py` to deploy backend services.

## Step 7: Set Up Networking

### 7.1 Create Load Balancer and Configure DNS
- Use `iac.py` to set up ELB and configure DNS with Route 53.

## Step 8: Deploying Frontend Services

### 8.1 Deploy Frontend on EC2
- Deploy the Dockerized frontend application using `iac.py`.

## Step 9: AWS Lambda Deployment

### 9.1 Create Lambda Functions
- Utilize `iac.py` to create and configure AWS Lambda functions.

## Step 10: Kubernetes (EKS) Deployment

### 10.1 Create EKS Cluster
- Create an EKS cluster using eksctl:
  ```bash
  eksctl create cluster --name smm-cluster --version 1.21 --region us-east-2 --nodegroup-name standard-workers --node-type t3.medium --nodes 3 --nodes-min 1 --nodes-max 4 --managed

  ```

### 10.2 Deploy Application with Helm
- Package and deploy the MERN application using Helm:
  ```bash
  helm install frontend-release ./frontend-chart
  helm install backend-release ./backend-chart
  ```

## Step 11: Monitoring and Logging

### 11.1 Set Up Monitoring
- Configure AWS CloudWatch for application monitoring.

### 11.2 Configure Logging
- Use AWS CloudWatch Logs for logging.

## Step 12: Documentation

### 12.1 Document the Architecture
- Create detailed documentation for the architecture and deployment process.

## Step 13: Final Checks

### 13.1 Validate the Deployment
- Ensure the MERN application is fully operational.

## BONUS: ChatOps Integration

### 14.1 Create SNS Topics and Lambda for ChatOps
- Use `iac.py` to create SNS topics and Lambda functions for ChatOps notifications.

### 14.2 Integrate ChatOps with Messaging Platform
- Set up integrations with Slack/MS Teams/Telegram for receiving notifications.

### 14.3 Configure SES
- Use AWS SES for email notifications.