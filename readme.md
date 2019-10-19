# openvpn-linux-gui [alpha v0.1]
A GUI that improves the UX of OPENVPN (should ready by alpha v0.2) for such services as ProtonVPN.

Actual Situation:
======
**NOTE:** This is a work in progress, occasional bugs or issues may occur. Since the work is not packaged, you'll have to download it from github and (preferably) clone it into your /home/[user]/ folder. 

Requirments:
======
* **Python >= v3.5**

* **openvpn**

* **[update-resolv-conf](https://github.com/alfredopalhares/openvpn-update-resolv-conf)**

* **requests**

* **netifaces**
  
Setup:
======
**Make sure that you have python >= v3.5  installed on your system.**

`git clone https://github.com/calexandru2018/protonvpn-linux-gui.git`

`cd protonvpn-linux-gui`

either `python3 main.py` or `python main.py` depending on your version.

Available Commands Explanation:
======
As of the moment, there are 14 commands you can give to the CLI:

Command | Explanation 
--- | ---
**[1] Check requirments** | Will check if you meet the requirments. Will return `True` or `False`. **Do not run the script** if you do not meet all requirments.
**[2] Create user** | This will initiliaze your account, by asking you for your VPN credentials, your vpn tier and your preferred protocol [udp/tcp]. These should be provided by your VPN service provider. They will be saved in the same folder as the project (within its own folder). The filetype is of type `.secret` for the credentials and for the tier and preferences is a `.json` type. 
**[3] Edit user** | This option allows you to edit either your credentials or tier and protocol. When **[8]**, the credentials will be copied into a folder within the /opt folder.
**[4] Cache Servers** | This commands gets all the servers from ProtonVPN and caches them locally in its own folder, within the projects folder.
**[5] Generate OPVN file** | This command generates the neccessary .ovpn file, by queyring the ProtonVPN API, so that a connection can be made. User will get prompted for the country they want to be connected to, by specifying one of the following iso: **AT**(Austria), **AU**: Australia, **BE**(Belgium), **BG**(Bulgaria), **BR**(Brazil), **CA**(Canada), **CH**(Switzerland), **CR**(Costa Rica), **CZ**(Czechia), **DE**(Germany), etc. **NOTE: It will generate the .ovpn for the fastest server from the user specified country, it also takes into consideration the users tier, so it will not connect to lower tier.**
**[6] OpenVPN Connect** | Attempts to connect to the vpn server with the previously created .ovpn file and the hard-coded ProtonVPN's DNS. Prior to starting the process in the bakground, it makes a backup of the actual DNS and applies the custom one from ProtonVPN.
**[7] OpenVPN Disconnect** | Disconnects from the vpn server. First attempts to find the PID of the OpenVPN server, then starts by restoring the original DNS configuration and lastly kills the OpenVPN process. 
**[8] Enable "start on boot" service** | This functions enables you to start the vpn server upon logging in into your account so you don't have to do it manually. It copies your credentials into a folder inside /opt/ (since openvpn can only access them from that folder, no user folders are accessible apparently). The user is prompted for the country that it wants the service to connect to upon login. **NOTE: I noticed that the DNS does not always change, so this might be needed to be done manually.**
**[9] Disable "start on boot" service** | Disables the previously mentoned service, so that next time the user boots into the desktop, the vpn server connection will **not** be established. 
**[10] Modify DNS (OVPN should fix it automatically)** | Manually modify the DNS. Does make a copy of the actual configuration located in `/etc/resolv.conf` and save a copy in the project folder. It then applies the custom DNS provided by ProtonVPN.
**[11] Restore original DNS** | Restores back the original DNS.
**[12] Restart "start on boot" service** | Restarts the **[8]** service. This may be handy when waking the computer from sleep/opening laptop lid.
**[13] Restart NetworkManager** | If **[12]** does not work, this might help. **NOTE: this will restore all your DNS settings and even possibly close your OpenVPN connection.**
**[14] Manage IPV6[Work in progress]** | Mostly a test function to see if the script can enble/disable IPV6 and save its configurations.



