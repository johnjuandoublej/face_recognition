from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from dbhelper import *
import cv2
import face_recognition
import os
import threading
import base64
import numpy as np
import time

app = Flask(__name__)
upload_folder = "static/img"
app.config["UPLOAD_FOLDER"] = upload_folder
app.secret_key = "!@#$"



# known_face_encodings = []

# def load_known_faces():
#     global known_face_encodings, known_names
#     users = getall('users')
#     known_face_encodings = []
#     known_names = []

#     for user in users:
#         if 'image' in user:
#             image_path = user['image']
#             image = face_recognition.load_image_file(image_path)
#             face_encodings = face_recognition.face_encodings(image)

#             if len(face_encodings) > 0:
#                 known_face_encodings.extend(face_encodings)
#                 known_names.extend([user['name']] * len(face_encodings))

# # Call the function to initialize known_face_encodings and known_names
    
# load_known_faces()
# print(known_face_encodings)



# Initialize video capture
video_capture = cv2.VideoCapture(0)
known_names = ["Known User"]

def video_feed_generator():
    global video_capture
    if video_capture is None or not video_capture.isOpened():
        print("Error: Unable to open video capture.")
        return

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)
        for face_location in face_locations:
            top, right, bottom, left = face_location
            face_encodings = face_recognition.face_encodings(frame, [face_location])
            if len(face_encodings) > 0:
                face_encoding = face_encodings[0]
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                name = known_names[matches.index(True)] if True in matches else "Unknown"
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
                print("Recognized Name:", name)

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(video_feed_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')


# def load_known_faces(image_paths, names):
#     known_face_encodings = []
#     known_names = []
#     print(image_paths)
#     for image_path, name in zip(image_paths, names):
#         try:
#             image = face_recognition.load_image_file(image_path)
#             face_encodings = face_recognition.face_encodings(image)
#             known_face_encodings.extend(face_encodings)
#             known_names.extend([name] * len(face_encodings))
#         except Exception as e:
#             print(f"Error loading image '{image_path}': {e}")

#     return known_face_encodings, known_names


def recognize_faces(frame):
    try:
        names = []
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # image = face_recognition.load_image_file("static/img/Bruce.jpg")
        # encoding = face_recognition.face_encodings(image)[0]
        # print(encoding)
        # print(image)
        getAllUsers = getall("users")


        for face_encoding in face_encodings:
            for row in getAllUsers:
                imagePath = row[4]
                known_image = face_recognition.load_image_file(imagePath)
                encoding = face_recognition.face_encodings(known_image)[0]
                matches = face_recognition.compare_faces([encoding], face_encoding)
                name = "Unknown"
                if True in matches:
                    first_match_index = matches.index(True)
                    isUser = known_names[first_match_index]
                    print(first_match_index)
                    names.append({
                        "name": row[1],
                        "coordinates": face_locations
                    })

        return names
    except Exception as e:
        print(f"Error in recognize_faces: {e}")
        return []

    

@app.route("/login", methods=["POST"])
def login():
    try:
        if 'picture' in request.form:
            img_data = request.form['picture'].split(",")[1]
            # print(img_data)
            nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            recognized_names = recognize_faces(frame)
            return jsonify({"recognized_names": recognized_names})
    except Exception as e:
        print(f"Error in /login route: {e}")

@app.route("/")
def main():
    rows = getall('users')
    return render_template('home.html', title="USERS", userlist=rows)


@app.route("/deleteuser", methods=["GET"])
def deleteuser() -> None:
    id = request.args.get('id')
    ok = deleterecord('users', id=id)
    return redirect(url_for('main'))


@app.route("/upload", methods=["POST", "GET"])
def upload() -> None:
    if request.method == "POST":
        image = request.files['image']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        imagename = upload_folder+'/' + name + '.jpg'
        image.save(imagename)
        ok = addrecord('users', name=name, email=email,password=password, image=imagename)
        if ok:
            flash("New user added")
        return redirect(url_for('main'))
    else:
        return render_template('upload.html', title="Register")


if __name__ == "__main__":

   

    video_thread = threading.Thread(target=video_feed_generator)
    video_thread.start()

    time.sleep(2)
    app.run(debug=True)