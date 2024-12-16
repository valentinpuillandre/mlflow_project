provider "aws" {
  region = "us-east-1"
}

# S3 Bucket
resource "aws_s3_bucket" "mlflow_bucket" {
  bucket = "mlflow-artifacts-bucket"
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Name = "mlflow-bucket"
  }
}

# Security Group
resource "aws_security_group" "mlflow_sg" {
  name        = "mlflow-sg"
  description = "Allow HTTP and SSH access"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "mlflow_instance" {
  ami           = "ami-0c2b8ca1dad447f8a"
  instance_type = "t2.micro"

  security_groups = [aws_security_group.mlflow_sg.name]

  tags = {
    Name = "MLflow-Instance"
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo yum install -y python3 git
              pip3 install mlflow boto3 pandas sklearn

              # Clone the repo
              git clone https://github.com/valentinpuillandre/mlflow_project.git /home/ec2-user/mlflow-project
              cd /home/ec2-user/mlflow-project

              # Start MLflow server
              nohup mlflow server \
                --backend-store-uri s3://${aws_s3_bucket.mlflow_bucket.bucket} \
                --default-artifact-root s3://${aws_s3_bucket.mlflow_bucket.bucket}/artifacts \
                --host 0.0.0.0 \
                --port 5000 &
              EOF
}

# Public IP
output "mlflow_instance_public_ip" {
  value = aws_instance.mlflow_instance.public_ip
}
