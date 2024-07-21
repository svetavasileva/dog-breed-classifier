resource "aws_ecr_repository" "dog-breed-classifier" {
  name                 = "dog-breed-classifier"
  image_tag_mutability = "MUTABLE"

  tags = {
    project = var.project_name
  }
}
