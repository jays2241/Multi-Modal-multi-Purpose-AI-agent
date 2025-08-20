import streamlit as st
import logging
import tempfile
import os
import base64

# ------------------------ Logging setup ------------------------
logging.basicConfig(
    filename="ai_agent.log",  # logs stored in file
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------------ Safe module imports ------------------------
# Notes Maker
notes_module_available = True
ollama_available = True
try:
    from modules.notes_maker.notes_maker import make_notes_from_image
    from modules.notes_maker.gpt_formatter import format_text_with_gpt
    import ollama
except ModuleNotFoundError as e:
    notes_module_available = False
    ollama_available = False
    logging.warning("Notes Maker or Ollama module not found: %s", e)

# Text to Audio
text_to_audio_available = True
try:
    from modules.text_to_audio.text_to_audio import convert_text_to_audio
except ModuleNotFoundError as e:
    text_to_audio_available = False
    logging.warning("Text-to-Audio module not found: %s", e)

# General Chat
general_chat_available = True
try:
    from modules.general_chatting.chat import return_chat
except ModuleNotFoundError as e:
    general_chat_available = False
    logging.warning("General Chat module not found: %s", e)

# Stock Sentiment
stock_sentiment_available = True
try:
    from modules.stock_market_sentiment.stock_sentiment import analyze_stock_sentiment
    from modules.stock_market_sentiment.name_extractor import extract_company_name
except ModuleNotFoundError as e:
    stock_sentiment_available = False
    logging.warning("Stock Sentiment module not found: %s", e)

# Gmail
gmail_available = True
try:
    from modules.gmail.gmail_main import gmail_operation
    from modules.gmail.sub_intent_classifier.gmail_sub_intent_classifier import predict_sub_intent
except ModuleNotFoundError as e:
    gmail_available = False
    logging.warning("Gmail module not found: %s", e)

# Intent Classifier
intent_classifier_available = True
try:
    from intent_classifier.main import classify_intent
except ModuleNotFoundError as e:
    intent_classifier_available = False
    logging.warning("Intent Classifier module not found: %s", e)

# -------------------------- UI aesthetics --------------------------
st.set_page_config(page_title="AI Agent", layout="centered")

st.sidebar.markdown(
    "**[🔗 LinkedIn- Jay Vijay Sawant](https://www.linkedin.com/in/jay-sawant-0011/)**",
    unsafe_allow_html=True
)

def set_bg_from_local(img_path):
    try:
        with open(img_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            css = f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpeg;base64,{encoded_string}");
                background-size: cover;
            }}
            </style>
            """
            st.markdown(css, unsafe_allow_html=True)
    except Exception as e:
        logging.error("Failed to set background image", exc_info=True)

bg_folder = "backgrounds"
bg_files = [f for f in os.listdir(bg_folder) if f.endswith((".jpg", ".jpeg", ".png"))]
default_image = "Default.jpg"
if default_image in bg_files:
    bg_files.remove(default_image)
    bg_files.insert(0, default_image)
bg_files.insert(0, "None")

selected_bg = st.sidebar.selectbox("Choose Background", bg_files, index=1)
if selected_bg != "None":
    set_bg_from_local(os.path.join(bg_folder, selected_bg))

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    classifier_type = st.selectbox(
        "Select Intent Classifier",
        ["ml", "rule_based", "transformer"],
        index=0,
        help="Choose the method for intent classification"
    )

st.title("Chat with Multi-Purpose AI Agent")
st.caption("Legends don’t use templates — Built from scratch by Jay & Jeswin 🔥")

# ----------------------- Chat form -----------------------
with st.form("chat_form"):
    prompt = st.text_input("Enter your message:")
    uploaded_file = st.file_uploader(
        "Optional Attachment (Image/Audio)", 
        type=["jpg", "jpeg", "png", "mp3", "wav", "m4a"]
    )
    submit = st.form_submit_button("Send")

if submit and prompt:
    st.markdown(f"### You: {prompt}")

    # ----------------------- Intent Classification -----------------------
    try:
        if not intent_classifier_available:
            raise ModuleNotFoundError("Intent Classifier module not available.")
        intent = classify_intent(prompt, method=classifier_type)
        st.markdown(f"_Intent Detected: `{intent}`_")
    except Exception as e:
        st.error("Could not detect intent. Please try again.")
        logging.error("Error during intent classification", exc_info=True)
        intent = None

    # ----------------------- Workflows based on intent -----------------------
    try:
        if intent == "make_notes":
            if not notes_module_available or not ollama_available:
                st.error("Notes Maker feature is not available. Required module missing.")
            else:
                st.subheader("Note Maker from Image")
                if uploaded_file and uploaded_file.type.startswith("image/"):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                            tmp_img.write(uploaded_file.read())
                            image_path = tmp_img.name

                        notes = make_notes_from_image(image_path)
                        st.text_area("Extracted Notes", value=notes, height=200)

                        if text_to_audio_available:
                            audio_path = "notes_audio.mp3"
                            convert_text_to_audio(notes, audio_path)
                            st.audio(audio_path)
                    except Exception as e:
                        st.error("Failed to extract notes or generate audio.")
                        logging.error("Error in make_notes workflow", exc_info=True)
                    finally:
                        if os.path.exists(image_path):
                            os.remove(image_path)
                else:
                    st.error("Please upload a valid image file.")

        elif intent == "convert_to_audio":
            if not text_to_audio_available:
                st.error("Text-to-Audio feature is not available.")
            else:
                st.subheader("Text to Speech")
                try:
                    convert_text_to_audio(prompt, "converted_audio.mp3")
                    st.audio("converted_audio.mp3")
                except Exception as e:
                    st.error("Failed to convert text to audio.")
                    logging.error("Text to audio conversion failed", exc_info=True)

        elif intent == "stock_sentiment":
            if not stock_sentiment_available:
                st.error("Stock Sentiment feature is not available.")
            else:
                st.subheader("Stock Market Sentiment Analysis")
                try:
                    company_name, news_url = extract_company_name(prompt)
                    if not company_name or not news_url:
                        st.warning("Could not extract a valid company name. Try again.")
                    else:
                        df = analyze_stock_sentiment(news_url)
                        if df.empty:
                            st.warning(f"No news articles found for `{company_name}`.")
                        else:
                            st.success(f"News Sentiment for `{company_name}`")
                            st.dataframe(df)
                except Exception as e:
                    st.error("Error while fetching stock sentiment.")
                    logging.error("Stock sentiment analysis failed", exc_info=True)

        elif intent == "general_chat":
            if not general_chat_available:
                st.error("General Chat feature is not available.")
            else:
                st.subheader("General Chat")
                try:
                    response = return_chat(prompt)
                    st.success("Response:")
                    st.write(response)
                except Exception as e:
                    st.error("Failed to generate chat response.")
                    logging.error("General chat error", exc_info=True)

        elif intent == "voice_summary":
            st.subheader("Audio Summarization (Coming Soon)")
            st.info("Audio summarization is not yet implemented.")

        elif intent == "gmail_operations":
            if not gmail_available:
                st.error("Gmail Operations feature is not available.")
            else:
                st.subheader("Gmail Operations")
                try:
                    sub_intent = predict_sub_intent(prompt)
                    st.markdown(f"_Gmail Sub-Intent: `{sub_intent}`_")
                    result = gmail_operation(prompt)
                    for idx, email in enumerate(result, 1):
                        st.markdown(f"#### Email {idx}")
                        st.markdown(f"- **From:** {email.get('From','N/A')}")
                        st.markdown(f"- **Subject:** {email.get('Subject','N/A')}")
                        st.markdown(f"- **Date:** {email.get('Date','N/A')}")
                        st.markdown(f"- **Snippet:** {email.get('Snippet','N/A')}")
                        st.text_area(f"Body of Email {idx}", email.get('Body',''), height=150, key=f"email_body_{idx}")
                except Exception as e:
                    st.error("Gmail operation failed.")
                    logging.error("Gmail module failed", exc_info=True)

        else:
            st.warning("Unknown or unsupported intent.")

    except Exception as e:
        st.error("An unexpected error occurred. Please try again.")
        logging.error("Unexpected error in main workflow", exc_info=True)
