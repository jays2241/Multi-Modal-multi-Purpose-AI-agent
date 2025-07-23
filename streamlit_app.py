import streamlit as st
import logging
import tempfile
import os

from modules.notes_maker.notes_maker import make_notes_from_image
from modules.text_to_audio.text_to_audio import convert_text_to_audio
from modules.general_chatting.chat import return_chat
from modules.stock_market_sentiment.stock_sentiment import analyze_stock_sentiment


from intent_classifier.main import classify_intent


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


st.set_page_config(page_title="ChatGPT-style AI Agent", layout="centered")
st.title("Chat with Multi-Modal AI Agent")
st.caption("Powered by Intent Classification and AI Modules")


with st.form("chat_form"):
    prompt = st.text_input("Enter your message:")
    uploaded_file = st.file_uploader("Optional Attachment (Image/Audio)", type=["jpg", "jpeg", "png", "mp3", "wav", "m4a"])
    submit = st.form_submit_button("Send")


if submit and prompt:
    st.markdown(f"### You: {prompt}")

    try:
        intent = classify_intent(prompt, method='transformer')  # or 'ml' or 'rule_based'
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
            st.error("Please upload a valid image file for note generation.")

    elif intent == "convert_to_audio":
        st.subheader("Text to Speech")
        try:
            convert_text_to_audio(prompt, "converted_audio.mp3")
            st.audio("converted_audio.mp3")
        except Exception as e:
            st.error("Failed to convert text to audio.")
            logging.error("Text to speech failed", exc_info=True)

    elif intent == "stock_sentiment":
        st.subheader("Stock Market Sentiment Analysis")
        try:
            company_name = prompt.strip()
            formatted_name = company_name.lower().replace(" ", "-")
            url = f"https://www.moneycontrol.com/news/tags/{formatted_name}.html"

            df = analyze_stock_sentiment(url)
            if df.empty:
                st.warning(f"No news articles found for `{company_name}`.")
            else:
                st.success(f"News Sentiment for `{company_name}`")
                st.dataframe(df)
        except Exception as e:
            st.error(f"Error while fetching sentiment: {e}")
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

    else:
        st.warning("Unknown or unsupported intent.")
