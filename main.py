import docker.types
from flask import Flask, request, jsonify, send_file
import os
import docker

app = Flask(__name__)

DATA_FOLDER = '../data'

client = docker.from_env()

@app.route("/")
def index():
    return "Hello, World!"

@app.route('/generate-3d-model', methods=['POST'])
def generate_3d_model():
    try:
        if "gender" not in request.form:
            return jsonify({'error': 'No gender provided'}), 400

        gender = request.form['gender']
        if gender not in ['male', 'neutral', 'female']:
            return jsonify({'error': 'Invalid gender provided'}), 400
        
        if "image" not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify({'error': 'No image file provided'}), 400
        
        images_folder = os.path.join(DATA_FOLDER, 'images')
        os.makedirs(images_folder, exist_ok=True)

        image_path = os.path.join(images_folder, "sample.jpg")
        image_file.save(image_path)

        client.containers.run("openpose", device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])], command=f"--image_dir {DATA_FOLDER}/images --write_json {DATA_FOLDER}/keypoints --face --hand --display 0 --render_pose 0", remove=True, volumes={"virtualfit_data": {"bind": "/data", "mode": "rw"}})

        client.containers.run("smplify-x", device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])], command=f"python3 smplifyx/main.py --config cfg_files/fit_smplx.yaml --data_folder {DATA_FOLDER} --output_folder {DATA_FOLDER}/smplify-x_results --visualize=False --gender={gender} --model_folder ../smplx/models --vposer_ckpt ../vposer/V02_05", remove=True, volumes={"virtualfit_data": {"bind": "/data", "mode": "rw"}})

        obj_file_path = os.path.join(DATA_FOLDER, 'smplify-x_results', 'meshes', 'sample', '000.obj')
        if not os.path.exists(obj_file_path):
            return jsonify({'error': 'Failed to generate 3D model, .obj file not found'}), 400
        
        os.remove(image_path)

        return send_file(obj_file_path, as_attachment=True)
    except docker.errors.NotFound as e:
        return jsonify({'error': e}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)