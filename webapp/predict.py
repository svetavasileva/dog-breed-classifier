import numpy as np
import os

from keras.models import load_model
from keras.preprocessing import image


IMAGE_SIZE = (150, 150)


def predict_dog_breed(img_path):
    classes = {
        0: 'Beagle',
        1: 'Boxer',
        2: 'Bulldog',
        3: 'Dachshund',
        4: 'German Shepherd',
        5: 'Golden Retriever',
        6: 'Labrador Retriever',
        7: 'Poodle',
        8: 'Rottweiler',
        9: 'Yorkshire Terrier'
    }

    dir_path = os.path.dirname(os.path.realpath(__file__))
    MODEL_PATH = os.environ['MODEL_PATH'] or (
        dir_path + "/ " + 'dog_breed_classifier_model.h5')

    model = load_model(MODEL_PATH)

    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    img = image.load_img(img_path, target_size=IMAGE_SIZE)
    img = image.img_to_array(img)
    img = img.reshape(1, 150, 150, 3)
    prediction = model.predict(img)
    dog_class = np.argmax(prediction, axis=1)

    return classes[dog_class[0]]
