from pydoc import cli
import socket
import sys

ENCODING = "utf-8"
MESSAGE_LENGTH_SIZE = 128

def input():
    try:
        HOST_ADDR = sys.argv[1]
        PORT = sys.argv[2]
        command = sys.argv[3]
        command_data = sys.argv[4:]
        SERVER_INFORMATION = (HOST_ADDR, int(PORT))
        
        return SERVER_INFORMATION, command, command_data
        
    except:
        print("Please Try Again with Right Input!")
        quit()

def main():

    SERVER_INFORMATION, command, command_data = input()
    print(SERVER_INFORMATION)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(SERVER_INFORMATION)
    except:
        print("NO SERVER WITH THAT INFORMATION")
    
    if command == "publish":
        send_message(s, command + "$" + command_data[0] + "$" + command_data[1] )
    
    elif command == "subscribe":  
        topics = command_data[0]
        for i in range(1,len(command_data)):
            topics += "$"
            topics += command_data[i]

        send_message(s, command + "$" + topics)
    else:
        print("INVALID COMMAND")
        quit()
    try:
        receive(s)
    except:
        print("CONNECTION INTERRUPTED")

def receive(client):
    client.settimeout(10.0)
    while True:

        try:
            massage_length = client.recv(MESSAGE_LENGTH_SIZE)
            if not massage_length:
                continue
            client.settimeout(None)
            massage_length = int(massage_length.decode(ENCODING))
            msg = client.recv(massage_length).decode(ENCODING)
            msg_data = msg.split("$")
        except:
            print("Connection Interuppted!")
        
        if msg_data[0] == "puback":
            print("Successful Publiching!")
        elif msg_data[0] == "ping":
            print("[Client receive Ping]")
            send_message(client, "pong")
        elif msg_data[0] == "suback":
            topics = msg_data[1:]
            print("Successful Subcribing on " + " ".join(str(i) for i in topics))
        elif msg_data[0] == "sub_data":
            print(msg_data[1] + ": " + msg_data[2])
        else:
            print("Invalid data from server")
            print(msg_data)


def send_message(client, message):

    msg = message.encode(ENCODING)
    msg_lenght = str(len(msg)).encode(ENCODING)
    msg_lenght += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_lenght))
    client.send(msg_lenght)
    client.send(msg)


if __name__ == "__main__":
    main()