SMPP
====

# Settings:  
### settings.py  
```sms_host = '192.168.0.1'    <-set SMSC ip
sms_port = 2020             <-set SMSC port
sms_pass = ''               <-set password for smpp-client
sms_id = ''                 <-set login for smpp-client
```
### my_tx.py  
```Line 35 client.send_message(source_addr='SMPP', <-set display name
Line 36     source_addr_ton=5,                  <-set source ton
Line 37     source_addr_npi=0,                  <-set source npi
Line 38     dest_addr_ton=1,                    <-set dst ton
Line 39     dest_addr_npi=1,                    <-set dst npi
Line 40     destination_addr=DST_ADDR,
Line 41     short_message=MSG.encode('cp1251')) <-set encoding
```

### phone_list.txt  
you can specify several numbers here  

## log file  
manually create diretory (if error)  
mkdir /var/log/sms/  
touch /var/log/sms/msg.log  

