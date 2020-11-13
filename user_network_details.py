import getpass
import os.path
import platform
import re
import socket
import subprocess
import sys
import uuid


def get_wifi_info():
    try:
        if sys.platform in ['Windows', 'win32', 'cygwin']:
            return_type = 0  # 0 for return None, 1 for return wifi_info, 2 for return ethernet_info
            wifi_info = os.popen("Netsh WLAN show interfaces").readlines()
            ethernet_info = os.popen(
                "netsh interface show interface name=\"Ethernet\"").readlines()
            print("Wifi Info: " + str(wifi_info))
            print("Ethernet Info: " + str(ethernet_info))
            wifi_name = "Cant Find WiFi Name"
            for line in wifi_info:
                if line.startswith('    State'):
                    print("Wifi Connection: " +
                          (line.split(": ")[1]).split("\n")[0])
                    if line.split(": ")[1] == "connected\n":
                        return_type = 1
                if line.startswith('    SSID'):
                    wifi_name = line.split(": ")[1].split("\n")[0]
                    print("Connected to Wifi: " + wifi_name)
            for line in ethernet_info:
                if line.startswith('   Connect state:'):
                    print("Ethernet Connection: " +
                          line.split(":        ")[1].split("\n")[0])
                    if line.split(":        ")[1] == "Connected\n":
                        return_type = 2
            if return_type == 0:
                return None
            elif return_type == 1:
                return wifi_name
            elif return_type == 2:
                return ethernet_info
        else:
            return None
    except Exception as e:
        print(e)
        return None


def get_username():
    try:
        username = getpass.getuser()
        print("Username: " + username)
        return username
    except Exception as e:
        print(e)
        return None


def get_homedir():
    try:
        homedir = os.path.expanduser("~")
        print("Home Directory: " + homedir)
        return homedir
    except Exception as e:
        print(e)
        return None


def get_hostname():
    try:
        hostname = socket.gethostname()
        print("Hostname: " + hostname)
        return hostname
    except Exception as e:
        print(e)
        return None


def get_alt_homedir():
    try:
        alt_homedir = platform.node()
        print("Alt Hostname: " + alt_homedir)
        return alt_homedir
    except Exception as e:
        print(e)
        return None


def get_host_name_by_address():
    try:
        hostname_by_address = socket.gethostbyaddr(socket.gethostname())
        print("Hostname by Address: " + str(hostname_by_address))
        return hostname_by_address
    except Exception as e:
        print(e)
        return None


def get_ip_address():
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
        print("IP Address: " + ip_address)
        return ip_address
    except Exception as e:
        print(e)
        return None


def get_mac_address():
    try:
        mac_address = hex(uuid.getnode())
        print("MAC Address: " + mac_address)
        return mac_address
    except Exception as e:
        print(e)
        return None


def get_formatted_mac_address():
    try:
        mac_address = hex(uuid.getnode())
        print("MAC Address: " + mac_address)
        print("Formatted MAC address: ", end="")
        print(':'.join(re.findall('..', '%012x' % uuid.getnode())))
        return mac_address
    except Exception as e:
        print(e)
        return None


def get_user_details():
    user_details = {
        "wifi_info": get_wifi_info(),
        "username": get_username(),
        "homedir": get_homedir(),
        "alt_homedir": get_alt_homedir(),
        "hostname": get_hostname(),
        "ip_address": get_ip_address(),
        "mac_address": get_mac_address(),
        "formatted_mac_address": get_formatted_mac_address(),
        "hostname_by_address": get_host_name_by_address()
    }
    return user_details


if __name__ == '__main__':
    get_user_details()
