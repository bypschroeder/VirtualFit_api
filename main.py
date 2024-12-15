import docker.types
from flask import Flask, request, jsonify
import os
import docker

app = Flask(__name__)

DATA_FOLDER = '/data'

client = docker.from_env()

@app.route("/")
def index():
    return "Hello, World!"

@app.route('/generate-3d-model', methods=['POST'])
def generate_3d_model():
    try:
        # if "image" not in request.files:
        #     return jsonify({'error': 'No image file provided'}), 400
        
        # image_file = request.files['image']

        # if image_file.filename == '':
        #     return jsonify({'error': 'No image file provided'}), 400
        
        # images_folder = os.path.join(DATA_FOLDER, 'images')
        # os.makedirs(images_folder, exist_ok=True)

        # image_path = os.path.join(images_folder, "sample.jpg")
        # image_file.save(image_path)

        result = client.containers.run("openpose", device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])], command=f"--image_dir {DATA_FOLDER}/images --write_json {DATA_FOLDER}/keypoints --face --hand --display 0 --render_pose 0", remove=True, volumes={DATA_FOLDER: {'bind': DATA_FOLDER, 'mode': 'rw'}})

        return jsonify({
            "message": "OpenPose execution successful",
            "output": result.output.decode("utf-8")
        }), 200
    except docker.errors.NotFound as e:
        return jsonify({'error': e}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)