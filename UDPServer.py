import socket
import random
from datetime import datetime

def udp_server(host='0.0.0.0', port=12345, loss_rate=0.3):
    # 创建UDP套接字
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定套接字到指定地址和端口
    serverSocket.bind((host, port))
    print(f"UDP服务器正在监听 {host}:{port}")

    try:
        while True:
            # 接收来自客户端的消息
            message, client_address = serverSocket.recvfrom(1024)

            # 如果收到的是"SYN"消息，表示客户端请求建立连接
            if message.decode() == "SYN":
                response = "SYN-ACK"
                serverSocket.sendto(response.encode(), client_address)
                print(f"SYN-ACK发送给 {client_address}")

                # 等待客户端的ACK确认
                ack_message, client_address = serverSocket.recvfrom(1024)
                if ack_message.decode() == "ACK":
                    print(f"接收到ACK，来自 {client_address}")
                else:
                    print("未收到ACK，连接终止")
                    continue

                continue

            # 解析客户端发送的消息
            decoded_message = message.decode().split(',')
            seq_no = decoded_message[0]

            # 如果收到的是"FIN"消息，表示客户端请求释放连接
            if decoded_message[-1] == "FIN":
                response = "FIN-ACK"
                serverSocket.sendto(response.encode(), client_address)
                print(f"连接释放确认发送给 {client_address}")

                # 发送FIN请求给客户端
                disconnect_msg = "FIN"
                serverSocket.sendto(disconnect_msg.encode(), client_address)
                print(f"发送FIN请求给 {client_address}")

                # 接收FIN-ACK确认
                response, client_address = serverSocket.recvfrom(1024)
                if response.decode() == "FIN-ACK":
                    print(f"接收到FIN-ACK确认，来自 {client_address}")
                break

            # 模拟丢包，如果随机值大于丢包率，发送响应
            if random.random() > loss_rate:
                current_time = datetime.now()
                response = f"{seq_no},2,{current_time.strftime('%Y-%m-%d %H:%M:%S.%f')}"
                serverSocket.sendto(response.encode(), client_address)
                print(f"回复客户端 {client_address}")
            else:
                print(f"模拟丢包 {client_address}")
    except KeyboardInterrupt:
        pass
    finally:
        # 关闭套接字
        serverSocket.close()

if __name__ == "__main__":
    udp_server()
