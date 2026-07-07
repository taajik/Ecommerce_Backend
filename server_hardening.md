
# Server Hardening

A simple list of things to do before deploying a project on a server.

Choose a port for ssh and use it anywhere in this document that this variable is used:
`SSH_PORT`


## Update and install packages

```
sudo apt update
sudo apt upgrade -y

sudo apt install wget curl git vim htop unzip at net-tools dnsutils tcpdump telnet fail2ban iptables-persistent

sudo apt autoremove -y
```


## SSH

Generate public-private key pairs and use them for authentication instead of a password.

Set these in `/etc/ssh/sshd_config`:
```
Port $SSH_PORT
ListenAddress 0.0.0.0
PermitRootLogin no
PasswordAuthentication no
```
and then
```
sudo systemctl restart ssh
```

To set up an inactivity timeout, create the file `/etc/profile.d/timout-settings.sh` with this content:
```
#!/bin/bash
TMOUT=900
readonly TMOUT
export TMOUT
```

<!-- hostnamectl set-hostname $HostName -->


## Disable unwanted services

```
sudo systemctl stop postfix
sudo systemctl disable postfix
sudo systemctl mask postfix

sudo systemctl stop firewalld
sudo systemctl disable firewalld
sudo systemctl mask firewalld

sudo systemctl stop ufw
sudo systemctl disable ufw
sudo systemctl mask ufw
```


## Firewall

To view all existing rules:
```
sudo iptables -L --line-numbers -v
```


> Before making changes to the firewall, set up a fail-safe to not get locked out:
> ```
> iptables-save > /root/iptables.backup
> echo "iptables-restore < /root/iptables.backup" | at now + 5 minutes
> ```
>
> and cancel it after, if there are no problems:
> ```
> atq
> atrm <jobid>
> ```

<br>

**Close all ports except 80, 443 and ssh's port:**

(run all these as a script)
```
#!/bin/bash

# Flush all existing rules
iptables -F
iptables -X

# Set default policies to DROP
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback interface (localhost)
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Allow SSH, HTTP and HTTPS ports
iptables -A INPUT -p tcp --dport $SSH_PORT -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

And persist the rules:
```
netfilter-persistent save
```


## fail2ban

Create the file `/etc/fail2ban/jail.local` with this content:
```
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = $SSH_PORT

[dropbear]
port = $SSH_PORT

[selinux-ssh]
port = $SSH_PORT
```

And then enable it:
```
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo fail2ban-client status
```


## Timezone

To have accurate timezone and synchronization:
```
sudo timedatectl set-timezone UTC
sudo timedatectl set-ntp true
```


## Docker

Installation instructions:
> https://docs.docker.com/engine/install/

<br>

Add your system user to docker's group to be able to run docker without super user privileges:
```
sudo usermod -aG docker myappuser
```

And enable the docker service: (these are not needed for Debian and Ubuntu)
```
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```


## Run the app

Now you can copy the project files onto the server.

- Depending on the server resources, adjust gunicorn's --workers and --threads values, and resource limits of compose services in the [docker-compose.yml](/docker-compose.yml) file.

- Restrict permissions to the env file:
```
chmod 600 .env
```

- As a safety measure to hide the .env file, rename it to somethings random and update references to it in the compose and dockerignore files. (beware of the compose file's use of .env for its own variable interpolation)

<!-- mkdir static -->

And finally you can run
```
docker compose up -d
```
