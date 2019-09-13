from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import json, os, subprocess, sys, time, math

# Captive portal utilities - nodogsplash command line interface (ndsctl)
# Output from: sudo ndsctl clients
#
# 1 (Number of clients attached to the network)
#
# client_id=0
# ip=192.168.1.83
# mac=e4:f8:9c:1d:26:26
# added=0
# active=1568330427
# duration=0
# token=3dfda243
# state=Preauthenticated
# downloaded=0
# avg_down_speed=0.00
# uploaded=0
# avg_up_speed=0.00

# Get an array of clients connected to the IOTA Hotspot
def get_arr_clients():
	nds_clients = subprocess.Popen('sudo ndsctl clients', stdout=subprocess.PIPE, shell=True)
	arr_clients = nds_clients.stdout.read().splitlines()
	return arr_clients

# Get an specific element of the array (ip, mac, token...)
# from a given client (client_pos)
def get_arr_elem(arr_clients, client_pos, elem_pos):
	index = (client_pos * 13) + 2 + elem_pos
	element = arr_clients[index].split('=')
	return element[1]

# Deauthenticate a client from the network to prohibit it
# accessing the Internet (must be authenticated again)
def deauth_client(mac):
	cmd = 'sudo ndsctl deauth ' + str(mac)
	os.system(cmd)

# Default possition for each element in a client object
mac_addr_pos = 2
downloaded_pos = 8
uploaded_pos = 10

# Recover the MBytes requested by the user
fp = open('/tmp/mbytes-requested.out','r')
mbytes = int(fp.readline().rstrip())
fp.close()

# Calculate the IOTA tokens transfer by the user
tokens = (mbytes / 5)
# Conver the MBytes to Kbytes
kbytes_requested = (mbytes * 1000)

arr_clients = get_arr_clients()
# Get the current number of clients attached network
curr_num_clients = int(arr_clients[0])
# THIS client is the last element in the array
client_pos = curr_num_clients - 1
client_mac_addr = get_arr_elem(arr_clients, client_pos, mac_addr_pos)

while 1:
	arr_clients = get_arr_clients()
	num_of_clients = int(arr_clients[0])

	# In case some clients are removed from the network,
	# recalcualte the position of THIS client (client_pos)
	if num_of_clients < curr_num_clients:
		for cpos in range(num_of_clients):
			index = (cpos * 13) + 2 + mac_addr_pos
			mac_addr = arr_clients[index].split('=')
			if mac_addr[1] == client_mac_addr:
				client_pos = cpos
				break

	curr_num_clients = num_of_clients

	# Get the overall data consumed by the client
	downloaded = int(get_arr_elem(arr_clients, client_pos, downloaded_pos))
	uploaded = int(get_arr_elem(arr_clients, client_pos, uploaded_pos))
	kbytes_consumed = math.floor(downloaded + uploaded)

	# For demonstration purposes in the monitor.html page, the data
	# consumed and tokens left are stored in xml files
	# Only supported for one client, in this case the first one that joins
	# the network
	if client_pos == 0:
		# Calcualte mbytes and tokens left
		mbytes_consumed = math.floor(kbytes_consumed / 1000)
		tokens_left = tokens - math.floor(mbytes_consumed / 5)
		if tokens_left < 0:
			tokens_left = 0

		# Create the xml client file
		root = Element('root')
		child = SubElement(root, 'tokens')
		child.text = str(tokens_left)
		child = SubElement(root, 'mbytes')
		child.text = str(mbytes_consumed)

		# Overwrite the file
		file = open('/etc/nodogsplash/htdocs/xml/client.xml','w')
		file.write(tostring(root))
		file.close()

	# The client is remove from the network once it has
	# consumed all the data requested
	if kbytes_requested <= kbytes_consumed:
		deauth_client(client_mac_addr)
		sys.exit(0)

	# Sleep at least 10 sec to realese the processor and
	# let nodogsplash update the data consumption
	time.sleep(10)
