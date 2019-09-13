#!/bin/bash

METHOD="$1"
MAC="$2"

case "$METHOD" in
  auth_client)
    IOTA_MSG="$3"

    # Validate if the IOTA message passed by the user matches
    # the one obtained from the latest list of transactions (bundle)
    python /home/pi/IOTA-Hotspot/pyota/validator.py $IOTA_MSG
    IS_MSG_VALID=$(cat /tmp/is-msg-valid.out)

    # If the message is valid, then the client is authenticated
    if [ $IS_MSG_VALID == "1" ]; then
      # Allow client to access the Internet for one hour (3600 seconds)
      # Further values are upload and download limits in bytes. 0 for no limit.
      echo 3600 0 0
      # Run a client.py script in the background for each client
      # This script keeps track of data usage and deals with deauthentication
      nohup python /home/pi/IOTA-Hotspot/pyota/client.py &>/dev/null &
      exit 0
    else
      # Deny client to access the Internet.
      exit 1
    fi
    ;;
  client_auth|client_deauth|idle_deauth|timeout_deauth|ndsctl_auth|ndsctl_deauth|shutdown_deauth)
    INGOING_BYTES="$3"
    OUTGOING_BYTES="$4"
    SESSION_START="$5"
    SESSION_END="$6"
    # client_auth: Client authenticated via this script.
    # client_deauth: Client deauthenticated by the client via splash page.
    # idle_deauth: Client was deauthenticated because of inactivity.
    # timeout_deauth: Client was deauthenticated because the session timed out.
    # ndsctl_auth: Client was authenticated by the ndsctl tool.
    # ndsctl_deauth: Client was deauthenticated by the ndsctl tool.
    # shutdown_deauth: Client was deauthenticated by Nodogsplash terminating.
    ;;
esac

