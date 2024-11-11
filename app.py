from flask import Flask, render_template, request, Response, stream_with_context, send_file, jsonify
from rag_agent import query_agent
from tts_run import get_audio
from stt_run import record_audio
from Wake_word import listen_for_wake_word
import tempfile
import threading
import time
import csv
import os

app = Flask(__name__)

# API key and file paths
data_file_path = "./Data/Database_files/Sample.pdf"
embedding_data_path = "./Data/Embedding_Store/"

# Load exhibit data
with open("./Data/Database_files/exhibit_data.csv", "r") as file:
    reader = csv.DictReader(file)
    exhibit_data = list(reader)

# Flask routes
@app.route('/')
def home():
    return render_template('home.html', active_page='home')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html', active_page='chatbot')

@app.route('/about')
def about():
    return render_template('about.html', active_page='about')

@app.route('/exhibits')
def exhibits():
    return render_template('exhibits.html', exhibits=exhibit_data, active_page='exhibits')

@app.route('/exhibit/<int:exhibit_id>')
def exhibit_page(exhibit_id):
    exhibit = get_exhibit_by_id(exhibit_id)
    if exhibit:
        # main(exhibit['long_description']) # updated
        return render_template('exhibit.html', exhibit=exhibit, exhibit_id=exhibit_id)
    return "Exhibit not found", 404

@app.route('/tour/<int:current_id>')
def tour(current_id):
    exhibit = get_exhibit_by_id(current_id)
    if exhibit:
        # exhibit_text = f"{exhibit['exhibit_name']}. {exhibit['short_description']}." # updated
        # speak(exhibit_text)
        next_id = current_id + 1 if current_id < len(exhibit_data) else None
        prev_id = current_id - 1 if current_id > 1 else None
        return render_template('tour.html', exhibit=exhibit, current_id=current_id, next_id=next_id, prev_id=prev_id)
    return "Exhibit not found", 404

def get_exhibit_by_id(exhibit_id):
    return exhibit_data[exhibit_id - 1]

conversation_file = 'messages.txt'
# Audio file handling
AUDIO_FOLDER = 'static/audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

def save_message(message, sender='user'):
    with open(conversation_file, 'a') as f:
        f.write(f'{sender}: {message}\n')

@app.route('/get', methods=['POST'])
def query():
    try:
        user_input = request.form["msg"]
        # save_message(user_input, sender="user")
        output = query_agent(user_input)
        # save_message(output, sender="bot")
        _ = get_audio(output)
        # audio_file = "question_audio.wav"

        
        # Return both text and audio file path
        return jsonify({
            "text": output,
            "audio_file": f"./static/question_audio.wav"  # Return relative path
        })
    except Exception as e:
        print(f"Error in query: {str(e)}")
        return jsonify({
            "text": "Sorry, there was an error processing your request.",
            "audio_path": None
        }), 500

    # threading.Thread(target=main, args=(output,)).start()  # updated
    # return jsonify({"text": output})

# @app.route('/speak', methods=['POST'])
# def speak():
#     data = request.json
#     text = data['text']
#     if text:
#         print(f"TTS request received: {text}")
#         threading.Thread(target=get_audio, args=(text,)).start()  # Call the TTS function
#     return jsonify({"message": "Audio generated"}), 200

@app.route('/stt', methods=['GET'])
def stt():
    transcription = record_audio()
    return jsonify({"text": transcription})

@app.route('/detect_wake_word', methods=['POST'])
def detect_wake_word():
    detected_wake_word = listen_for_wake_word()  # Use your actual detection logic
    if detected_wake_word == "hey robot":
        stt_text = record_audio()
        return jsonify(action="stt", transcription=stt_text)
    elif detected_wake_word == "yes i do":
        return jsonify(action="chatbot")
    elif detected_wake_word == "no i dont":
        #main("Let's move on.")
        return jsonify(action="next_exhibit", audio="lets_move_on")
    else:
        #main("Shall we move on?")
        #time.sleep(3)  # wait for 3 seconds
        return jsonify(action="next_exhibit", audio="shall_I_move_on")
    

if __name__ == '__main__':
    app.run(debug=True)