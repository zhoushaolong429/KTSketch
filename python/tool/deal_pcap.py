from scapy.all import rdpcap

if __name__ == '__main__':
    # 读取pcap文件并返回一个packet列表
    packets = rdpcap('D:\\a_networktrace\\MAWI\\202204130000.pcap')
    WRITE = open("D:\\a_networktrace\\MAWI\\0.txt")
    # 遍历packet列表并解析每个数据包
    for idx, packet in enumerate(packets):
        # 在这里可以对每个数据包进行处理和解析，例如：
        # 获取源IP地址
        if idx % 10000 == 0:
            print(idx)
        try:
            src_ip = packet['IP'].src
            # 获取目的IP地址
            dst_ip = packet['IP'].dst
            line_ = str(src_ip) + " " + str(dst_ip) + '\n'
            WRITE.write(line_)
        except:
            continue
    WRITE.close()