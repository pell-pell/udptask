import socket
import time
import sys
import numpy as np
from datetime import datetime

def udp_client(server_ip, server_port):
    # 创建UDP套接字
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 设置超时时间为100ms
    clientSocket.settimeout(0.1)

    nums = 12  # 总共发送12个请求包
    rcvd = 0  # 接收到的包计数
    rttList = []  # 存储RTT值的列表
    first = None  # 记录服务器第一次响应的时间戳
    last = None  # 记录服务器最后一次响应的时间戳
    total_time = None  # 总响应时间

    try:
        # 发送SYN建立连接
        connect_msg = "SYN"
        clientSocket.sendto(connect_msg.encode(), (server_ip, server_port))

        # 接收SYN-ACK并发送ACK
        response, server_addr = clientSocket.recvfrom(1024)
        if response.decode() == "SYN-ACK":
            print(f"连接建立，来自 {server_addr}")
            ack_msg = "ACK"
            clientSocket.sendto(ack_msg.encode(), server_addr)
        else:
            print("未收到SYN-ACK")
            return

        # 发送12个请求包
        for i in range(nums):
            seq_no = i + 1  # 序列号从1开始
            ver = 2  # 版本号为2
            others = "hfn%#d*&"  # 随机填充内容
            msg = f"{seq_no},{ver},{others}"
            tries = 0  # 重传计数

            while tries < 2:  # 最多重传2次
                try:
                    sendtime = time.perf_counter()  # 记录发送时间
                    clientSocket.sendto(msg.encode(), (server_ip, server_port))

                    response, server_addr = clientSocket.recvfrom(1024)
                    rcvtime = time.perf_counter()  # 记录接收时间
                    rtt = (rcvtime - sendtime) * 1000  # 计算RTT，单位为毫秒
                    rttList.append(rtt)

                    decoded = response.decode().split(',')
                    resp_seqno = decoded[0]
                    resp_time = decoded[2]
                    resp_time = datetime.strptime(resp_time, '%Y-%m-%d %H:%M:%S.%f')
                    resp_timestamp = resp_time.timestamp()

                    if first is None:
                        first = resp_timestamp
                    last = resp_timestamp

                    print(f"sequence no: {resp_seqno}, {server_ip}:{server_port}, rtt: {rtt:.2f} ms")
                    rcvd += 1
                    break
                except socket.timeout:
                    print(f"超时，重传第{tries + 1}次，SeqNo:{seq_no}")
                    tries += 1

            if tries == 2:
                print("两次重传失败，放弃重传")

        total_time = last - first  # 计算总响应时间

        # 计算和打印RTT统计信息
        if rttList:
            max_rtt = max(rttList)
            min_rtt = min(rttList)
            aver_rtt = np.mean(rttList)
            std_rtt = np.std(rttList)
        else:
            max_rtt = min_rtt = aver_rtt = std_rtt = 0

        loss_rate = (1 - (rcvd / nums)) * 100
        print(f"接收到的UDP数据包数量: {rcvd}")
        print(f"丢包率: {loss_rate:.2f}%")
        print(f"最大RTT: {max_rtt:.2f} ms")
        print(f"最小RTT: {min_rtt:.2f} ms")
        print(f"平均RTT: {aver_rtt:.2f} ms")
        print(f"RTT标准差: {std_rtt:.2f} ms")
        print(f"服务器总响应时间: {total_time:.2f} 秒")

        # 发送FIN请求释放连接
        disconnect_msg = "FIN"
        clientSocket.sendto(disconnect_msg.encode(), (server_ip, server_port))
        print("连接释放请求发送")

        response, server_addr = clientSocket.recvfrom(1024)
        print(f"连接释放确认收到，来自 {server_addr}")

        # 接收服务器的FIN请求
        response, server_addr = clientSocket.recvfrom(1024)
        if response.decode() == "FIN":
            print(f"接收到FIN请求，来自 {server_addr}")

            # 发送FIN-ACK确认
            fin_ack_msg = "FIN-ACK"
            clientSocket.sendto(fin_ack_msg.encode(), server_addr)
            print(f"发送FIN-ACK确认给 {server_addr}")

    finally:
        # 关闭套接字
        clientSocket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("请输入server_ip, server_port")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    udp_client(server_ip, server_port)    #192.168.242.132
