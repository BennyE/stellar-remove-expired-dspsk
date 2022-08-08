# stellar-remove-expired-dspsk
A smaller helper script meant to run on an Alcatel-Lucent Enterprise OmniSwitch with AOS Release 8

# Usage
- git clone the respository
- Modify the **settings_template.json** and save it as **settings.json**
  - Note that some entries are not needed, but the settings.json shall largely stay compatible to my other scripts (this is probably in your interest ;))
- Follow instructions to deploy "requests" to OmniSwitch AOS R8
- Create a CRON job for the script on OmniSwitch AOS R8
