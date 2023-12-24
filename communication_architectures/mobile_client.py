# Composing a 3 thread architecture,
# and 2 socket connection, input (for text to read) and output (for text to send)
# sending each word or sub sentence once completed,
# reading a word-by-word from queue.
# Using a server (satellite) to control the communication.
import threading


def input_from_queue():
    pass


def input_reader():
    pass


def output_cheetah():
    pass


def main():
    # Initialize the threads
    input_from_queue_thread = threading.Thread(target=input_from_queue)
    input_from_queue_thread.start()
    input_reader_thread = threading.Thread(target=input_reader)
    input_reader_thread.start()
    output_cheetah_thread = threading.Thread(target=output_cheetah)
    output_cheetah_thread.start()

    # Wait for the input thread to finish
    input_from_queue_thread.join()
    input_reader_thread.join()
    output_cheetah_thread.join()


if __name__ == '__main__':
    main()
