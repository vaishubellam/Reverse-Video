from flask import Flask, request, jsonify, send_file, send_from_directory
import os
from reverse_video import reverse_video  # Import your model

app = Flask(__name__)

# Create directories for uploads and outputs if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Serve the frontend HTML file
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/process-video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    video_file = request.files['video']
    
    # Define input and output paths
    input_path = os.path.join("uploads", video_file.filename)
    output_path = os.path.join("outputs", f"reversed_{video_file.filename}")

    # Save uploaded video to input path
    try:
        video_file.save(input_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save video: {str(e)}"}), 500

    # Call the reverse_video model to process the file
    try:
        reverse_video(input_path, output_path)
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500
    
    # Return the output file to the frontend
    try:
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"Failed to send file: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)  # No need to specify a port
