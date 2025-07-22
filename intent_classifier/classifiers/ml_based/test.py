import pickle

with open("./model/intent_classifier_pipeline.pkl", "rb") as f:
    model = pickle.load(f)

def predict_intent(text):
    return model.predict([text])[0]

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        intent = predict_intent(user_input)
        print(f"Predicted Intent: {intent}")
