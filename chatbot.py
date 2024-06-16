import gradio as gr
import requests

OLLAMA_API_URL = "https://8ae4-103-123-226-98.ngrok-free.app/api/generate"
messages = []  # Initialize empty list for chat history

# Function to add user input to chat history
def add_text(history, text):
    global messages
    print(f"User input: {text}")
    history.append((text, ''))  # Append to history as a tuple with empty response
    messages.append({"role": 'user', 'content': text})  # Append to messages list
    return history, ""

# Function to generate response using Ollama API
def generate(history):
    global messages
    
    # Construct the prompt from the chat history
    prompt = ' '.join([msg['content'] for msg in messages if msg['role'] == 'user'])
    print(f"Generated prompt: {prompt}")
    
    # Construct payload for API request
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    
    # Send POST request to Ollama API
    response = requests.post(OLLAMA_API_URL, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        generated_text = result.get("response", "")
        print(f"API response: {generated_text}")
        
        # Add the generated text to the latest user input in history
        history[-1] = (history[-1][0], generated_text)
        
        # Return the updated history
        return history
    else:
        # Handle API request error gracefully
        print(f"Error: {response.status_code} - {response.reason}")
        return history  # Return unchanged history on error

# Initialize Gradio interface
with gr.Blocks(css="""
    .gradio-container .gr-text-input textarea { 
        border-radius: 0; 
    } 
    .gradio-container .gr-button { 
        border-radius: 0; 
        padding: 6px 10px; 
        font-size: 14px; 
        height: 40px; 
        margin-left: -1px; 
    }
    .gradio-container .gr-row { 
        display: flex; 
        align-items: center; 
    }
""") as demo:
    chatbot = gr.Chatbot(value=[], elem_id="chatbot")
    with gr.Row():
        with gr.Column(scale=12):
            txt = gr.Textbox(
                show_label=False,
                placeholder="Enter text and press enter",
                lines=1
            )
        with gr.Column(scale=1, min_width=50):
            send_button = gr.Button(value="Send", variant="primary")
        
    def send_and_clear(history, text):
        # Add the text to history
        history, _ = add_text(history, text)
        
        # Clear the input field
        return history, ""
        
    # Link send_and_clear to both button click and textbox submit
    txt.submit(send_and_clear, [chatbot, txt], [chatbot, txt], queue=False).then(
        generate, inputs=[chatbot], outputs=chatbot,
    )
    send_button.click(send_and_clear, [chatbot, txt], [chatbot, txt], queue=False).then(
        generate, inputs=[chatbot], outputs=chatbot,
    )
    
demo.queue()
demo.launch(debug=True)
