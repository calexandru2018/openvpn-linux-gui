# openvpn-linux-gui [alpha v0.2.5] - [Closed]
A terminal GUI that improves the UX of ProtonVPN.

Actual Situation:
======
**NOTE:** Occasional bugs or issues may occur. Since the work is not packaged, you'll have to download it from github and (preferably) clone it into your /home/[user]/ folder. 

Requirments:
======
* **Python >= v3.5**

* **openvpn**

* **[update-resolv-conf](https://github.com/alfredopalhares/openvpn-update-resolv-conf)**

* **requests**
  
Setup:
======
**`You can either git clone it and install manually, or download the from releases and run it.`**

**Make sure that you have python >= v3.5  installed on your system.**

**If running single file:**

1. Open terminal in home folder (Make sure you clone it into your home folder, otherwise it won´t work at the moment)

2. `git clone https://github.com/calexandru2018/openvpn-linux-gui.git`

3. `cd openvpn-linux-gui/dist/`

4. Run the file.

**If installing manually:**

1. `git clone https://github.com/calexandru2018/openvpn-linux-gui.git`

2. `cd openvpn-linux-gui`

3. `pipenv install`

4. `python main.py`

Available Commands Explanation:
======
As of the moment, there are 14 commands you can give to the CLI:

Command | Explanation 
--- | ---
**[1] Check requirments** | Will check if you meet the requirments. Will return `True` or `False`. **Do not run the script** if you do not meet all requirments.
**[2] Create user** | This will initiliaze your account, by asking you for your VPN credentials, your vpn tier and your preferred protocol [udp/tcp]. These should be provided by your VPN service provider. They will be saved in the same folder as the project (within its own folder). The filetype is of type `.secret` for the credentials and for the tier and preferences is a `.json` type. 
**[3] Edit user** | This option allows you to edit either your credentials or tier and protocol. When **[8]**, the credentials will be copied into a folder within the /opt folder.
**[4] Connect to quickest by country** | Will connect to quickest server based on user specified country code; **AT**(Austria), **AU**: Australia, **BE**(Belgium), **BG**(Bulgaria), **BR**(Brazil), **CA**(Canada), **CH**(Switzerland), **CR**(Costa Rica), **CZ**(Czechia), **DE**(Germany), etc. **NOTE: It will generate the .ovpn for the fastest server from the user specified country, it also takes into consideration the users tier, so it will not connect to higher tier servers.**
**[5] OpenVPN Disconnect** | Disconnects from the vpn server. First attempts to find the PID of the OpenVPN server, then starts by restoring the original DNS configuration and lastly kills the OpenVPN process. 
**[6] Enable "start on boot" service** | This functions enables you to start the vpn server upon logging in into your account so you don't have to do it manually. It copies your credentials into a folder inside /opt/ (since openvpn can only access them from that folder, no user folders are accessible apparently). The user is prompted for the country that it wants the service to connect to upon login. **NOTE: I noticed that the DNS does not always change, so this might be needed to be done manually.**
**[7] Disable "start on boot" service** | Disables the previously mentoned service, so that next time the user boots into the desktop, the vpn server connection will **not** be established. 
**[8] Restart "start on boot" service** | Restarts as per **[6]** service. This may be handy when waking the computer from sleep/opening laptop lid.
**[9] Quick connect to quickest server** | Will connect user to the fastest server without user input for country specification. Takes into consideration and and excludes features such as **TOR** and **Secure Core** since these slow down connections **[UNDER WORK]**.
**[10] Connect to fastest P2P** | Will connect user to the fastest P2P server without user input for country specification. **[UNDER WORK]**.
**[11] Connect to fastest TOR** | Will connect user to the fastest TOR server without user input for country specification. **[UNDER WORK]**.
**[12] Connect to fastest Secure Core** | Will connect user to the fastest Secure Core server without user input for country specification. **[UNDER WORK]**.
**[13] Connect to last connected** | Will connect user to the last connected server. **[UNDER WORK]**.
**[14] Manage DNS (OVPN should fix it automatically)** | Manually modify the DNS. Does make a copy of the actual configuration located in `/etc/resolv.conf` and save a copy in the project folder. It then applies the custom DNS provided by ProtonVPN. It can also restore from backedup file.
**[15] Restart NetworkManager** | In case there are issues with connecting to the VPN, restores DNS. **NOTE: this will restore all your DNS settings and even possibly close your OpenVPN connection.**
**[16] Manage IPV6** | Restore or backup IPV6 configurations.
**[17] Check for VPN status** | Checks if VPN is running, will also look if a custom DNS was applied or not, if not a warning will be issued for DNS leakage. 


