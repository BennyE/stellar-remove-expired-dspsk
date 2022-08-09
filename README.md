# stellar-remove-expired-dspsk
A small helper script meant to run on an Alcatel-Lucent Enterprise OmniSwitch with AOS Release 8

# Usage
- git clone the respository
- Modify the **settings_template.json** and save it as **settings.json**
  - Note that some entries are not needed, but the settings.json shall largely stay compatible to my other scripts (this is probably in your interest ;))
- Follow instructions to deploy "requests" to OmniSwitch AOS R8 (Alcatel-Lucent Enterprise can help you via our Professional Service team)
- Create a CRON job for the script on OmniSwitch AOS R8 (This was tested on AOS 8.8R2 GA on OS6465T-P12)
  - Edit this file: **/flash/working/pkg/ams/cron.cfg**
  - The following entry would be executed every five minutes:
    - */5 * * * * /bin/python3 /flash/python/stellar-remove-expired-dspsk.py
  - The following entry would be executed every Wednesday at 06:00 in the morning:
    - 0 6 * * WED /bin/python3 /flash/python/stellar-remove-expired-dspsk.py
```
(admin@router) Password: 
 ________  ________  ________           ________  ________     
|\   __  \|\   __  \|\   ____\         |\   __  \|\   __  \    
\ \  \|\  \ \  \|\  \ \  \___|_        \ \  \|\  \ \  \|\  \   
 \ \   __  \ \  \\\  \ \_____  \        \ \   _  _\ \   __  \  
  \ \  \ \  \ \  \\\  \|____|\  \        \ \  \\  \\ \  \|\  \ 
   \ \__\ \__\ \_______\____\_\  \        \ \__\\ _\\ \_______\
    \|__|\|__|\|_______|\_________\        \|__|\|__|\|_______|
                       \|_________|                            
					       OmniSwitch 6465T
Router-> cat /flash/working/pkg/ams/cron.cfg 
0 6 * * WED /bin/python3 /flash/python/stellar-remove-expired-dspsk.py
Router-> show appmgr  
Legend: (+) indicates application is not saved across reboot
  Application    Status    Package Name        User                  Status Time Stamp
---------------+---------+-------------------+---------------------+---------------------
  cron-app      restarted ams                 admin                 Tue Aug  9 16:11:10 2022

Router-> appmgr restart ams cron-app
Please wait...

Router-> show appmgr                
Legend: (+) indicates application is not saved across reboot
  Application    Status    Package Name        User                  Status Time Stamp
---------------+---------+-------------------+---------------------+---------------------
+ cron-app      restarted ams                 admin                 Tue Aug  9 17:14:09 2022
Router-> write memory flash-synchro 

File /flash/working/vcsetup.cfg replaced.
Please wait...

File /flash/working/vcboot.cfg replaced.
```
