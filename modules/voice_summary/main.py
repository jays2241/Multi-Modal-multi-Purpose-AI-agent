from .summarize_transcribe import summarize_transcribe
from .voice_transcribe import transcribe_audio_file

def summarize_audio(file_path, model_size="base", gpt_model="llama3.1"):
    """
    Transcribe and summarize an audio file.
    
    :param file_path: Path to the audio file.
    :param model_size: Size of the Whisper model to use for transcription.
    :param gpt_model: Model to use for summarization.
    :return: Summary of the audio content.
    """
    try:
        # Transcribe the audio file
        transcribed_text = transcribe_audio_file(file_path, model_size)
        print("Transcription successful. Summarizing...")
        
        # Summarize the transcribed text
        summary = summarize_transcribe(transcribed_text, model=gpt_model)
        return summary
    
    except Exception as e:
        return f"⚠️ Error processing audio file: {e}"
    
if __name__ == "__main__":
    file_path = "C:\\Users\\91966\\Desktop\\Recording.m4a"
    summary = summarize_audio(file_path)
    print("Audio Summary:\n", summary)