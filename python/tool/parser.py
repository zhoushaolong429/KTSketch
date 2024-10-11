import dpkt
import socket
from dpkt.compat import compat_ord
pcap_file_name = "D:\\a_networktrace\\MAWI\\202204130000.pcap"
target_text_file_name = "D:\\a_networktrace\\MAWI\\00.txt"
def mac_addr(address):
    """Convert a MAC address to a readable/printable string

       Args:
           address (str): a MAC address in hex form (e.g. '\x01\x02\x03\x04\x05\x06')
       Returns:
           str: Printable/readable MAC address
    """
    return ':'.join('%02x' % compat_ord(b) for b in address)

def inet_to_str(inet):
    """Convert inet object to a string

        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)

if __name__ == '__main__':
    pcap_r = open(pcap_file_name, 'rb')
    target_file_source = open(target_text_file_name, 'w')
    pcap = dpkt.pcap.Reader(pcap_r)
    header = "src,dst\n"
    for idx, t in enumerate(pcap):
        if idx % 1000000 == 0:
            print(idx, " packets had been done!")
        try:
            buf = t[1]
            pkt = dpkt.ethernet.Ethernet(buf)
            # pkt = dpkt.ip.IP(buf)
            #print(mac_addr(pkt.src), mac_addr(pkt.dst))
            line_ = mac_addr(pkt.src) + " " + mac_addr(pkt.dst)+ "\n"
            target_file_source.write(line_)
        except:
            continue

    pcap_r.close()
    target_file_source.close()