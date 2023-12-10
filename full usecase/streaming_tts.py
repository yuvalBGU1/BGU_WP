import socket
import threading
import time

from RealtimeTTS import TextToAudioStream, SystemEngine, AzureEngine, ElevenlabsEngine

global stream
engine = SystemEngine() # replace with your TTS engine
stream = TextToAudioStream(engine)
# stream.feed("Hello world! How are you today?")
# stream.play_async()

# stream.feed("Hello, this is a sentence.")


# def write(prompt: str):
#     for chunk in openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content" : prompt}],
#         stream=True
#     ):
#         if (text_chunk := chunk["choices"][0]["delta"].get("content")) is not None:
#             yield text_chunk


# text_stream = write("A three-sentence relaxing speech.")

# stream.feed(text_stream)

# char_iterator = iter("Streaming this character by character.")
# stream.feed(char_iterator)
#
# stream.play()
# print("sleeping...")
# time.sleep(15)

# ----testing with client
def read_text_from_queue():
    global stream
    while True:
        stream.play(buffer_threshold_seconds=5)



def push_text_from_client_to_queue():
    """
        Initiating the reciving server.
        Creating a socket connection with the client
    """
    global stream
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_address = ('127.0.0.1', 7777)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)

    print("Waiting for a connection...")

    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print("Connected to:", client_address)

    while True:
        data_len_buffer = client_socket.recv(2)
        if data_len_buffer:
            data_len = int.from_bytes(data_len_buffer, 'big')
            data = client_socket.recv(data_len).decode()
            if not data:
                continue
            stream.feed(data)
            print("feed: " + data)


def main():
    # Start the input thread
    input_thread = threading.Thread(target=push_text_from_client_to_queue)
    input_thread.start()

    # Start the read thread
    read_thread = threading.Thread(target=read_text_from_queue)
    read_thread.start()

    # Wait for the input thread to finish
    input_thread.join()
    read_thread.join()


if __name__ == '__main__':
    main()
