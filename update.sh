#!/bin/bash
set -e

cd /home/pi/cable-tester

# Zorg dat de service niet actief draait tijdens update
systemctl stop cable-tester.service || true

# Repo bijwerken
git fetch --prune
git reset --hard origin/main

# Service opnieuw starten
systemctl start cable-tester.service