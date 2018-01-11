from scapy.all import *


def detect_button(pkt):
    if pkt.haslayer(DHCP):
            print "Button Press Detected : " + pkt[Ether].src

sniff(prn=detect_button, filter="(udp and (port 67 or 68))", store=0)
