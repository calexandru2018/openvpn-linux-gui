function get_home() {
  if [[ -z "$SUDO_USER" ]]; then
    CURRENT_USER="$(whoami)"
  else
    CURRENT_USER="$SUDO_USER"
  fi
  USER_HOME=$(getent passwd "$CURRENT_USER" 2> /dev/null | cut -d: -f6)
  if [[ -z "$USER_HOME" ]]; then
    USER_HOME="$HOME"
  fi
  echo "$USER_HOME"
}

function sha512sum_func() {
  if [[ -n $(which sha512sum) ]]; then
    sha512sum_tool="$(which sha512sum)"
  elif [[ -n $(which shasum) ]]; then
    sha512sum_tool="$(which shasum) -a 512 "
  fi
  export sha512sum_tool
}

function get_protonvpn_cli_home() {
  echo "$(get_home)/.protonvpn-cli"
}

function check_if_openvpn_is_currently_running() {
  if [[ $(is_openvpn_currently_running) == true ]]; then
    echo "[!] Error: OpenVPN is already running on this machine."
    exit 1
  fi
}

function check_if_profile_initialized() {
  _=$(cat "$(get_protonvpn_cli_home)/protonvpn_openvpn_credentials" "$(get_protonvpn_cli_home)/protonvpn_tier" &> /dev/null)
  if [[ $? != 0 ]]; then
    echo "[!] Profile is not initialized."
    echo -e "Initialize your profile using: \n    $(basename $0) --init"
    exit 1
  fi
}

function is_internet_working_normally() {
  if [[ "$(check_ip)" != "Error." ]]; then
    echo true
  else
    echo false
  fi
}

function check_if_internet_is_working_normally() {
  if [[ "$(is_internet_working_normally)" == false ]]; then
    echo "[!] Error: There is an internet connection issue."
    exit 1
  fi
}

function is_openvpn_currently_running() {
  if [[ $(pgrep openvpn) == "" ]]; then
    echo false
  else
    echo true
  fi
}

function install_update_resolv_conf() {
  if [[ ("$UID" != 0) ]]; then
    echo "[!] Error: Installation requires root access."
    exit 1
  fi
  echo "[*] Installing update-resolv-conf..."
  mkdir -p "/etc/openvpn/"
  file_sha512sum="81cf5ed20ec2a2f47f970bb0185fffb3e719181240f2ca3187dbee1f4d102ce63ab048ffee9daa6b68c96ac59d1d86ad4de2b1cfaf77f1b1f1918d143e96a588"
  wget "https://raw.githubusercontent.com/ProtonVPN/scripts/master/update-resolv-conf.sh" -O "/etc/openvpn/update-resolv-conf"
  if [[ ($? == 0) && ($($sha512sum_tool "/etc/openvpn/update-resolv-conf" | cut -d " " -f1) == "$file_sha512sum")  ]]; then
    chmod +x "/etc/openvpn/update-resolv-conf"
    echo "[*] Done."
  else
    echo "[!] Error installing update-resolv-conf."
    rm -f "/etc/openvpn/update-resolv-conf" 2> /dev/null
    exit 1
  fi
}

function check_ip() {
  counter=0
  ip=""
  while [[ "$ip" == "" ]]; do
    if [[ $counter -lt 3 ]]; then
      ip=$(wget --header 'x-pm-appversion: Other' \
                --header 'x-pm-apiversion: 3' \
                --header 'Accept: application/vnd.protonmail.v1+json' \
                -o /dev/null \
                --timeout 6 --tries 1 -q -O - 'https://api.protonmail.ch/vpn/location' \
                | $python -c 'import json; _ = open("/dev/stdin", "r").read(); print(json.loads(_)["IP"])' 2> /dev/null)
      counter=$((counter+1))
    else
      ip="Error."
    fi
    if [[ -z "$ip" ]]; then
      sleep 2  # Sleep for 2 seconds before retrying.
    fi
  done
  echo "$ip"
}

function init_cli() {
  if [[ -f "$(get_protonvpn_cli_home)/protonvpn_openvpn_credentials" ]]; then
    echo -n "[!] User profile for protonvpn-cli has already been initialized. Would you like to start over with a fresh configuration? [Y/n]: "
    read "reset_profile"
  fi
  if  [[ ("$reset_profile" == "n" || "$reset_profile" == "N") ]]; then
     echo "[*] Profile initialization canceled."
     exit 0
  fi

  rm -rf "$(get_protonvpn_cli_home)/"  # Previous profile will be removed/overwritten, if any.
  mkdir -p "$(get_protonvpn_cli_home)/"

  create_vi_bindings

  read -p "Enter OpenVPN username: " "openvpn_username"
  read -s -p "Enter OpenVPN password: " "openvpn_password"
  echo -e "$openvpn_username\n$openvpn_password" > "$(get_protonvpn_cli_home)/protonvpn_openvpn_credentials"
  chown "$USER:$(id -gn $USER)" "$(get_protonvpn_cli_home)/protonvpn_openvpn_credentials"
  chmod 0400 "$(get_protonvpn_cli_home)/protonvpn_openvpn_credentials"

  echo -e "\n[.] ProtonVPN Plans:\n1) Free\n2) Basic\n3) Plus\n4) Visionary"
  protonvpn_tier=""
  available_plans=(1 2 3 4)
  while [[ $protonvpn_tier == "" ]]; do
    read -p "Enter Your ProtonVPN plan ID: " "protonvpn_plan"
    case "${available_plans[@]}" in  *"$protonvpn_plan"*)
      protonvpn_tier=$((protonvpn_plan-1))
      ;;
    4)
      protonvpn_tier=$((protonvpn_tier-1)) # Visionary gives access to the same VPNs as Plus.
      ;;
    *)
      echo "Invalid input."
    ;; esac
  done
  echo -e "$protonvpn_tier" > "$(get_protonvpn_cli_home)/protonvpn_tier"
  chown "$USER:$(id -gn $USER)" "$(get_protonvpn_cli_home)/protonvpn_tier"
  chmod 0400 "$(get_protonvpn_cli_home)/protonvpn_tier"

  read -p "[.] Would you like to use a custom DNS server? (Warning: This would make your VPN connection vulnerable to DNS leaks. Only use it when you know what you're doing) [y/N]: " "use_custom_dns"

  if  [[ ("$use_custom_dns" == "y" || "$use_custom_dns" == "Y") ]]; then
     custom_dns=""
     while [[ $custom_dns == "" ]]; do
       read -p "Custom DNS Server: " "custom_dns"
     done
     echo -e "$custom_dns" > "$(get_protonvpn_cli_home)/.custom_dns"
     chown "$USER:$(id -gn $USER)" "$(get_protonvpn_cli_home)/.custom_dns"
     chmod 0400 "$(get_protonvpn_cli_home)/.custom_dns"
  fi

  read -p "[.] [Security] Decrease OpenVPN privileges? [Y/n]: " "decrease_openvpn_privileges"
  if [[ "$decrease_openvpn_privileges" == "y" || "$decrease_openvpn_privileges" == "Y" ||  "$decrease_openvpn_privileges" == "" ]]; then
    echo "$decrease_openvpn_privileges" > "$(get_protonvpn_cli_home)/.decrease_openvpn_privileges"
  fi

  # Disabling killswitch prompt
  #read -p "[.] Enable Killswitch? [Y/n]: " "enable_killswitch"
  #if [[ "$enable_killswitch" == "y" || "$enable_killswitch" == "Y" || "$enable_killswitch" == "" ]]; then
  #  echo > "$(get_protonvpn_cli_home)/.enable_killswitch"
  #fi

  config_cache_path="$(get_protonvpn_cli_home)/openvpn_cache/"
  rm -rf "$config_cache_path"
  mkdir -p "$config_cache_path"  # Folder for openvpn config cache.

  chown -R "$USER:$(id -gn $USER)" "$(get_protonvpn_cli_home)/"
  chmod -R 0400 "$(get_protonvpn_cli_home)/"

  echo "[*] Done."
}

function manage_ipv6() {
  # ProtonVPN support for IPv6 coming soon.
  errors_counter=0
  if [[ ("$1" == "disable") && ( $(detect_platform_type) != "macos" ) ]]; then
    if [ -n "$(ip -6 a 2> /dev/null)" ]; then

      # Save linklocal address and disable IPv6.
      ip -6 a | awk '/^[0-9]/ {DEV=$2}/inet6 fe80/ {print substr(DEV,1,length(DEV)-1) " " $2}' > "$(get_protonvpn_cli_home)/.ipv6_address"
      if [[ $? != 0 ]]; then errors_counter=$((errors_counter+1)); fi

      sysctl -w net.ipv6.conf.all.disable_ipv6=1 &> /dev/null
      if [[ $? != 0 ]]; then errors_counter=$((errors_counter+1)); fi

      sysctl -w net.ipv6.conf.default.disable_ipv6=1 &> /dev/null
      if [[ $? != 0 ]]; then errors_counter=$((errors_counter+1)); fi

    fi
  fi

  # Disable IPv6 in macOS.
  if [[ ("$1" == "disable") &&  ( $(detect_platform_type) == "macos" ) ]]; then
    # Get list of services and remove the first line which contains a heading.
    ipv6_services="$( networksetup  -listallnetworkservices | sed -e '1,1d')"

    # Go through the list disabling IPv6 for enabled services, and outputting lines with the names of the services.
    echo %s "$ipv6_services" | \

    while read ipv6_service ; do
      # If first character of a line is an asterisk, the service is disabled, so we skip it.
      if [[ "${ipv6_service:0:1}" != "*" ]] ; then
        ipv6_status="$( networksetup -getinfo "$ipv6_service" | grep 'IPv6: ' | sed -e 's/IPv6: //')"
        if [[ "$ipv6_status" = "Automatic" ]] ; then
          networksetup -setv6off "$ipv6_service"
          echo "$ipv6_service" >> "$(get_protonvpn_cli_home)/.ipv6_services"
        fi
      fi
    done

  fi

  if [[ ("$1" == "enable") && ( ! -f "$(get_protonvpn_cli_home)/.ipv6_address" ) && ( $(detect_platform_type) != "macos" ) ]]; then
    echo "[!] This is an error in enabling IPv6 on the machine. Please enable it manually."
  fi

  if [[ ("$1" == "enable") && ( -f "$(get_protonvpn_cli_home)/.ipv6_address" ) && ( $(detect_platform_type) != "macos" ) ]]; then
    sysctl -w net.ipv6.conf.all.disable_ipv6=0 &> /dev/null
    if [[ $? != 0 ]]; then errors_counter=$((errors_counter+1)); fi

    sysctl -w net.ipv6.conf.default.disable_ipv6=0 &> /dev/null
    if [[ $? != 0 ]]; then errors_counter=$((errors_counter+1)); fi

    # Restore linklocal on default interface.
    while read -r DEV ADDR; do
      ip addr add "$ADDR" dev "$DEV"  &> /dev/null
      if [[ ($? != 0) && ($? != 2) ]]; then errors_counter=$((errors_counter+1)) ; fi
    done < "$(get_protonvpn_cli_home)/.ipv6_address"

    rm -f "$(get_protonvpn_cli_home)/.ipv6_address"
  fi

  if [[ ("$1" == "enable") && ( ! -f "$(get_protonvpn_cli_home)/.ipv6_services" ) && ( $(detect_platform_type) == "macos" ) ]]; then
    echo "[!] This is an error in enabling IPv6 on the machine. Please enable it manually."
  fi

  # Restore IPv6 in macOS.
  if [[ ("$1" == "enable") && ( -f "$(get_protonvpn_cli_home)/.ipv6_services" ) && ( $(detect_platform_type) == "macos" ) ]]; then
    if [[ $(< "$(get_protonvpn_cli_home)/.ipv6_services") == "" ]] ; then
      return
    fi

    ipv6_service=$(< "$(get_protonvpn_cli_home)/.ipv6_services")

    while read ipv6_service ; do
      networksetup -setv6automatic "$ipv6_service"
    done < "$(get_protonvpn_cli_home)/.ipv6_services"

    rm -f "$(get_protonvpn_cli_home)/.ipv6_services"
  fi

  if [[ $errors_counter != 0 ]]; then
    echo "[!] There are issues in managing IPv6 in the system. Please test the system for the root cause."
    echo "Not being able to manage IPv6 by protonvpn-cli may leak the system's IPv6 address."
  fi
}

function modify_dns() {
  # Backup DNS entries.
  if [[ ("$1" == "backup") ]]; then
    if [[  ( $(detect_platform_type) == "macos" ) ]]; then
      networksetup listallnetworkservices | tail +2 | while read interface; do
        networksetup -getdnsservers "$interface" > "$(get_protonvpn_cli_home)/$(sanitize_interface_name "$interface").dns_backup"
      done
    else # non-Mac
      cp "/etc/resolv.conf" "$(get_protonvpn_cli_home)/.resolv.conf.protonvpn_backup"
    fi
  fi

  # Apply ProtonVPN DNS.
  if [[ ("$1" == "to_protonvpn_dns") ]]; then
      connection_logs="$(get_protonvpn_cli_home)/connection_logs"
      dns_server=$(grep 'dhcp-option DNS' "$connection_logs" | head -n 1 | awk -F 'dhcp-option DNS ' '{print $2}' | cut -d ',' -f1) # ProtonVPN internal DNS.

    if [[ ( $(detect_platform_type) == "macos" ) ]]; then
      networksetup listallnetworkservices | tail +2 | while read interface; do
        networksetup -setdnsservers "$interface" $dns_server
      done
    else # non-Mac
      echo -e "# ProtonVPN DNS - protonvpn-cli\nnameserver $dns_server" > "/etc/resolv.conf"
    fi
  fi

  # Apply Custom DNS.
  if [[ ("$1" == "to_custom_dns") ]]; then
      custom_dns="$(get_protonvpn_cli_home)/.custom_dns"
      dns_server=$(< "$custom_dns")

    if [[ ( $(detect_platform_type) == "macos" ) ]]; then
      networksetup listallnetworkservices | tail +2 | while read interface; do
        networksetup -setdnsservers "$interface" $dns_server
      done
    else # non-Mac
      echo -e "# ProtonVPN DNS - Custom DNS\nnameserver $dns_server" > "/etc/resolv.conf"
    fi
  fi

  # Restore backed-up DNS entries.
  if [[ "$1" == "revert_to_backup" ]]; then
    if [[  ( $(detect_platform_type) == "macos" )  ]]; then
      networksetup listallnetworkservices | tail +2 | while read interface; do
        file="$(get_protonvpn_cli_home)/$(sanitize_interface_name "$interface").dns_backup"
        if [[ -f "$file" ]]; then
          if grep -q "There aren't any DNS Servers set" "$file"; then
            networksetup -setdnsservers "$interface" empty
          else
            networksetup -setdnsservers "$interface" "$(< "$file")"
          fi
        fi
      done
    else # non-Mac
      cp "$(get_protonvpn_cli_home)/.resolv.conf.protonvpn_backup" "/etc/resolv.conf"
    fi
  fi
}

function openvpn_disconnect() {
  max_checks=3
  counter=0
  disconnected=false

  if [[ "$1" != "quiet" ]]; then
    echo "Disconnecting..."
  fi

  if [[ $(is_openvpn_currently_running) == true ]]; then
    manage_ipv6 enable # Enabling IPv6 on machine.
  fi

  while [[ $counter -lt $max_checks ]]; do
      pkill -f openvpn
      sleep 0.50
      if [[ $(is_openvpn_currently_running) == false ]]; then
        modify_dns revert_to_backup # Reverting to original DNS entries
        disconnected=true
        # killswitch disable # Disabling killswitch
        cp "$(get_protonvpn_cli_home)/.connection_config_id" "$(get_protonvpn_cli_home)/.previous_connection_config_id" 2> /dev/null
        cp "$(get_protonvpn_cli_home)/.connection_selected_protocol" "$(get_protonvpn_cli_home)/.previous_connection_selected_protocol" 2> /dev/null
        rm -f  "$(get_protonvpn_cli_home)/.connection_config_id" "$(get_protonvpn_cli_home)/.connection_selected_protocol" 2> /dev/null

        if [[ "$1" != "quiet" ]]; then
          echo "[#] Disconnected."
          echo "[#] Current IP: $(check_ip)"
        fi

        if [[ "$2" != "dont_exit" ]]; then
          exit 0
        else
          break
        fi
      fi
    counter=$((counter+1))
  done

  if [[ "$disconnected" == false ]]; then
    if [[ "$1" != "quiet" ]]; then
      echo "[!] Error disconnecting OpenVPN."

      if [[ "$2" != "dont_exit" ]]; then
        exit 1
      fi

    fi
  fi
}

function update_cli() {
  check_if_internet_is_working_normally

  cli_path="/usr/local/bin/protonvpn-cli"
  if [[ ! -f "$cli_path" ]]; then
    echo "[!] Error: protonvpn-cli does not seem to be installed."
    exit 1
  fi
  echo "[#] Checking for update..."
  current_local_hashsum=$($sha512sum_tool "$cli_path" | cut -d " " -f1)
  remote_=$(wget --timeout 6 -o /dev/null -q -O - 'https://raw.githubusercontent.com/ProtonVPN/protonvpn-cli/master/protonvpn-cli.sh')
  if [[ $? != 0 ]]; then
    echo "[!] Error: There is an error updating protonvpn-cli."
    exit 1
  fi
  remote_hashsum=$(echo "$remote_" | $sha512sum_tool | cut -d ' ' -f1)

  if [[ "$current_local_hashsum" == "$remote_hashsum" ]]; then
    echo "[*] protonvpn-cli is up-to-date!"
    exit 0
  else
    echo "[#] A new update is available."
    echo "[#] Updating..."
    wget -q --timeout 20 -O "$cli_path" 'https://raw.githubusercontent.com/ProtonVPN/protonvpn-cli/master/protonvpn-cli.sh'
    if [[ $? == 0 ]]; then
      echo "[#] protonvpn-cli has been updated successfully."
      exit 0
    else
      echo "[!] Error: There is an error updating protonvpn-cli."
      exit 1
    fi
  fi
}


function openvpn_connect() {
  check_if_openvpn_is_currently_running

  modify_dns backup # Backing-up current DNS entries.
  manage_ipv6 disable # Disabling IPv6 on machine.
  # killswitch backup_rules # Backing-up firewall rules.
  
  #this variable stores the server ID
  config_id=$1
  selected_protocol=$2
  if [[ -z "$selected_protocol" ]]; then
    selected_protocol="udp"  # Default protocol
  fi

  current_ip="$(check_ip)"
  connection_logs="$(get_protonvpn_cli_home)/connection_logs"
  openvpn_config="$(get_protonvpn_cli_home)/protonvpn_openvpn_config.conf"

  rm -f "$connection_logs"  # Remove previous connection logs.
  rm -f "$openvpn_config" # Remove previous openvpn config.

  config_cache_path="$(get_protonvpn_cli_home)/openvpn_cache/"
  mkdir -p "$config_cache_path"  # Folder for openvpn config cache.

  if [[ "$PROTONVPN_CLI_LOG" == "true" ]]; then  # PROTONVPN_CLI_LOG is retrieved from env.
    # This option only prints the path of connection_logs to end-user.
    echo "[*] CLI logging mode enabled."
    echo -e "[*] Logs path: $connection_logs"
  fi

  # Set PROTONVPN_CLI_DAEMON=false to disable daemonization of openvpn.
  PROTONVPN_CLI_DAEMON=${PROTONVPN_CLI_DAEMON:=true}

  wget \
    --header 'x-pm-appversion: Other' \
    --header 'x-pm-apiversion: 3' \
    --header 'Accept: application/vnd.protonmail.v1+json' \
    -o /dev/null \
    --timeout 10 --tries 1 -q -O "$openvpn_config" \
    "https://api.protonmail.ch/vpn/config?Platform=$(detect_platform_type)&LogicalID=$config_id&Protocol=$selected_protocol"

  config_cache_name="$config_cache_path/$(detect_platform_type)-$config_id-$selected_protocol"
  if [[ -f "$config_cache_name" ]]; then
    if [[ $(diff "$config_cache_name" "$openvpn_config") ]]; then
      echo "Configuration changed (of $(detect_platform_type)-$selected_protocol-$config_id)"
    fi
  fi

  cp "$openvpn_config" "$config_cache_name"
  echo "Connecting..."
  {
    max_checks=3
    counter=0
    while [[ $counter -lt $max_checks ]]; do
      sleep 6
      new_ip="$(check_ip)"
      if [[ ("$current_ip" != "$new_ip") && ("$new_ip" != "Error.") ]]; then
        echo "[$] Connected!"
        echo "[#] New IP: $new_ip"

        # DNS management
        if [[ -f "$(get_protonvpn_cli_home)/.custom_dns" ]]; then
          modify_dns to_custom_dns # Use Custom DNS.
          echo "[Warning] You have chosen to use a custom DNS server. This may make you vulnerable to DNS leaks. Re-initialize your profile to disable the use of custom DNS."
        else
          modify_dns to_protonvpn_dns # Use ProtonVPN DNS server.
        fi

        # killswitch enable # Enable killswitch

        echo "$config_id" > "$(get_protonvpn_cli_home)/.connection_config_id"
        echo "$selected_protocol" > "$(get_protonvpn_cli_home)/.connection_selected_protocol"
        exit 0
      fi

      counter=$((counter+1))
    done

    echo "[!] Error connecting to VPN."
    if grep -q "AUTH_FAILED" "$connection_logs"; then
      echo "[!] Reason: Authentication failed. Please check your ProtonVPN OpenVPN credentials."
    fi
    openvpn_disconnect quiet dont_exit
    exit 1
  } &
  status_check_pid=$!

  OPENVPN_OPTS=(
    --config "$openvpn_config"
    --auth-user-pass "$(get_protonvpn_cli_home)/protonvpn_openvpn_credentials"
    --auth-retry nointeract
    --verb 4
    --log "$connection_logs"
  )

  if [[ -f "$(get_protonvpn_cli_home)/.decrease_openvpn_privileges" ]]; then
    OPENVPN_OPTS+=(--user nobody
                   --group "$(id -gn nobody)"
                  )
  fi

  if [[ $PROTONVPN_CLI_DAEMON == true ]]; then
    openvpn --daemon "${OPENVPN_OPTS[@]}"
    trap 'openvpn_disconnect "" dont_exit' INT TERM
  else
    trap 'openvpn_disconnect "" dont_exit' INT TERM
    openvpn "${OPENVPN_OPTS[@]}"
    openvpn_exit=$?
  fi

  wait $status_check_pid
  status_exit=$?
  if [[ $PROTONVPN_CLI_DAEMON != true ]] && (( status_exit == 0 )); then
    status_exit=$openvpn_exit
  fi
  exit $status_exit
}