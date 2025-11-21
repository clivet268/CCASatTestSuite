import iperf3
import os
import paramiko

GEO = ("GEO", "ccasatpi.dyn.wpi.edu")
LEO = ("LEO", "ccasatpi.dyn.wpi.edu")
WL4GLTE = ("4G/LTE", "ccasatpi.dyn.wpi.edu")
WL5G = ("5G", "ccasatpi.dyn.wpi.edu")
WiFi = ("WiFi", "ccasatpi.dyn.wpi.edu")
Ethernet = ("Ethernet", "ccasatpi.dyn.wpi.edu")

platforms = [GEO, LEO, WL4GLTE, WL5G, WiFi, Ethernet]
ccas = ["CUBIC", "HyStart", "HyStart++", "BBR", "SEARCH"]


def default(platform, port = 5201):
	client = iperf3.Client()
	client.duration = 10  #Seconds
	client.server_hostname = platform[1]
	client.port = port #50268

	result = client.run()

	# Process the results
	if result.error:
		print(f"Error: {result.error}")
	else:
		print("Test completed successfully.")
		print(f"Bandwidth: {result.sent_Mbps} Mbps (sent), {result.received_Mbps} Mbps (received)")
		print(f"Retransmits: {result.retransmits}")
condtions = [default]


def readServerList(filename:str):
	out = {}
	with open(filename,"r") as file:
		for line in file:
			if(len(line)==0):
				continue
			(server,port,alg) = line.split(':')
			out[server] = {port,alg}
	return out

serverList = readServerList("./serverlist.txt")

def ssh(server):
    lines = []
    with open(".env","r") as envfile:
        for line in envfile:
            lines.append(line)
        for line in lines:
            parts = str(line).split('=')
            for i in range(len(parts)):
                parts[i]= parts[i].strip()
            os.environ[parts[0]]=parts[1]

    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    location = os.getenv('LOCATION')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server,username=username,password=password)
    client.exec_command(f"cd ~")
    stdin, stdout,stderr =client.exec_command("sudo -S ./clientruntest.sh")
    stdin.write(password+'\n')
    stdin.flush()

    stdin.close()
    stdout.close()
    stderr.close()
    client.close()

for platform in platforms:
	default(platform)
