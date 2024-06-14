#Импорт необходимых библиотек
import cv2 #Работа с фотографиями
import insightface  #Распознование лиц
import matplotlib.pyplot as plt #Отображение фотографий
from insightface.app import FaceAnalysis    #Объект отвечающий за распознавание
#from insightface.data import get_image as ins_get_image


#print('insightface', insightface.__version__) Вывод версии библиотеки

plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))

#img = ins_get_image('t1')
img = cv2.imread('phot.jpg')
plt.imshow(img[:,:,::-1])
plt.axis('off')
plt.show()
#Координаты рамки лица faces[номер лица]['bbox']
faces = app.get(img)

#Извлечение векторов лиц
face_vectors = []
for face in faces:
    vector = face.normed_embedding
    face_vectors.append(vector)

print(f"Размер вектора: {len(face_vectors)}")
rimg = app.draw_on(img, faces)
cv2.imwrite("./t1_out.jpg", rimg)