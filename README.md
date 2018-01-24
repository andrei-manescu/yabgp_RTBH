# yabgp_RTBH
# A simple RTBH mechanism to monitor Maildir directory for spam and add the source IP addresses into BGP, creating a remote triggered blackhole for spammers IP
# Spammers exploit remote servers that have poor security to send aggressive spam (with malicious attachments). 
# Having the network edge protection from these servers is a crucial step towards a secure enterprise.

#
# ***** How does it work *****
# 1. YABGP is used as BGP peer to inject prefixes into the network.
# 2. YABGP uses RESTFUL API to accept remote interaction.
# 3. Every IMAP mail server will use a "Maildir" formatted mailbox. 
#     Spam/Junk folder has it's own directory on the disk.
# 4. Once an email message is categorized as SPAM and moved to Spam/Junk directory, 
#     a "spam_watchdog.py" python script will pick up the file and extract the IP of the sender.
# 5. The IP is submitted along with an arbitrary next hop (preferably in RFC1918 or bogon ranges).
# 6. Based on the next hop, the network injection point will use the NH as a discard or reject (preferably discard).
# 7. IP Spoofing screen should be used to perform uRPF check on connection from infected hosts.
# 8. Since the NH is discard, incoming packet will fail the uRPF check and will be discarded.
