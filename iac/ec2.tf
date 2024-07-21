data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-ebs"]
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.large"

  root_block_device {
    volume_size = 8
  }

  vpc_security_group_ids = [
    module.ec2_sg.security_group_id,
    module.dev_ssh_sg.security_group_id
  ]
  iam_instance_profile = aws_iam_instance_profile.ec2.name

  tags = {
    "Name"  = "dog-breed-classifier"
    project = var.project_name
  }

  key_name                = "dbc_key"
  monitoring              = true
  disable_api_termination = false
  ebs_optimized           = true
}

resource "aws_key_pair" "terraform_ec2_key" {
  key_name   = "dbc_key"
  public_key = file("dbc_key.pub")
}
