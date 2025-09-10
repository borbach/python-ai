import gradio as gr

def sentiment_analysis(text):
    return "Positive" if "good" in text else "Negative"

gr.Interface(fn=sentiment_analysis, inputs="text", outputs="text").launch()

