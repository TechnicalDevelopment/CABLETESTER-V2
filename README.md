# CABLETESTER-V2


#-- het pullen van een nieuwe git repository versie --
cd /home/pi/cable-tester
git pull
sudo systemctl restart cable-tester.service

##-- installeren van github -- 
sudo apt update
sudo apt install -y git

##-- config menu
sudo raspi-config

##-- reboot pi
sudo reboot

##-- install driver screen 3,5 inch
sudo rm -rf LCD-show
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show
chmod -R 755 .
sudo ./MHS35-show

##-- frame buffer leeg maken (schermleeg maken)-- 
sudo killall fbi 2>/dev/null || true
sudo dd if=/dev/zero of=/dev/fb1 bs=1M count=8 2>/dev/null


#-- update van een git repository versie --
cd /home/pi/cable-tester
sudo systemctl stop cable-tester.service
git fetch --prune
git reset --hard origin/main
sudo systemctl start cable-tester.service
