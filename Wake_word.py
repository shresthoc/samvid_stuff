import pyaudio
import pvporcupine
import struct
import time

# Callback functions for each wake word
def wake_word_callback_yes():
    # print("Wake word 'Yes I do' detected!")
    return "yes i do"

def wake_word_callback_no():
    # print("Wake word 'No I don't' detected!")
    return "no i dont"

def wake_word_callback_hey_robot():
    return "hey robot"

# Function to listen for either "yes" or "no" wake words
def listen_for_wake_word(timeout=10):
    ACCESS_KEY = 'w2qE4ae60qLlol9zA4mCeThpW2yessF0e8ipcG6dR+rcVXZXMlR9eQ=='
    KEYWORD_FILE_PATH_YES = r"/Users/shresthochatterjee/Documents/Wake_word_detection/Yes-i-do_en_mac_v3_0_0/Yes-i-do_en_mac_v3_0_0.ppn"
    KEYWORD_FILE_PATH_NO = r"/Users/shresthochatterjee/Documents/Wake_word_detection/No-i-don--t_en_mac_v3_0_0/No-i-don--t_en_mac_v3_0_0.ppn"
    KEYWORD_FILE_PATH_HEY_ROBOT = r"/Users/shresthochatterjee/Documents/Wake_word_detection/Hey-robot_en_mac_v3_0_0/Hey-robot_en_mac_v3_0_0.ppn"
    
    # Initialize Porcupine with both "yes" and "no" wake words
    porcupine = pvporcupine.create(access_key=ACCESS_KEY, keyword_paths=[KEYWORD_FILE_PATH_YES, KEYWORD_FILE_PATH_NO, KEYWORD_FILE_PATH_HEY_ROBOT])

    # Initialize PyAudio for audio input
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    detected_word = None  # Flag to store detected word
    start_time = time.time()  # Start the timer

    try:
        # print("Listening for wake words 'Yes I do' or 'No I don't'...")
        while not detected_word:
            # Check if timeout is reached
            if time.time() - start_time > timeout:
                break
            
            # Read audio frame from microphone
            audio_frame = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, audio_frame)

            # Process audio frame to detect wake word
            keyword_index = porcupine.process(pcm)

            if keyword_index == 0:
                detected_word = wake_word_callback_yes()  # Detects "yes I do" wake word
            elif keyword_index == 1:
                detected_word = wake_word_callback_no()   # Detects "no I don't" wake word
            elif keyword_index == 2:
                detected_word = wake_word_callback_hey_robot()

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        # Clean up resources
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

    return detected_word  # Return the detected word or None if timeout was reached


# Main decision-making block
#print(listen_for_wake_word())

# if result == "yes I do":
#     print("Executing action x for 'Yes I do' wake word.")
#     # Perform action x here
# elif result == "no I don't":
#     print("Executing action y for 'No I don't' wake word.")
#     # Perform action y here
# else:
#     print("Executing action z for no wake word detected.")
#     # Perform action z here