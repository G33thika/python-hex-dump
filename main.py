import socket 
import time
import sys
import netifaces
from ctypes import *
from struct import *


#getting ip address =======================================================================================================
#https://pythonguides.com/python-get-an-ip-address/  
dstaddr = sys.argv[1]
dstad = socket.gethostbyname(dstaddr)

#https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-from-nic-in-python
srcaddr = netifaces.ifaddresses('ens33')
srcad = srcaddr[netifaces.AF_INET][0]['addr']

ip_src = socket.inet_aton(srcad)
ip_dst = socket.inet_aton(dstad)


#ICMP pack =================================================================================================================
# https://gist.github.com/shawwwn/91cc8979e33e82af6d99ec34c38195fb
def checksum(data):
    if len(data) & 0x1: # Odd number of bytes
        data += b'\0'
    cs = 0
    for pos in range(0, len(data), 2):
        b1 = data[pos]
        b2 = data[pos + 1]
        cs += (b1 << 8) + b2
    while cs >= 0x10000:
        cs = (cs & 0xffff) + (cs >> 16)
    cs = ~cs & 0xffff
    return cs

i_type = 8
i_code = 0
i_check = 0
i_id = 5656
i_seq = 1

icmp_header = pack('!bbHHh', i_type, i_code, i_check, i_id, i_seq)
size = 32
data = b'Q'*size
get_checksum = checksum(icmp_header + data)
get_checksum = pack('H', socket.htons(get_checksum))
icmp_header = pack('!bb2sHh', i_type, i_code, get_checksum , i_id, i_seq)
packet = icmp_header + data


hops = 0 
ip_ttl= 1

while hops < 30:
    #send packet ====================================================================================
    #https://www.programcreek.com/python/example/116468/socket.IP_TTL
    s= socket.socket(socket.AF_INET,  socket.SOCK_RAW, socket.IPPROTO_ICMP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_IP, socket.IP_TTL, ip_ttl)
    s.sendto(packet,(dstad, 1))

    #unpack ip =======================================================================================
    class IP(Structure):
        _fields_ = [
            ("src", c_uint32),
            ("des", c_uint32)

        ]

        def __new__(self, socket_buffer=None):
            return self.from_buffer_copy(socket_buffer)

        def __init__(self, socket_buffer=None):
            
            self.src_addr = socket.inet_ntoa(pack("@I", self.src))
            self.dst_addr = socket.inet_ntoa(pack("@I", self.des))
            
    #unpack icmp =======================================================================================
    class ICMP(Structure):
        _fields_=[
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("chsum", c_ushort),
        ("id", c_ushort),
        ("seq", c_ushort)
        ]
        def __new__(self, socket_buffer=None):
            return self.from_buffer_copy(socket_buffer)

        def __init__(self, socket_buffer=None):
            pass
    #get recived packet =================================================================================
    try:
        recv_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_sock.bind(('ens33', 0))
        recv_data = recv_sock.recvfrom(65535)[0]
        icmp = ICMP(recv_data[34:])

        if icmp.type == 11:
            ip = IP(recv_data[26:])
            print(f"{ip_ttl} {ip.src_addr}")
            ip_ttl = ip_ttl + 1
        elif icmp.type == 0 and icmp.id == 6166:
            ip = IP(recv_data[26:])
            hostbyaddr = socket.gethostbyaddr(ip.src_addr)
            print(f"{ip_ttl} {ip.src_addr} {hostbyaddr[0]}")
            print("trace complete..")
            break
    except socket.herror:
        print(f"{ip_ttl} {ip.src_addr} Unknown host")
        print("trace complete..")
        break
    hops = hops + 1