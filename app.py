import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import io
from PIL import Image
import base64
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Set your Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -----------------------------------------------------
# 🔹 Generate design endpoint
# -----------------------------------------------------
@app.route("/generate", methods=["POST"])
def generate_design():
    try:
        print("🚀 /generate endpoint called")

        # 1️⃣ Get uploaded image and keyword
        image_file = request.files.get("image")
        keyword = request.form.get("keyword")

        if not image_file or not keyword:
            return jsonify({"error": "Missing image or keyword"}), 400

        # 2️⃣ Save uploaded image
        image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(image_path)
        print(f"💾 Uploaded image saved to: {image_path}")

        # 3️⃣ Prepare prompt for Gemini
        prompt = (
            f"You are an AI interior designer. Using the provided reference image as inspiration, "
            f"generate a realistic aluminum-themed interior design for a {keyword}. "
            f"Focus on aluminum frames, partitions, furniture, and decor. "
            f"Maintain the same room layout, lighting, and realism."
        )
        print(f"🧠 Prompt ready: {prompt}")

        # 4️⃣ Load image bytes
        with open(image_path, "rb") as img_file:
            img_bytes = io.BytesIO(img_file.read())

        # 5️⃣ Initialize Gemini model
        model = genai.GenerativeModel("gemini-2.0-flash")  # ✅ Supports image input/output
        print("🎨 Generating design with Gemini 2.0 Flash ...")

        response = model.generate_content(
            [prompt, {"mime_type": "image/png", "data": img_bytes.getvalue()}],
            generation_config={"temperature": 0.8},
        )

        # 6️⃣ Extract and save generated image
        if not response or not response.candidates:
            raise ValueError("No candidates returned from Gemini")

        image_data = response.candidates[0].content.parts[0].inline_data.data
        image_bytes = base64.b64decode(image_data)

        output_filename = "generated_design.png"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        with open(output_path, "wb") as f:
            f.write(image_bytes)

        print(f"✅ Generated design saved to: {output_path}")

        # 7️⃣ Return full URL for frontend
        return jsonify({"generated_image": f"http://127.0.0.1:8000/generated/generated_design.png"})


    except Exception as e:
        print("🔥 Error during generation:")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------
# 🔹 Serve uploaded images
# -----------------------------------------------------
@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# -----------------------------------------------------
# 🔹 Serve generated images
# -----------------------------------------------------
@app.route("/generated/<path:filename>")
def serve_generated(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

# -----------------------------------------------------
# 🔹 Root test route
# -----------------------------------------------------
@app.route("/")
def root():
    return jsonify({"message": "AI Aluminum Interior Generator API running successfully!"})

# -----------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
