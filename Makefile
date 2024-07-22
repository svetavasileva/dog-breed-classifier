IMAGE_NAME := model-trainer
CONTAINER_NAME := $(IMAGE_NAME)

build:
	docker build -t $(IMAGE_NAME) -f Dockerfile.model-trainer .

train-model: build
	@IMAGE_HASH=$$(docker images --format '{{.ID}}' $(IMAGE_NAME) | head -n 1) && \
	docker run --name $(CONTAINER_NAME) \
		-v $(pwd)/model/output:/app/output \
		-v $(pwd)/model/training_data:/app/training_data \
		--env-file .env \
		$$IMAGE_HASH

	mv $(pwd)/model/output/dog_breed_classifier_model.h5 $(pwd)/model
	scp -i "iac/dbc_key" $(pwd)/model/dog_breed_classifier_model.h5 ec2-user@ec2-54-91-116-13.compute-1.amazonaws.com:~/.
