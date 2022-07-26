import pyshark
import requests
import csv
from colorama import Fore
from datetime import date
import ipaddress

def read_pcap(pcap_file):
	ips = []
	try:
		pcap = pyshark.FileCapture(pcap_file)
		print(Fore.GREEN + "[+] Pcap File is valid")
		for packet in pcap:
			if "IP" in packet: 
				ips.append(packet.ip.src) 
				ips.append(packet["ip"].dst)
		
		ips_list(ips)

	except FileNotFoundError:
		exit(Fore.RED + '[!] Pcap path is incorrect')


def ips_list(ips):
	ips_lists = []
	aborted_ips = []
	for ip in ips :
		if ip not in ips_lists and ipaddress.ip_address(ip).is_global:
			ips_lists.append(ip)
		elif ip not in aborted_ips and '192.168.' in ip:
			aborted_ips.append(ip)
	for ip in aborted_ips:
		print(Fore.YELLOW + "[!] Remove " + Fore.RED + ip + Fore.YELLOW + ' From Scanning')
	#call get ip info function
	if len(ips_lists) <1:
		exit(Fore.RED + "[-] No ip to scan. ")
	get_ip_info(ips_lists)


def get_ip_info(list_ip):
	data = []
	for ip in list_ip:
		
		print(Fore.YELLOW + "[+] Start analyzing IP : " + ip )
		try:
			req = requests.get("http://ip-api.com/json/"+ip+"?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,,query").content.decode()
			if "message" not in req:
				data.append(req)
		except requests.exceptions.ConnectionError:
			exit(Fore.RED + "Check your internet connection and try again ....")
	dic_data = []
	for i in data:
		l = eval(i)
		dic_data.append(l)
	export_result(dic_data)


def export_result(data):
	for i in data:
		i['ip'] = i.pop('query') 
		i = i.pop('status')
	fieldnames = []
	for i in data[0].keys():
		fieldnames.append(i)
	with open('scan_result-'+str(date.today())+'.csv', 'w', encoding='UTF8', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(data)
	print(Fore.GREEN + "\n  **Report Exported Succesfully!**")
 
pcap_path = input("[-] Enter pcap file: ")

ips = read_pcap(pcap_path)

