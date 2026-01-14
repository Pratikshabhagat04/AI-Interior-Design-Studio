# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.responses import StreamingResponse, JSONResponse
# from PIL import Image
# import google.generativeai as genai
# import io, os, uuid
# from dotenv import load_dotenv

# # ----------------------------
# # CONFIG
# # ----------------------------
# load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# text_model = genai.GenerativeModel("gemini-2.5-flash")
# image_model = genai.GenerativeModel("gemini-2.5-flash-image")

# app = FastAPI(title="AI Interior Designer API")

# # Make sure upload folder exists
# UPLOAD_FOLDER = "images"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # ----------------------------
# # API 1: Upload Image + assign unique ID
# # ----------------------------
# @app.post("/upload-image")
# async def upload_image(image: UploadFile = File(...)):
#     try:
#         # Generate unique ID
#         image_id = str(uuid.uuid4())
#         ext = os.path.splitext(image.filename)[1]
#         save_path = os.path.join(UPLOAD_FOLDER, f"{image_id}{ext}")

#         # Save uploaded image
#         with open(save_path, "wb") as f:
#             f.write(await image.read())

#         return {"status": "success", "image_id": image_id, "filename": f"{image_id}{ext}"}

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})


# # ----------------------------
# # API 2: Generate Interior using stored image AND save output
# # ----------------------------
# @app.post("/generate-interior")
# async def generate_interior(
#     image_id: str = Form(...),
#     room_type: str = Form(...),
#     style: str = Form(...),
#     color_theme: str = Form(...),
#     budget: str = Form(...),
#     ceiling: str = Form(...)
# ):
#     try:
#         # Locate stored image
#         files = os.listdir(UPLOAD_FOLDER)
#         matched_files = [f for f in files if f.startswith(image_id)]
#         if not matched_files:
#             return JSONResponse(status_code=404, content={"error": "Image ID not found"})
#         image_path = os.path.join(UPLOAD_FOLDER, matched_files[0])

#         # Open image
#         original_image = Image.open(image_path).convert("RGB")

#         # ----------------------------
#         # Text analysis
#         # ----------------------------
#         analysis_prompt = f"""
# You are a professional interior designer.

# Analyze the uploaded {room_type} image.

# STRICT RULE:
# - Keep layout unchanged

# Design preferences:
# - Style: {style}
# - Color theme: {color_theme}
# - Budget: {budget}
# - Ceiling: {ceiling}

# Create a photorealistic image generation prompt.
# """
#         text_response = text_model.generate_content([analysis_prompt, original_image])
#         design_prompt = text_response.text

#         # ----------------------------
#         # Image generation
#         # ----------------------------
#         image_prompt = f"""
# STRICT IMAGE EDITING TASK.

# Use the uploaded image as the BASE IMAGE.

# DO NOT change:
# - Room structure
# - Camera angle
# - Image size

# ONLY change:
# - Interior design elements
# - Furniture, lighting, decor
# - Style and colors

# {design_prompt}

# Ultra-realistic interior photography.
# """

#         image_response = image_model.generate_content([original_image, image_prompt])

#         for part in image_response.candidates[0].content.parts:
#             if part.inline_data:
#                 generated_image = Image.open(io.BytesIO(part.inline_data.data))
#                 # Force same size
#                 generated_image = generated_image.resize(original_image.size)

#                 # ----------------------------
#                 # SAVE GENERATED IMAGE TO FOLDER
#                 # ----------------------------
#                 output_filename = f"{image_id}_generated.png"
#                 output_path = os.path.join(UPLOAD_FOLDER, output_filename)
#                 generated_image.save(output_path, format="PNG")

#                 # ----------------------------
#                 # RETURN IMAGE AS RESPONSE
#                 # ----------------------------
#                 buffer = io.BytesIO()
#                 generated_image.save(buffer, format="PNG")
#                 buffer.seek(0)

#                 return StreamingResponse(buffer, media_type="image/png")

#         return JSONResponse(status_code=500, content={"error": "Image generation failed"})

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})



from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from PIL import Image
import google.generativeai as genai
import io, os, uuid
from dotenv import load_dotenv

# ----------------------------
# CONFIG
# ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

text_model = genai.GenerativeModel("gemini-2.5-flash")
image_model = genai.GenerativeModel("gemini-2.5-flash-image")

app = FastAPI(title="AI Interior Designer API")

# ----------------------------
# FOLDERS
# ----------------------------
UPLOAD_FOLDER = "images/uploads"
GENERATED_FOLDER = "images/generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

# ----------------------------
# API 1: Upload Image + assign unique ID
# ----------------------------
@app.post("/upload-image")
async def upload_image(image: UploadFile = File(...)):
    try:
        # Generate unique ID
        image_id = str(uuid.uuid4())
        ext = os.path.splitext(image.filename)[1]
        save_path = os.path.join(UPLOAD_FOLDER, f"{image_id}{ext}")

        # Save uploaded image
        with open(save_path, "wb") as f:
            f.write(await image.read())

        return {"status": "success", "image_id": image_id, "filename": f"{image_id}{ext}"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ----------------------------
# API 2: Generate Interior using stored image AND save output
# ----------------------------
@app.post("/generate-interior")
async def generate_interior(
    image_id: str = Form(...),
    room_type: str = Form(...),
    style: str = Form(...),
    color_theme: str = Form(...),
    budget: str = Form(...),
    ceiling: str = Form(...)
):
    try:
        # Locate stored uploaded image
        files = os.listdir(UPLOAD_FOLDER)
        matched_files = [f for f in files if f.startswith(image_id)]
        if not matched_files:
            return JSONResponse(status_code=404, content={"error": "Image ID not found"})
        image_path = os.path.join(UPLOAD_FOLDER, matched_files[0])

        # Open image
        original_image = Image.open(image_path).convert("RGB")

        # ----------------------------
        # Text analysis
        # ----------------------------
        analysis_prompt = f"""
You are a professional interior designer.

Analyze the uploaded {room_type} image.

STRICT RULE:
- Keep layout unchanged

Design preferences:
- Style: {style}
- Color theme: {color_theme}
- Budget: {budget}
- Ceiling: {ceiling}

Create a photorealistic image generation prompt.
"""
        text_response = text_model.generate_content([analysis_prompt, original_image])
        design_prompt = text_response.text

        # ----------------------------
        # Image generation
        # ----------------------------
        image_prompt = f"""
STRICT IMAGE EDITING TASK.

Use the uploaded image as the BASE IMAGE.

DO NOT change:
- Room structure
- Camera angle
- Image size

ONLY change:
- Interior design elements
- Furniture, lighting, decor
- Style and colors

{design_prompt}

Ultra-realistic interior photography.
"""

        image_response = image_model.generate_content([original_image, image_prompt])

        for part in image_response.candidates[0].content.parts:
            if part.inline_data:
                generated_image = Image.open(io.BytesIO(part.inline_data.data))
                # Force same size
                generated_image = generated_image.resize(original_image.size)

                # ----------------------------
                # SAVE GENERATED IMAGE TO SEPARATE FOLDER
                # ----------------------------
                output_filename = f"{image_id}_generated.png"
                output_path = os.path.join(GENERATED_FOLDER, output_filename)
                generated_image.save(output_path, format="PNG")

                # ----------------------------
                # RETURN IMAGE AS RESPONSE
                # ----------------------------
                buffer = io.BytesIO()
                generated_image.save(buffer, format="PNG")
                buffer.seek(0)

                return StreamingResponse(buffer, media_type="image/png")

        return JSONResponse(status_code=500, content={"error": "Image generation failed"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
