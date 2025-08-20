# ------------------------Import necessary libraries--------------------
import streamlit as st
import logging
import tempfile
import os 
from modules.notes_maker.notes_maker import make_notes_from_image
from modules.text_to_audio.text_to_audio import convert_text_to_audio
from modules.general_chatting.chat import return_chat
from modules.stock_market_sentiment.stock_sentiment import analyze_stock_sentiment
from modules.stock_market_sentiment.name_extractor import extract_company_name
from modules.gmail.gmail_main import gmail_operation
import base64
from intent_classifier.main import classify_intent
from modules.gmail.sub_intent_classifier.gmail_sub_intent_classifier import predict_sub_intent

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

st.set_page_config(page_title="AI Agent", layout="centered")

# ---------------------------------asthetics-------------------------------------------
st.sidebar.markdown("**[🔗 LinkedIn- Jay Vijay Sawant](https://www.linkedin.com/in/jay-sawant-0011/)**", unsafe_allow_html=True)
def set_bg_from_local(img_path):
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

bg_folder = "backgrounds"
bg_files = [f for f in os.listdir(bg_folder) if f.endswith((".jpg", ".jpeg", ".png"))]

default_image = "Default.jpg"

if default_image in bg_files:
    bg_files.remove(default_image)
    bg_files.insert(0, default_image)
bg_files.insert(0, "None")

selected_bg = st.sidebar.selectbox("Choose Background", bg_files, index=1)

if selected_bg != "None":
    image_path = os.path.join(bg_folder, selected_bg)
    set_bg_from_local(image_path)

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


# -----------------------chat------------------

with st.form("chat_form"):
    prompt = st.text_input("Enter your message:")
    uploaded_file = st.file_uploader("Optional Attachment (Image/Audio)", type=["jpg", "jpeg", "png", "mp3", "wav", "m4a"])
    submit = st.form_submit_button("Send")

if submit and prompt:
    st.markdown(f"### You: {prompt}")

    try:
        intent = classify_intent(prompt, method=classifier_type)

        st.markdown(f"_Intent Detected: `{intent}`_")
    except Exception as e:
        st.error("Intent classification failed.")
        logging.error("Error during intent classification", exc_info=True)
        intent = None

    if intent == "make_notes":
        st.subheader("Note Maker from Image")
        if uploaded_file and uploaded_file.type.startswith("image/"):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                    tmp_img.write(uploaded_file.read())
                    image_path = tmp_img.name

                notes = make_notes_from_image(image_path)
                st.text_area("Extracted Notes", value=notes, height=200)

                audio_path = "notes_audio.mp3"
                convert_text_to_audio(notes, audio_path)
                st.audio(audio_path)
            except Exception as e:
                st.error("Failed to extract notes or generate audio.")
                logging.error("Error in make_notes workflow", exc_info=True)
            finally:
                os.remove(image_path)
        else:
            st.error("Please upload a valid image file.")

    elif intent == "convert_to_audio":
        st.subheader("Text to Speech")
        try:
            convert_text_to_audio(prompt, "converted_audio.mp3")
            st.audio("converted_audio.mp3")
        except Exception as e:
            st.error("Failed to convert text to audio.")
            logging.error("Text to audio conversion failed", exc_info=True)

    elif intent == "stock_sentiment":
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
            st.error("Error while fetching sentiment.")
            logging.error("Stock sentiment analysis failed", exc_info=True)

    elif intent == "general_chat":
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
        st.subheader("Gmail Operations")
        try:
            sub_intent = predict_sub_intent(prompt)
            st.markdown(f"_Gmail Sub-Intent: `{sub_intent}`_")
            result = gmail_operation(prompt)
            for idx, email in enumerate(result, 1):
                st.markdown(f"#### Email {idx}")
                st.markdown(f"- **From:** {email['From']}")
                st.markdown(f"- **Subject:** {email['Subject']}")
                st.markdown(f"- **Date:** {email['Date']}")
                st.markdown(f"- **Snippet:** {email['Snippet']}")
                st.text_area(f"Body of Email {idx}", email['Body'], height=150, key=f"email_body_{idx}")

            else:
                st.success(result)
        except Exception as e:
            st.error("Gmail operation failed.")
            logging.error("Gmail module failed", exc_info=True)

    else:
        st.warning("Unknown or unsupported intent.")

