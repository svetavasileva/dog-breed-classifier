import os
import numpy as np
import random
import matplotlib.pyplot as plt
import mlflow
from PIL import Image
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.layers import Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient


# Helper function to load images
def load_images_from_folder(folder, image_size=(150, 150)):
    images = []
    labels = []
    for label in os.listdir(folder):
        label_path = os.path.join(folder, label)
        if os.path.isdir(label_path):
            for filename in os.listdir(label_path):
                img_path = os.path.join(label_path, filename)
                img = Image.open(img_path)
                img = img.resize(image_size)
                img = np.array(img)
                images.append(img)
                labels.append(label)
    return np.array(images), np.array(labels)


# Load data
data_dir = 'training_data'
image_size = (150, 150)


X, y = load_images_from_folder(data_dir, image_size)


# fill in with the public DNS of the EC2 instance
TRACKING_SERVER_HOST = os.getenv("MLFLOW_HOST")
mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")


# Normalize pixel values to be between 0 and 1
X = X / 255.0


print(f"tracking URI: '{mlflow.get_tracking_uri()}'")


# Encode labels to integers
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)


# Convert labels to one-hot encoding
y = to_categorical(y)

mlflow.search_experiments()
mlflow.set_experiment("my-experiment-1")

with mlflow.start_run():

    # Split data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42)

    # Print shapes to confirm
    print(f'X_train shape: {X_train.shape}')
    print(f'X_val shape: {X_val.shape}')
    print(f'y_train shape: {y_train.shape}')
    print(f'y_val shape: {y_val.shape}')

    # Define the CNN model
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)),
        MaxPooling2D(2, 2),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        Flatten(),
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(len(label_encoder.classes_), activation='softmax')
    ])

    # model.summary()

    # Compile the model
    model.compile(
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )

    # Train the model
    history = model.fit(
        X_train, y_train,
        epochs=30,
        batch_size=32,
        validation_data=(X_val, y_val)
    )

    # Evaluate the model on the validation set
    val_loss, val_accuracy = model.evaluate(X_val, y_val)
    # print(f'Validation accuracy: {val_accuracy:.4f}')
    mlflow.log_metric("accuracy", val_accuracy)

    # Save the model
    mlflow.sklearn.log_model(model, artifact_path="models")

    # Function to predict the breed of a random image from the dataset
    def predict_random_image(model, X, y, label_encoder):
        idx = random.randint(0, len(X) - 1)
        plt.imshow(X[idx])
        plt.title('Actual:' +
                  f'{label_encoder.inverse_transform([np.argmax(y[idx])])[0]}')
        plt.show()

        # Predict the class of the selected image
        y_pred = model.predict(X[idx].reshape(1, 150, 150, 3))
        print(f'Prediction probabilities: {y_pred}')

        # Get the predicted class
        predicted_class = label_encoder.inverse_transform([np.argmax(y_pred)])
        print(f'Predicted class: {predicted_class[0]}')


mlflow.end_run()

print(f"default artifacts URI: '{mlflow.get_artifact_uri()}'")


# import matplotlib.pyplot as plt
# acc = history.history['accuracy']
# val_acc = history.history['val_accuracy']
# loss = history.history['loss']
# val_loss = history.history['val_loss']

# epochs = range(len(acc))

# plt.plot(epochs, acc, 'r', label='Training accuracy')
# plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
# plt.title('Training and validation accuracy')

# plt.figure()

# plt.plot(epochs, loss, 'r', label='Training Loss')
# plt.plot(epochs, val_loss, 'b', label='Validation Loss')
# plt.title('Training and validation loss')
# plt.legend()

# plt.show()


# ## Interacting with the model registry


# Setting the AWS credentials for model upload to s3
# os.environ["AWS_ACCESS_KEY_ID"] = "***"
# os.environ["AWS_SECRET_ACCESS_KEY"] = "***"


client = MlflowClient(f"http://{TRACKING_SERVER_HOST}:5000")

EXPERIMENT_NAME = "my-experiment-1"

experiment = client.get_experiment_by_name(EXPERIMENT_NAME)

best_run = client.search_runs(experiment_ids=experiment.experiment_id,
                              run_view_type=ViewType.ACTIVE_ONLY,
                              max_results=1,
                              order_by=["metrics.rmse ASC"])[0]


# client.list_run_infos(experiment_id='1')[0].run_id
run_id = best_run.info.run_id
run_id

mlflow.register_model(
    model_uri=f"runs:/{run_id}/models",
    name='dog-breed-classifier'
)

mlflow.end_run()


# ## Predicting a random image
model.save('/output/dog_breed_classifier_model.h5')


# # Load the trained model
model = load_model('/output/dog_breed_classifier_model.h5')


# Predict for a random image
predict_random_image(model, X_val, y_val, label_encoder)
