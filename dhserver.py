from socket import *
import ipaddress

DHCP_SERVER = ('', 67)
DHCP_CLIENT = ('255.255.255.255', 68)
global_pool = {}
global_taken = {}

for i in range(2, 255):
    reserved_ip = ipaddress.ip_address(f'192.168.0.{i}')
    global_pool.add(reserved_ip)

# Create a UDP socket
s = socket(AF_INET, SOCK_DGRAM)

# Allow socket to broadcast messages
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

# Bind socket to the well-known port reserved for DHCP servers
s.bind(DHCP_SERVER)

# Receive a UDP message
msg, addr = s.recvfrom(1024)

# Print the client's MAC Address from the DHCP header
print("Client's MAC Address is " + format(msg[28], 'x'), end='')
mac_addr = ""


byte_data = msg[28:34]
string_mac = byte_data.hex()
mac_addr = ':'.join(string_mac[i:i+2] for i in range(0,12,2))

transaction_id = msg[4:8]


# Parse ip and what kind of request
option_code = ""
request = 0
ip = None
request_found = False
ip_found = False
lease_time = 0

location_ip = 0
location_op = 0


i = 240
while i < len(msg):
    option_code = msg[i]
    
    # what kind of request
    if option_code == 53:
        location_op = i
        request = msg[i+2]
        request_found = True
    
    # ip address
    if option_code == 50:
        location_ip = i
        ip = msg[i+2:i+6]
        ip_found = True

    if request_found and ip_found:
        break

    if option_code == 255:
        break

    if option_code == 0:
        i += 1
        continue
        
    # jumps to location of option code
    i += msg[i+1] + 2


if request == 1:
    DHCP_ip(mac_address)

   
print()


# Send a UDP message (Broadcast)
s.sendto(b'Hello World!', DHCP_CLIENT)
    
 

        

def DHCP_ip(full_addr):
    global global_pool
    global global_taken


    response = bytearray(msg)
    # op code = 2 (sending)
    response[0] = 2


    response[location_op + 2] = 2


    access_pool = list(global_pool)
    first_element = access_pool[0]
    global_pool.remove(first_element)
    global_taken.add(first_element)

    ip_parts = first_element.split('.')
    ip_bytes = bytes([int(ip_parts[0]), int(ip_parts[1]), int(ip_parts[2]), int(ip_parts[3])])
    
    response[16:20] = ip_bytes

    pos = 240

    while pos < len(response) and response[pos] != 255:
        if response[pos] == 0:
            pos += 1
        else:
            pos += 2 + response[pos + 1]


    new_options = bytearray()
    # server ip
    new_options.extend([54, 4, 192, 168, 0, 1])
    
    # lease time
    new_options.extend([51, 4, 0, 0, 0, 60])
 

    # subnet mask
    new_options.extend([1, 4, 255, 255, 255, 0])

    #router
    new_options.extend([3, 4, 192, 168, 0, 1])


    response = response[:pos] + new_options + response[pos:]


    s.sendto(response, addr)
