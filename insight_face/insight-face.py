import io
import cv2
import insightface
#from insightface.app import FaceAnalysis
from face_analysis import app
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import numpy as np
import base64
import os
import time
from PIL import Image

#app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))

apps = FastAPI()

save_dir = '/app/saved_images'
os.makedirs(save_dir, exist_ok=True)

@apps.post("/data")
async def create_data(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        img = Image.open(io.BytesIO(file_content))
        img = np.array(img)

        faces = app.get(img)

        face_vectors = []
        face_boxes = []
        for face in faces:
            vector = face.normed_embedding
            face_vectors.append(vector.tolist())
            face_boxes.append(face.bbox.tolist())

        rimg = app.draw_on(img, faces)
        ret, buffer = cv2.imencode('.jpg', rimg)
        img_bytes = buffer.tobytes()
#Временно
        save_path = os.path.join(save_dir, f'processed_{int(time.time())}.jpg')
        cv2.imwrite(save_path, rimg)
        print(f'Обработанное изображение сохранено: {save_path}')
#///
        base64_encoded = base64.b64encode(img_bytes).decode('utf-8')

        return {"image": base64_encoded, "face_vectors": face_vectors, "face_boxes": face_boxes}

    except Exception as e:
        return {"error": str(e)}