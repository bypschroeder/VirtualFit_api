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

        result = client.containers.run("openpose/openpose:latest", command=f"--image_dir {DATA_FOLDER}/images --write_json {DATA_FOLDER}/keypoints --display 0 --write_images 0", remove=True)
        print(result)

        return jsonify({
            "message": "OpenPose execution successful",
            "output": result.output.decode("utf-8")
        }), 200
    except docker.errors.NotFound:
        return jsonify({'error': 'OpenPose container not found'}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)