#!/bin/bash
set -e

cd /home/pi/cable-tester

/usr/bin/systemctl stop cable-tester.service || true

/usr/bin/git fetch --prune
/usr/bin/git reset --hard origin/main

/usr/bin/systemctl start cable-tester.service