
# BGP AS and ISP Tracing Code with inter ISP-HOP latency calculations
# Author:   Harris

## Imports
import socket, time, requests, json, csv

target = "fb.com"

def trace(target):
    d_ip = socket.gethostbyname(target)
    hops  = 15                          # Maximum number of hops to wait for
    ttl =  1                            # Increment TTL after loop iteration
    last_gap = 0
    while True:
        r_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, 1)       # Recieving Socket for ICMP Packets
        s_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 17)    # Sending Socket for UDP Packets
        s_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)             # Set socket options
        r_socket.bind(("", 33434))                                           # Bind to receiving on port 33434 on any interface
        s_socket.sendto(("").encode(),(d_ip, 33434))
        sent_time = time.time()                                             # Time at packet transmission
        try:
            hop_addr = None
            x, hop_addr = r_socket.recvfrom(512)                         # Socket received data and source address port tuple. Discard data (x), use source address port
            return_time = time.time()
            hop_addr = hop_addr[0]
        except socket.error:
            pass
        s_socket.close()
        r_socket.close()

        if hop_addr == None:
            hop_addr = "* * *"
        else:
            hop_addr = hop_addr

        source_time = round(((return_time - sent_time) * 1000),3)
        asn = as_info(hop_addr)
        hop_gap = hop_latency(source_time,last_gap)
        last_gap = source_time
        data_list = hop_addr,source_time,asn,hop_gap
        print(data_list)
        tracedata(data_list)
        print("HOP ADDRESS:  " + str(hop_addr))
        print("TIME FROM SOURCE:  " + str(source_time))
        print("AS Number:   "   + str(asn))
        print("HOP GAP TIME: "  + str(hop_gap))
        print("+++++++++++++++++++++++++++++++++++")
        ttl += 1

        if hop_addr == target or ttl > 15:
            print("Trace Complete / HOP Exceeded")
            break

def as_info(ip):
    as_url = 'http://ip-api.com/json/' + str(ip)
    as_response = requests.get(as_url)
    as_data = as_response.json()
    try:
        return (as_data['as'])
    except:
        return ("PRIVATE IP RANGE")
    #return as_data['as']

def hop_latency(time, last_gap):
    hop_gap =  time - last_gap
    return round(hop_gap,3)

def tracedata(data):
    with open(r'tracedata', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)


if __name__ == '__main__':
    while True:
        time.sleep(15)
        trace(target)
