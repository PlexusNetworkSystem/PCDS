#!/bin/bash
echo "PID | $$"

# Run terminal.py and capture its PID
nohup python terminal.py > /dev/null 2>&1 &
TERMINAL_PID=$!

# Run host.py and capture its PID
nohup python host.py > /dev/null 2>&1 &
HOST_PID=$!

# Run fileexplorer.py and capture its PID
nohup python fileexplorer.py > /dev/null 2>&1 &
FM_PID=$!

echo "Terminal PID: $TERMINAL_PID"
echo "Host PID: $HOST_PID"
echo "Fileexplorer PID: $FM_PID"

read -n 1 -s -r -p "Press any key to exit..."
kill $TERMINAL_PID
kill $HOST_PID
kill $FM_PID

echo "Exiting..."
exit 0
