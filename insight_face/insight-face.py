import io
import cv2
import insightface
from face_analysis import app
from fastapi import FastAPI, File, UploadFile
import numpy as np
import base64
from PIL import Image

app.prepare(ctx_id=0, det_size=(640, 640))

apps = FastAPI()

@apps.post("/data")
async def create_data(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        img = Image.open(io.BytesIO(file_content))
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
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

        encoded_image = base64.b64encode(img_bytes).decode('utf-8')

        return {"image": encoded_image, "face_vectors": face_vectors, "face_boxes": face_boxes}
    except Exception as e:
        return {"Error": str(e)}