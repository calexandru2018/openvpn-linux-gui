# protonvpn-linux-gui [alpha v.1]
A GUI that improves the UX of ProtonVPN (should ready by alpha v2), developed by me.

## Actual situation:
Until the software reaches a solid CLI conversion based on ProtonVPN own CLI, the only way to interact with it will be through this version of CLI.

**NOTE:** This is a work in progress, occasional bugs or issues may occur. Since the work is not packaged, you'll have to download it from github and (preferably) clone it into your /home/[user]/ folder. 

Setup
======
`git clone https://github.com/calexandru2018/protonvpn-linux-gui.git`

`cd protonvpn-linux-gui`

either `python3 main.py` or `python main.py` depending on your version.

Available Commands Explanation
======
As of the moment, there are 14 commands you can give to the CLI:

Command | Explanation 
--- | ---
**[1] Check requirments** | Will check if you meed the requirments. Will return `True` or `False`. **Do not run the script** if you do not meet all requirments.
**[2] Create user** | This will initiliaze your account conf, by asking you for your VPN credentials, your vpn tier and your preferred protoco [udp/tcp]. These should be provided by your VPN service provider. They will get saved in the same folder as the project (within its own folder). The filetype is of type `.secret` for the credentials and for the tier and prefernces is a `.json` type. 
**[3] Edit user** | This option allows you to edit either your credentials or tier and protocol. When **[8]**, the credentials will be copied to a folder inside /opt folder.
**[4] Check requirments** | This commands gets all the servers from ProtonVPN and caches them locally in its own folder, inside the projects folder.
**[5] Check requirments** | This command generates the neccessary .ovpn file, by queyring the ProtonVPN API, so that a connection can be made. User will get prompted for the country they want to be connected to, by specifying one of the following iso: **AT**(Austria), **AU**: Australia, **BE**(Belgium), **BG**(Bulgaria), **BR**(Brazil), **CA**(Canada), **CH**(Switzerland), **CR**(Costa Rica), **CZ**(Czechia), **DE**(Germany), etc.
**[6] Check requirments** | Attempts to connect to the vpn server with the previously created .ovpn file and the hard-coded ProtonVPN's DNS. Prior to starting the process in the bakground, it makes a backup of the actual DNS and applies the custom one from ProtonVPN.
**[7] Check requirments** | Disconnects from the vpn server. First attempts to find the PID of the OpenVPN server, then starts by restoring the original DNS configuration and lastly kills the OpenVPN process. 
**[8] Check requirments** | This functions enables you to start the vpn server upon logging in into your account so you don't have to do it manually. It copies your credentials into a folder inside /opt/ (since openvpn can only access them from that folder, no user folders are accessible apparently). The user is prompted for the country that it wants the service to connect to upon login. **NOTE: I noticed that the DNS does not always change, so this might be needed to be done manually.**
**[9] Check requirments** | Disables the previously mentoned service, so that next time the user boots into the desktop, the vpn server connection will **not** be established. 
**[10] Check requirments** | Manually modify the DNS. Does make a copy of the actual configuration located in `/etc/resolv.conf` and save a copy in the project folder. It then applies the custom DNS provided by ProtonVPN.
**[11] Check requirments** | Restores back the original DNS.
**[12] Check requirments** | Restarts the **[8]** service. This may be handy when waking the computer from sleep/opening laptop lid.
**[13] Check requirments** | If **[12]** does not work, this might help. **NOTE: this will restore all your DNS settings and even possibly close your OpenVPN connection.**
**[14] Check requirments** | Mostly a test function to see if the script can enble/disable IPV6 and save its configurations.



