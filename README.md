# mlops-project

## Problem Statement

## Infrastructure setup

### Generate EC2 instance SSH key
`cd iac && ssh-keygen -f dbc_key`

### Setup AWS
- Adjust terraform s3 backend name in the `providers.tf`
- Run `aws configure` and provide you Access Keys
- Adjust VPC ID in the `main.auto.tfvars`
- `terraform init`
- `terraform plan`
- `terraform apply`

### Configure Docker on the EC2
Substitute `<EC2_DNS_INSTANCE_HOSTNAME>` with the EC2 instance DNS address
```
ssh -i "dbc_key" ec2-user@<EC2_DNS_INSTANCE_HOSTNAME>
sudo yum install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## Model training
Model `dog_breed_classifier_model.h5` is already commited to the repository but here are the steps to train it from scratch.
It needs MLFLOW instance running and AWS credentials to upload the artifact data to the MLFLOW's s3 bucket. This can be set in the `.env` file.

`make train-model`

## Webapp deployment
Webapp is deployed with GitHub Actions automatically to the EC2 instance automatically. GHA workflow requires the following secrets to be setup in order to sucessfully proceed with the deployment:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
EC2_SSH_KEY
EC2_USER
EC2_HOST
```

Application should start listening at http://<EC2_DNS_NAME>:80
