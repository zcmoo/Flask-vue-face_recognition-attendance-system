from PIL import Image
from arcface import ExtractEmbeddings
import numpy as np
import matplotlib.pyplot as plt

extract_embeddings = ExtractEmbeddings()
def face_distance(image_1, image_2):
    encoding_1 = extract_embeddings.encode_face_dataset_visualization(image_1)
    encoding_2 = extract_embeddings.encode_face_dataset_visualization(image_2)
    l1 = np.linalg.norm(encoding_1 - encoding_2, axis=1)
    img1 = Image.open(image_1)
    img2 = Image.open(image_2)
    plt.subplot(1, 2, 1)
    plt.imshow(np.array(img1))
    plt.subplot(1, 2, 2)
    plt.imshow(np.array(img2))
    plt.text(-12, -12, 'Distance:%.3f' % l1, ha='center', va='bottom', fontsize=11)
    plt.show()
    return l1


if  __name__ == "__main__":
    while True:
            image_1 = input('Input image_1 filename:')
            image_2 = input('Input image_2 filename:')
            probability = face_distance(image_1,image_2)
            print(probability)
