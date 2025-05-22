# Gmail to S3 API Deployment Plan

This document outlines the steps to deploy the Gmail to S3 API on AWS EC2 and update the frontend to connect to the deployed API.

## 1. Local Docker Setup and Testing

### 1.1 Setup Local Environment

```bash
# Navigate to the Gmail to S3 API directory
cd path/to/your/repo/envision_product/tools/gmail_s3
```

### 1.2 Create a Dockerfile

Create a `Dockerfile` in the Gmail to S3 API directory:

```bash
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a directory for tokens if it doesn't exist
RUN mkdir -p tokens

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8002

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
EOF
```

### 1.3 Create a .dockerignore file

```bash
cat > .dockerignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.env.*
.git/
.gitignore
.pytest_cache/
.coverage
htmlcov/
.vscode/
tokens/
*.log
EOF
```

### 1.4 Set Up Environment Variables for Local Testing

```bash
# Create .env file for local testing
cat > .env.local << 'EOF'
# Google API credentials
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8002/auth/callback

# AWS S3 credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=your_s3_bucket_name
S3_REGION=your_s3_region

# API configuration
API_HOST=0.0.0.0
API_PORT=8002
API_PREFIX=/api
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Email configuration
TARGET_EMAIL_SUBJECTS=logistics,shipment,delivery
EOF

# Update with your actual values
# Edit the .env.local file with your preferred text editor
```

### 1.5 Build and Test the Docker Container Locally

```bash
# Build the Docker image
docker build -t gmail-s3-api:local .

# Run the container locally
docker run -d --name gmail-s3-api-local -p 8002:8002 --env-file .env.local gmail-s3-api:local

# Check if the container is running
docker ps

# Test the API locally
curl http://localhost:8002/auth/status

# View logs if needed
docker logs gmail-s3-api-local

# Stop and remove the container when done testing
docker stop gmail-s3-api-local
docker rm gmail-s3-api-local
```

## 2. EC2 Setup via AWS Management Console and CloudShell

### 2.1 Launch an EC2 Instance via AWS Console

1. **Sign in to the AWS Management Console**
   - Go to https://console.aws.amazon.com/
   - Sign in with your AWS account credentials

2. **Navigate to EC2 Dashboard**
   - Click on "Services" in the top navigation bar
   - Select "EC2" under Compute section

3. **Launch a new EC2 instance**
   - Click the "Launch instance" button
   - Provide a name for your instance (e.g., "gmail-s3-api-server")

4. **Select an Amazon Machine Image (AMI)**
   - Choose "Amazon Linux 2 AMI" (or the latest Amazon Linux version)
   - Select the 64-bit (x86) architecture

5. **Choose an Instance Type**
   - Select "t2.small" or "t2.micro" for testing
   - Click "Next"

6. **Configure Instance Details**
   - Keep the default settings or adjust as needed
   - Click "Next"

7. **Add Storage**
   - Set the size to 20 GB
   - Keep the default volume type (gp2)
   - Click "Next"

8. **Add Tags (Optional)**
   - Add a tag with key "Name" and value "gmail-s3-api-server"
   - Click "Next"

9. **Configure Security Group**
   - Create a new security group
   - Name it "gmail-s3-api-sg"
   - Add the following rules:
     - SSH (port 22) from your IP address
     - HTTP (port 80) from anywhere (0.0.0.0/0)
     - HTTPS (port 443) from anywhere (0.0.0.0/0)
     - Custom TCP (port 8000) from anywhere (0.0.0.0/0)
     - Custom TCP (port 8002) from anywhere (0.0.0.0/0)
   - Click "Review and Launch"

10. **Review and Launch**
    - Review your instance configuration
    - Click "Launch"

11. **Create or Select a Key Pair**
    - Create a new key pair or select an existing one
    - If creating new, download the key pair (.pem file) and save it securely
    - Click "Launch Instances"

12. **Note the Instance ID and Public IP**
    - After the instance is launched, note its Instance ID and Public IP address
    - You'll need these for the next steps

### 2.2 Access AWS CloudShell

1. **Open AWS CloudShell**
   - Click on the CloudShell icon in the top navigation bar of the AWS Management Console
   - Wait for the CloudShell environment to initialize

2. **Verify CloudShell Access**
   - You should see a terminal prompt in your browser
   - CloudShell comes pre-authenticated with your AWS credentials
   - Run `aws --version` to verify the AWS CLI is installed

### 2.3 Connect to Your EC2 Instance from CloudShell

1. **Upload your key pair to CloudShell**
   - Click on "Actions" in the CloudShell toolbar
   - Select "Upload file"
   - Browse and select your .pem key file
   - Wait for the upload to complete

2. **Set proper permissions for your key file**
   ```bash
   chmod 400 your-key-pair.pem
   ```

3. **Connect to your EC2 instance**
   ```bash
   # Get the public IP of your instance if you don't have it
   aws ec2 describe-instances \
     --instance-ids i-0123abc456def7890 \
     --query "Reservations[0].Instances[0].PublicIpAddress" \
     --output text
   
   # SSH into the instance
   ssh -i your-key-pair.pem ec2-user@your-instance-public-ip
   ```

## 3. Setup on EC2 Instance Using AWS CLI

### 3.1 Install Required Software

```bash
# Update the system
sudo yum update -y

# Install git
sudo yum install git -y

# Install Docker
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo systemctl enable docker

# Log out and log back in to apply the docker group
exit
# SSH back in from CloudShell
ssh -i your-key-pair.pem ec2-user@your-instance-public-ip
```

### 3.2 Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name/envision_product/tools/gmail_s3
```

### 3.3 Create Dockerfile on EC2

```bash
# Create the Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a directory for tokens if it doesn't exist
RUN mkdir -p tokens

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8002

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
EOF
```

### 3.4 Create .dockerignore on EC2

```bash
cat > .dockerignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.env.*
.git/
.gitignore
.pytest_cache/
.coverage
htmlcov/
.vscode/
tokens/
*.log
EOF
```

### 3.5 Set Up Environment Variables for Production

```bash
# Create .env file
cat > .env << 'EOF'
# Google API credentials
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://your-ec2-public-ip:8002/auth/callback

# AWS S3 credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=your_s3_bucket_name
S3_REGION=your_s3_region

# API configuration
API_HOST=0.0.0.0
API_PORT=8002
API_PREFIX=/api
CORS_ORIGINS=http://your-frontend-domain.com,http://localhost:3000

# Email configuration
TARGET_EMAIL_SUBJECTS=logistics,shipment,delivery
EOF

# Update with your actual values
# Replace your-ec2-public-ip with your actual EC2 public IP
sed -i "s/your-ec2-public-ip/$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/g" .env

# Edit other values as needed
nano .env
```

### 3.6 Build and Run the Docker Container

```bash
# Build the Docker image
docker build -t gmail-s3-api .

# Run the container
docker run -d --name gmail-s3-api -p 8002:8002 --env-file .env --restart unless-stopped gmail-s3-api
```

### 3.7 Verify Deployment

```bash
# Check if the container is running
docker ps

# Test the API endpoint
curl http://localhost:8002/auth/status

# View container logs if needed
docker logs gmail-s3-api
```

## 4. Set Up HTTPS with Nginx (Optional but Recommended)

### 4.1 Install and Configure Nginx

```bash
# Install Nginx
sudo amazon-linux-extras install nginx1 -y
sudo systemctl enable nginx
sudo systemctl start nginx

# Create Nginx configuration
sudo tee /etc/nginx/conf.d/gmail-s3-api.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-ec2-public-ip;

    location / {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Replace with your actual IP
sudo sed -i "s/your-ec2-public-ip/$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/g" /etc/nginx/conf.d/gmail-s3-api.conf

# Restart Nginx
sudo systemctl restart nginx
```

### 4.2 Set Up SSL with Let's Encrypt (If You Have a Domain)

```bash
# Install certbot
sudo amazon-linux-extras install epel -y
sudo yum install certbot python-certbot-nginx -y

# Get and install certificate
sudo certbot --nginx -d your-domain.com
```

## 5. Frontend Integration

### 5.1 Update API Base URL

In the Neural POC frontend's `script.js`, update the `GMAIL_S3_API_BASE_URL` constant:

```javascript
// API Base URL - Update this for production deployment
const GMAIL_S3_API_BASE_URL = 'http://your-ec2-public-ip:8002';  // or https://your-domain.com
```

You can do this directly in your local repository and push to GitHub, or edit it on the server:

```bash
# Navigate to the frontend directory
cd /path/to/frontend/directory

# Edit the script.js file
nano script.js

# Find and update the GMAIL_S3_API_BASE_URL constant
```

### 5.2 Update OAuth Redirect URI

1. Go to Google Cloud Console > APIs & Services > Credentials
2. Edit your OAuth 2.0 Client ID
3. Add the new redirect URI: `http://your-ec2-public-ip:8002/auth/callback` (or with https if using SSL)

### 5.3 Update CORS Settings

Ensure your frontend domain is included in the `CORS_ORIGINS` environment variable:

```bash
# Edit the .env file
nano .env

# Update the CORS_ORIGINS line
# CORS_ORIGINS=http://your-frontend-domain.com,http://localhost:3000
```

### 5.4 Test the Integration

1. Access your frontend application
2. Test the Gmail authentication flow
3. Test email listing and attachment retrieval
4. Test S3 upload functionality

## 6. Monitoring and Maintenance

### 6.1 Set Up Basic Monitoring

```bash
# Create a monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash

# Check if container is running
if ! docker ps | grep -q gmail-s3-api; then
  echo "Container is not running. Attempting to restart..."
  docker start gmail-s3-api
  
  # Send an email alert (requires mailx)
  echo "Gmail S3 API container was down and has been restarted" | mail -s "Alert: Gmail S3 API Down" your-email@example.com
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
  echo "Disk usage is at $DISK_USAGE%. Consider cleaning up." | mail -s "Alert: High Disk Usage" your-email@example.com
fi
EOF

# Make the script executable
chmod +x monitor.sh

# Add to crontab to run every hour
crontab -e
# Add: 0 * * * * /path/to/your-repo/envision_product/tools/gmail_s3/monitor.sh
```

### 6.2 Set Up Log Rotation

```bash
# Create a logrotate configuration
sudo tee /etc/logrotate.d/gmail-s3-api > /dev/null << 'EOF'
/var/log/gmail-s3-*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 640 ec2-user ec2-user
}
EOF
```

## 7. Troubleshooting

### 7.1 Common Issues

- **OAuth Callback Issues**: Ensure redirect URIs are correctly configured in both the Google Cloud Console and your `.env` file
- **CORS Errors**: Check CORS_ORIGINS in environment variables and ensure it includes your frontend domain
- **S3 Upload Failures**: Verify AWS credentials and bucket permissions
- **Container Not Starting**: Check Docker logs with `docker logs gmail-s3-api`
- **API Not Accessible**: Verify security group settings and Nginx configuration

### 7.2 Useful Commands for Troubleshooting

```bash
# Check container status
docker ps -a

# View container logs
docker logs gmail-s3-api

# Check Nginx status
sudo systemctl status nginx

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Check if the API port is listening
sudo netstat -tulpn | grep 8002

# Test the API endpoint
curl http://localhost:8002/auth/status
```

## 8. Managing Your Deployment from CloudShell

### 8.1 Reconnecting to Your EC2 Instance

If you close your CloudShell session and need to reconnect later:

```bash
# Open CloudShell again from the AWS Console
# Ensure your key is still available or re-upload it

# Connect to your EC2 instance
ssh -i your-key-pair.pem ec2-user@your-instance-public-ip
```

### 8.2 Updating Your Deployment

```bash
# Connect to your EC2 instance from CloudShell
ssh -i your-key-pair.pem ec2-user@your-instance-public-ip

# Navigate to your repository
cd your-repo-name/envision_product/tools/gmail_s3

# Pull the latest changes
git pull

# Rebuild and restart the container
docker build -t gmail-s3-api .
docker stop gmail-s3-api
docker rm gmail-s3-api
docker run -d --name gmail-s3-api -p 8002:8002 --env-file .env --restart unless-stopped gmail-s3-api
```

### 8.3 Creating a Deployment Script

```bash
# Create a deployment script on your EC2 instance
cat > deploy.sh << 'EOF'
#!/bin/bash

# Pull latest changes from GitHub
git pull

# Rebuild the Docker image
docker build -t gmail-s3-api .

# Stop and remove the existing container
docker stop gmail-s3-api
docker rm gmail-s3-api

# Run the new container
docker run -d --name gmail-s3-api -p 8002:8002 --env-file .env --restart unless-stopped gmail-s3-api

echo "Deployment completed successfully"
EOF

# Make the script executable
chmod +x deploy.sh

# Run the script when you need to update
./deploy.sh
```
