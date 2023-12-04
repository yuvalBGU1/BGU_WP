import socket

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server's IP address and port
server_address = ('127.0.0.1', 7777)
client_socket.connect(server_address)

try:
    while True:
        message = input("Enter a message (type 'exit' to quit): ")
        if message.lower() == 'exit':
            break  # Exit the loop if the user enters 'exit'
        # message = "hi there"
        for part in message.split(" "):
            # input()
            buffer = part.encode()
            buffer_len = len(buffer)
            client_socket.send(buffer_len.to_bytes(2, 'big'))
            client_socket.send(buffer)

except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Closing the client...")

# Close the connection
client_socket.close()
