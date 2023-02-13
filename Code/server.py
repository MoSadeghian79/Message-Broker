import socket
import threading
import time


PORT = 1373
ENCODING = "utf-8"
MESSAGE_LENGTH_SIZE = 128
connect_clients = {}
news = {}


def send_message(client, message):

    msg = message.encode(ENCODING)
    msg_lenght = str(len(msg)).encode(ENCODING)
    msg_lenght += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_lenght))
    client.send(msg_lenght)
    client.send(msg)

def main():

    address = socket.gethostbyname(socket.gethostname())
    Host_INFORMATION = (address, PORT)

    # Create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(Host_INFORMATION)

    print("[SERVER STARTS] Server is starting...")
    start(s)

def remove_client(clients):
    for client in clients:
        connect_clients.pop(client)
        client.close()



def ping_clients():
    global connect_clients
    remove = []
    for i in connect_clients:
        if connect_clients[i] != 0:
            print(i.getpeername())

    for i in connect_clients:
        if connect_clients[i] < 3:
            connect_clients[i] += 1
            ping(i)
        elif connect_clients[i] == 3:
            remove.append(i)
    remove_client(remove)
    
    time.sleep(10.0)
    ping_clients()


def ping(client):
    try:
        print("[Server Send Ping]")
        send_message(client, "ping")
    except:
        print("Connection Interuppted form sending pings!")
    

def start(server: socket):
    global connect_clients

    server.listen()
    threading.Thread(target= ping_clients).start()
    while True:
        conn, address = server.accept()
        t = threading.Thread(target= client_handeler, args = (conn, address))
        t.start()
        
        connect_clients[conn] = 0

def client_handeler(conn, address):
    global connect_clients

    
    with conn:
        print("[NEW CONNECTION] connected from {}".format(address))

        while True:
            try:
                massage_length = conn.recv(MESSAGE_LENGTH_SIZE)
                if not massage_length:
                    continue
                massage_length = int(massage_length.decode(ENCODING))
                msg = conn.recv(massage_length).decode(ENCODING)
                msg_data = msg.split("$")
            except:
                print("Connection Interuppted!")
            
            try: 
                if msg_data[0] == "publish":
                    publish(conn, msg_data[1], msg_data[2])
                elif msg_data[0] == "pong":
                    connect_clients[conn]  == 0
                elif msg_data[0] == "subscribe":
                    subscribe(conn, msg_data[1:])
            except:
                connect_clients.pop(conn)
                conn.close()
                print("Exception in Command from Client")

            #print("[MESSAGE RECEIVED] {}".format(msg))


def publish(client, topic, massage):
    send_message(client,"puback")
    news[topic] = massage


def subscribe(client, topics):
    accept_topics = ""
    for topic in topics:
        if topic in news:
            accept_topics = topic + "$"
    if len(accept_topics) != 0:
        send_message(client,"suback" + "$" + accept_topics[:-1])
    else:
        send_message(client,"suback" + "$" + "No Topics Find")

    for topic in topics:
        if topic in news:
            send_message(client,"sub_data" + "$" + str(topic) + "$" + news[topic])

if __name__ == "__main__":
    main()    

        



