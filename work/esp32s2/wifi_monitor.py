import gc
import time
import board
import digitalio
import supervisor
import random

import wifi
import espidf
import ipaddress
import socketpool
import ssl

from secrets import secrets


PARSE_HEADER = True
PARSE_BODY = True  # if True, PARSE_HEADER must be True
PARSE_IES = False  # if True, PARSE_BODY must be True

type_names = ("mgmt", "ctrl", "data", "extn")

subt_names = ("AssocReq", "AssocResp", "RAssoc Req", "RAssocResp",
              "ProbeReq", "ProbeResp", "Timing", "Reserved7",
              "Beacon", "ATIM", "DisAssoc", "Auth",
              "DeAuth", "Action", "ActionN", "ReservedF",)

fixed = (4,6,10,6,
         0,12,0,0,
         12,0,2,6,
         2,0,0,0,)

ie_names = {0: "0_SSID",
            1: "1_Rates",
            2: "2_FH",
            3: "3_DS",
            4: "4_CF",
            5: "5_TIM",
            6: "6_IBSS",
            7: "7_Country",
            8: "8_HopParam",
            9: "9_HopTable",
            10: "10_Req",
            16: "16_Challenge",
            32: "32_PowConst",
            33: "33_PowCapab",
            34: "34_TPCReq",
            35: "35_TPCRep",
            36: "36_Chans",
            37: "37_ChSwitch",
            38: "38_MeasReq",
            39: "39_MeasRep",
            40: "40_Quiet",
            41: "41_IBSSDFS",
            42: "42_ERP",
            48: "48_Robust",
            50: "50_XRates",
            221: "221_WPA",}


def extract_dhcp():
    dhcp_name = ""
    mac = 0
    if DHCP:
        with open(DHCP, "r") as df:
            for dl in df:
                if dl:
                    if (dl[0] != '#'):
                        # line format: DHCPNAME, MAC, IPv4
                        try:
                            dhcp_name = dl.split(',')[0].strip()
                        except IndexError as e:
                            # print('DHCP name not found in line: ', e)
                            continue
                        try:
                            mac =  dl.split(',')[1].strip().split(',')[0].strip().upper()
                        except IndexError as e:
                            # print('DHCP MAC not found in line: ', e)
                            continue
                        dhcp_dict[mac] = dhcp_name
    return

def lookup_dhcp(mac):
    dhcp_name = ""
    # mac = mac.upper()
    if mac in dhcp_dict:
        dhcp_name = dhcp_dict[mac]
    return dhcp_name

def check_type(mac):
    # determine MAC type
    mactype = ""
    try:
        # mac_int = int('0x' + mac[1], base=16)  # not supported in CP
        mac_int = int("".join(("0x", mac[0:2])))
        if (mac_int & 0b0011) == 0b0011:    # 3,7,B,F LOCAL MULTICAST
            mactype = "L_M"
        elif (mac_int & 0b0010) == 0b0010:  # 2,3,6,7,A,B,E,F LOCAL
            mactype = "LOC"
        elif (mac_int & 0b0001) == 0b0001:  # 1,3,5,7,9,B,D,F MULTICAST
            mactype = "MUL"
        else:  # 0,4,8,C VENDOR (or unassigned)
            mactype = "VEN"
    except (ValueError, IndexError) as e:
        pass
    return mactype

def parse_header(fd, buf):
    fd["type"]     = (buf[0] & 0b00001100) >> 2
    fd["typename"] = type_names[fd["type"]]
    fd["subt"]     = (buf[0] & 0b11110000) >> 4
    fd["subtname"] = subt_names[fd["subt"]]
    fd["fc0"]       = buf[0]
    fd["fc1"]       = buf[1]
    fd["dur"]      = (buf[3] << 8) + buf[2]
    fd["a1"]   = ":".join("%02X" % _ for _ in buf[4:10])
    fd["a2"]   = ":".join("%02X" % _ for _ in buf[10:16])
    fd["a3"]   = ":".join("%02X" % _ for _ in buf[16:22])
    fd["a1_type"]  = check_type(fd["a1"])
    fd["a2_type"]  = check_type(fd["a2"])
    fd["a3_type"]  = check_type(fd["a3"])
    fd["seq"]      = ((buf[22] & 0b00001111) << 8) + buf[23]
    fd["frag"]     = (buf[22] & 0b11110000) >> 4
    return fd

def parse_body(fd, buf):
    ies = {}
    fd["ssid"] = ""
    pos = 24 + fixed[fd["subt"]]
    while pos < fd["len"] - 1:
        try:
            ie_id  = buf[pos]
            ie_len = buf[pos + 1]
            ie_start = pos + 2
            ie_end = ie_start + ie_len

            if (ie_id == 0):
                if (ie_len > 0):
                    # if fd["subt"] in (1, 4, 5, 8):
                    ssid = ""
                    for _ in range(ie_start, ie_end):
                        ssid = ssid + chr(buf[_])
                    fd["ssid"] = ssid

            # if SSID wasn't in the first IE, too bad...
            if not PARSE_IES:
                break;

            ie_body = "".join("%02X" % _ for _ in buf[ie_start : ie_end])
            if ie_id in ie_names:
                ies[ie_names[ie_id]] = ie_body
            else:
                ies[ie_id] = ie_body
        except IndexError as e:  # 32   32      33
            print("IndexError", e, pos, ie_end, fd["len"])
        pos = ie_end
    fd["ies"] = ies
    return fd

def get_packet():
    fd = {}
    fd["qlen"] = monitor.queued()
    fd["lost"] = monitor.lost()
    received = monitor.packet()
    if received != {}:
        fd["len"] = received[wifi.Packet.LEN]
        fd["ch"] = received[wifi.Packet.CH]
        fd["rssi"] = received[wifi.Packet.RSSI]
        if PARSE_HEADER:
            fd = parse_header(fd, received[wifi.Packet.RAW])
        if PARSE_BODY:
            fd = parse_body(fd, received[wifi.Packet.RAW])
    return fd

if supervisor.runtime.usb_connected:
    while not supervisor.runtime.serial_connected:
        pass
    print(".")
    time.sleep(1)
    print(".")
    time.sleep(1)

print("-"*49)
print("Starting Monitor...")
monitor = wifi.Monitor()
loop = 0
packets = 0

print("-"*49)
start = time.monotonic_ns()
while True:
    loop += 1
    try:
        monitor.channel = random.randrange(1, 14)
        fd = get_packet()

        if len(fd) > 2:
            packets += 1
            runtime = (time.monotonic_ns() - start) / 1_000_000_000
            print(f'{loop} {packets}p {runtime:.3f}s {int(packets / runtime):2d}/s', end=" ")
            print(f'{fd["qlen"]:3d} {fd["lost"]:3d} {espidf.heap_caps_get_largest_free_block():5d}', end=" ")
            print(f'{fd["len"]:4d} {fd["ch"]:2d} {fd["rssi"]:+3d}', end=" ")
            if PARSE_HEADER:
                print(f'{fd["fc0"]:02X} {fd["typename"]} {fd["subtname"]:11s} {fd["fc1"]:02X} {fd["dur"]:04X}', end=" ")
                print(f'{fd["a1"]} {fd["a1_type"]} {fd["a2"]} {fd["a2_type"]} {fd["a3"]} {fd["a3_type"]}', end=" ")
                print(f'{fd["seq"]:3d} {fd["frag"]:2d}', end=" ")
            if PARSE_BODY:
                print(f'{fd["ssid"]:18s}', end=" ")
                ie_ids = []
                for _ in fd["ies"]:
                    ie_ids.append(int(str(_).split("_")[0]))
                ie_ids.sort()
                for _ in ie_ids:
                    print(_, end=" ")
            print()

            if PARSE_IES:
                for _ in fd["ies"]:
                    print(f'{_} {fd["ies"][_]}', end=" ")
                print()
                print()

            if packets % 100 == 1:
                print("💾", espidf.heap_caps_get_largest_free_block(), espidf.heap_caps_get_free_size(), espidf.heap_caps_get_total_size(), gc.mem_free(), end=" ")
                print()
    except RuntimeError as e:
        print("RuntimeError", e)


