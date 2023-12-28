from multiprocessing import freeze_support
from RealtimeTTS import TextToAudioStream, CoquiEngine


# ----testing with client
def read_text_from_queue():
    global stream
    while True:
        stream.play()


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
    import socket
    import threading
    import torch

    print("is GPU available: " + str(torch.cuda.is_available()))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # for normal use with minimal logging:
    engine = CoquiEngine(voice="vocals/id1/tr02.wav")

    # test with extended logging:
    # import logging
    #
    # logging.basicConfig(level=logging.INFO)
    # engine = CoquiEngine(level=logging.INFO, voice="vocals/id1/tr01.wav", use_deepspeed=True, speed=2.0)

    global stream
    stream = TextToAudioStream(engine)

    freeze_support()
    main()
