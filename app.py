
import streamlit as st
from PIL import Image
import google.generativeai as genai
import io
import os

# ----------------------------
# CONFIGURE GEMINI
# ----------------------------
genai.configure(api_key="AIzaSyApKxQvUpkhlB1C1JdtCnzU3dzSmG1T47s")

text_model = genai.GenerativeModel("gemini-2.5-flash")
image_model = genai.GenerativeModel("gemini-2.5-flash-image")

# ----------------------------
# STREAMLIT CONFIG
# ----------------------------
st.set_page_config(page_title="AI Interior Designer", layout="wide")
st.title("AI Interior Design Studio")

# ----------------------------
# STATE INIT (IMPORTANT)
# ----------------------------
if "image" not in st.session_state:
    st.session_state.image = None

if "design_text" not in st.session_state:
    st.session_state.design_text = None

# ----------------------------
# UI LAYOUT
# ----------------------------
left, right = st.columns(2)

with left:
    uploaded_image = st.file_uploader(
        "Upload Room Image",
        type=["jpg", "jpeg", "png"]
    )

    style = st.selectbox(
        "Interior Style",
        ["Modern", "Minimalist", "Luxury", "Scandinavian", "Indian Contemporary"]
    )

    room_type = st.selectbox(
        "Room Type",
        ["Living Room", "Bedroom", "Office", "Kitchen"]
    )

    color_theme = st.selectbox(
        "Color Theme",
        ["Neutral", "Warm", "Cool", "Earthy"]
    )

    budget = st.selectbox(
        "Budget Level",
        ["Low", "Medium", "Luxury"]
    )

    celink = st.selectbox(
        "Ceiling Type",
        ["Fan", "Chandelier", "POP"]
    )

with right:
    if uploaded_image:
        st.session_state.image = Image.open(uploaded_image).convert("RGB")
        st.image(
            st.session_state.image,
            caption="Original Room",
            # use_container_width=True
            width="stretch"

        )

# ----------------------------
# STEP 1: TEXT DESIGN
# ----------------------------
if uploaded_image and st.button("Generate Interior Design Plan"):

    with st.spinner("Analyzing room with Gemini..."):

        analysis_prompt = f"""
You are a professional interior designer.

Analyze the uploaded {room_type} image.

Requirements:
- Style: {style}
- Color theme: {color_theme}
- Budget: {budget}
- Keep layout unchanged

Provide:
1. Detailed design description
2. Furniture & decor
3. Lighting plan
4. Color & material palette
5. FINAL photorealistic image generation prompt
"""

        response = text_model.generate_content(
            [analysis_prompt, st.session_state.image]
        )

        st.session_state.design_text = response.text

    st.success("Design Analysis Complete")

# ----------------------------
# DISPLAY DESIGN PLAN
# ----------------------------
if st.session_state.design_text:
    st.subheader("Interior Design Plan")
    st.write(st.session_state.design_text)

# ----------------------------
# STEP 2: IMAGE GENERATION
# ----------------------------
if uploaded_image and st.session_state.design_text and st.button("Generate Final Interior Image"):

    st.subheader("Generated Interior Image")

    with st.spinner("Generating AI interior image..."):

        image_prompt = f"""
STRICT IMAGE EDITING TASK.

Use the uploaded image as the BASE IMAGE.

ABSOLUTE RULES:
- KEEP exact room size and proportions
- KEEP same camera angle
- KEEP walls, doors, windows, ceiling position unchanged
- DO NOT change layout or structure

ONLY CHANGE:
- Room type: {room_type}
- Interior style: {style}
- Color theme: {color_theme}
- Budget level: {budget}
- Ceiling type: {celink}
- Furniture, lighting, decor, materials

Make it ultra-realistic, interior photography, natural lighting.
"""

        image_response = image_model.generate_content(
            [st.session_state.image, image_prompt]
        )

        for part in image_response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                generated_image = Image.open(io.BytesIO(image_bytes))

                # FORCE SAME SIZE AS ORIGINAL
                generated_image = generated_image.resize(
                    st.session_state.image.size
                )

                st.image(
                        generated_image,
                        caption="AI Generated Interior (Same Size & Layout)",
                        width="stretch"
                    )


                # ----------------------------
                # DOWNLOAD BUTTON
                # ----------------------------
                buffer = io.BytesIO()
                generated_image.save(buffer, format="PNG")
                buffer.seek(0)

                st.download_button(
                    label="⬇️ Download Interior Image (PNG)",
                    data=buffer,
                    file_name="ai_interior_design.png",
                    mime="image/png"
                )
