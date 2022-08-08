#!/usr/bin/env python3

# This script is supposed to be executed directly and NOT via the event-action command!

# Written by Benjamin Eggerstedt in 2022
# Developed during my free time, thus not official ALE code.

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

#
# Imports
#
import sys
try:
    import requests
except ImportError as ie:
    print(ie)
    # python3 -m pip install requests
    sys.exit("Please install python-requests!")
import json
try:
    import urllib3
except ImportError as ie:
    print(ie)
    # This comes as dependency of requests, so should always be there.
    # python3 -m pip install urllib3
    sys.exit("Please install urllib3!")  
import time

#
# Functions
#

def send_mail(email_from, email_to, language, smtp_server, smtp_auth, smtp_user, smtp_port, smtp_password, dspsk_to_remove):

    # Send an HTML email with an embedded image and a plain text message for
    # email clients that don't want to display the HTML.

    #from email.MIMEMultipart import MIMEMultipart
    #from email.MIMEText import MIMEText
    #from email.MIMEImage import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage

    # Define these once; use them twice!
    strFrom = email_from
    strTo = email_to

    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    if language == "de":
        msgRoot['Subject'] = f"{len(dspsk_to_remove)} abgelaufene DSPSK MAC {'Adresse' if len(dspsk_to_remove) == 1 else 'Adressen'} wurden gelöscht"
    else:
        msgRoot['Subject'] = f"{len(dspsk_to_remove)} expired DSPSK MAC {'address' if len(dspsk_to_remove) == 1 else 'addresses'} {'was' if len(dspsk_to_remove) == 1 else 'were'} removed"
    msgRoot['From'] = strFrom
    msgRoot['To'] = strTo
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    # Generate an UUID for uniqe attachment Content-IDs
    # Re-introduced for QR code functionality
    # content_id = uuid.uuid1().hex

    if language == "de":
        msgText = MIMEText(f"""
Hallo,
soeben {'wurde' if len(dspsk_to_remove) == 1 else 'wurden'} folgende DSPSK MAC {'Adresse' if len(dspsk_to_remove) == 1 else 'Adressen'} gelöscht:
{', '.join(str(mac) for mac in dspsk_to_remove) }

Bis bald!
Ihr ALE Stellar Wireless Team
        """)
    else:
        msgText = MIMEText(f"""
Hi,
the following DSPSK MAC {'address' if len(dspsk_to_remove) == 1 else 'addresses'} {'was' if len(dspsk_to_remove) == 1 else 'were'} just removed:
{', '.join(str(mac) for mac in dspsk_to_remove) }

Thanks,
Regards,
The ALE Stellar Wireless Team
        """)

    msgAlternative.attach(msgText)

    # Send the email
    import smtplib
    # Fix for issue # 2 - Python3 SMTP ValueError: server_hostname cannot be an empty string or start with a leading dot 
    smtp = smtplib.SMTP(host=smtp_server, port=smtp_port)
    smtp.set_debuglevel(0)
    smtp.connect(host=smtp_server, port=smtp_port)

    if smtp_auth == "yes":
        smtp.ehlo()
        smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        result = smtp.sendmail(strFrom, strTo, msgRoot.as_string())
    else:
        result = smtp.sendmail(strFrom, strTo, msgRoot.as_string())

if __name__ == "__main__":
    # Load settings from settings.json file
    print("[+] Reading settings.json file")
    try:
# Depending on the target platform to run/host this script you may need to modify this
#        with open("/flash/python/settings.json", "r") as json_data:
        with open("settings.json", "r") as json_data:
            settings = json.load(json_data)
            ov_hostname = settings["ov_hostname"]
            ov_username = settings["ov_username"]
            ov_password = settings["ov_password"]
            validate_https_certificate = settings["validate_https_certificate"]
            email_from = settings["email_from"]
            send_emails = settings["send_emails"]
            runs_on_omniswitch = settings["runs_on_omniswitch"]
            smtp_server = settings["smtp_server"]
            smtp_auth = settings["smtp_auth"]
            smtp_user = settings["smtp_user"]
            smtp_port = settings["smtp_port"]
            smtp_password = settings["smtp_password"]
            language = settings["language"]
            # Note that email_to will override to sys.argv[2] if given
            email_to = settings["email_to"]
    except IOError as ioe:
        print(ioe)
        sys.exit("ERROR: Couldn't find/open settings.json file!")
    except TypeError as te:
        print(te)
        sys.exit("ERROR: Couldn't read json format!")

    # Validate that setting.json is configured and not using the default
    if ov_hostname == "omnivista.example.com":
        sys.exit("ERROR: Can't work with default template value for OmniVista hostname!")

    # Validate that the hostname is a hostname, not URL
    if "https://" in ov_hostname:
        print("[!] Found \"https://\" in ov_hostname, removing it!")
        ov_hostname = ov_hostname.lstrip("https://")

    # Validate that the hostname doesn't contain a "/"
    if "/" in ov_hostname:
        print("[!] Found \"/\" in hostname, removing it!")
        ov_hostname = ov_hostname.strip("/")

    # Figure out if HTTPS certificates should be validated
    # That should actually be the default, so we'll warn if disabled.

    if(validate_https_certificate.lower() == "yes"):
        check_certs = True
    else:
        # This is needed to get rid of a warning coming from urllib3 on self-signed certificates
        print("[!] Ignoring certificate warnings or self-signed certificates!")
        print("[!] You should really fix this!")
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        check_certs = False    

    # We support to send the guest_account details via email to the account creator
    if len(sys.argv) == 2:
        print(f"[+] Updating email_to address to: {sys.argv[1]}")
        email_to = sys.argv[1]

    # Test connection to OmniVista
    print(f"[*] Attempting to connect to OmniVista server @ https://{ov_hostname}")

    req = requests.Session()

    # Use the ca-certificate store managed via Debian
    # This is just for development, should be commented out for production.
    #req.verify = "/etc/ssl/certs/"

    # Check if we die on the HTTPS certificate
    try:
        ov = req.get(f"https://{ov_hostname}", verify=check_certs)
    except requests.exceptions.SSLError as sslerror:
        print(sslerror)
        sys.exit("[!] Caught issues on certificate, try to change \"validate_https_certificate\" to \"no\" in settings.json. Exiting!")

    if ov.status_code == 200:
        print(f"[*] Connection to {ov_hostname} successful!")
    else:
        sys.exit(f"[!] Connection to {ov_hostname} failed, exiting!")

    ov_login_data = {"userName" : ov_username, "password" : ov_password}
    ov_header = {"Content-Type": "application/json"}

    # requests.post with json=payload was introduced in version 2.4.2
    # otherwise it would need to be "data=json.dumps(ov_login_data),"

    ov = req.post(f"https://{ov_hostname}/rest-api/login",
                headers=ov_header,
                json=ov_login_data,
                verify=check_certs)

    if ov.status_code == 200:
        ov_header["Authorization"] = f"Bearer {ov.json()['accessToken']}"
    else:
        sys.exit("[!] The connection to OmniVista was not successful! Exiting!")
    
    ov_dspsk_req = {"start":"", "querySize":1000}

    dspsk_resp = req.post(f"https://{ov_hostname}/api/ham/enterpriseProperty/getAllPageEnterprisePropertyInfo",
                headers=ov_header,
                json=ov_dspsk_req,
                verify=check_certs)
    
    # Java works in ms, thus we multiply our timestamp by 1000
    current_time = int(round(time.time())) * 1000

    if dspsk_resp.status_code == 200:
        dspsk_to_remove = []
        for dspsk in dspsk_resp.json()["data"]:
            if dspsk["pskValidityPeriod"] != None:
                if dspsk["pskValidityPeriod"] < current_time:
                    dspsk_to_remove.append(dspsk["deviceMac"])
                    print(f"[!] Found expired DSPSK for MAC ADDR: {dspsk['deviceMac']}")
    else:
        sys.exit(f"[!] Failed to get DSPSK accounts! Got {dspsk_resp.status_code, dspsk_resp.reason}! Exiting!")    

    if len(dspsk_to_remove) > 0:
        print(f"[*] Found {len(dspsk_to_remove)} to remove!")
        # This shouldn't need a loop, as OV-UPAM accepts this to be a list!
        ov_rem_resp = req.post(f"https://{ov_hostname}/api/ham/enterpriseProperty/deleteEnterpriseProperty",
                headers=ov_header,
                json=dspsk_to_remove,
                verify=check_certs)
        if ov_rem_resp.status_code == 200:
            if len(ov_rem_resp.json()["data"]) != len(dspsk_to_remove):
                print("[!] Mismatch on items to delete and deleted items!")
            for removed_mac in ov_rem_resp.json()["data"]:
                if (removed_mac["operation"] == "Delete" and removed_mac["status"] == True):
                    print(f"[-] Successfully removed DSPSK MAC ADDRESS {removed_mac['displayName']}!")
                else:
                    print(f"[!] Removing DSPSK MAC ADDRESS {removed_mac['displayName']} failed!")
    else:
        print("[!] No expired DSPSK entries!")

    # # Logout from API
    ov3 = req.get(f"https://{ov_hostname}/rest-api/logout", verify=check_certs)

    if len(dspsk_to_remove) > 0:
        if send_emails == "yes":
            send_mail(email_from, email_to, language, smtp_server, smtp_auth, smtp_user, smtp_port, smtp_password, dspsk_to_remove)
            print("[*] Sending email")