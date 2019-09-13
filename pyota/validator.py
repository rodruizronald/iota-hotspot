# Imports of the PyOTA library
import sys, os
from iota import (
	__version__,
	Address,
	Iota
)

# Create an IOTA object
api = Iota('https://nodes.thetangle.org:443', '<TYPE_THE_IOTA_HOTSPOT_SEED_HERE>')
# IOTA hotspot addresses
iota_addr = Address(b'<TYPE_THE_IOTA_HOTSPOT_ADDRESS_HERE>')
# IOTA message received from the user transfer
iota_msg = ''
# Amount of data requested in MBytes
mbytes_requested = 0

# Get a list of bundles from the IOTA hotspot address
response = api.get_transfers()
bundles = response['bundles']
# Get a list of transactions from the most resent transfer (last bundle)
latest_bundle = bundles[len(bundles) - 1]
transactions = latest_bundle.transactions

# Decode the signature message framgment for each transation
for transaction in transactions:
	# Find the transation that contains the optional string message
	if transaction.value > 0:
		message = str(transaction.signature_message_fragment.decode())
		if message != '':
			value = transaction.value
			iota_msg = message
			# Convert from i to Mi tokens
			Mi = (value / 1000000)
			# 1 Mi equal to 5 MBytes
			mbytes_requested = (Mi * 5)

# Get the IOTA message entered from the splash.html (Passed from the wap_auth.sh)
usr_pwd = str(sys.argv[1])

# Read last iota message passed to the IOTA Hotspot
if os.path.exists('/tmp/last-iota-msg.out'):
	fp = open('/tmp/last-iota-msg.out','r')
	last_iota_msg = fp.readline().rstrip()
	fp.close()
else:
	last_iota_msg = iota_msg

# Check that the IOTA message entered by the user matches the one obtained
# from the transaction, and that the message is not repeated.
# The results from this validation are stored in temporary files '/tmp'
# that are later used in the wap_auth.sh and client.py
if usr_pwd == iota_msg and last_iota_msg != iota_msg:
	os.system('echo "1" > /tmp/is-msg-valid.out')
	output_msg = 'echo {} > /tmp/mbytes-requested.out'
	os.system(output_msg.format(25))
	output_msg = 'echo {} > /tmp/last-iota-msg.out'
	os.system(output_msg.format(iota_msg))
else:
	os.system('echo "0" > /tmp/is-msg-valid.out')

