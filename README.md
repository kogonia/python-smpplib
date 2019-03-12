SMPP
====

## Settings:  
#### settings.py
```
sms_host = '192.168.0.1'    <-set SMSC ip
sms_port = 2020             <-set SMSC port
sms_pass = ''               <-set password for smpp-client
sms_id = ''                 <-set login for smpp-client
```
#### my_tx.py
```
Line 47 source_addr="SMPP", <-set display name
```
#### phone_list.txt  
you can specify several numbers here  

## log file  
manually create diretory (if error)  
mkdir /var/log/sms/  
touch /var/log/sms/msg.log  

