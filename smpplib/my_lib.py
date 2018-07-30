#!/usr/bin/python3

import re, time

def l(data):
    f = open("/var/log/smpp/msg.log", "a")
    log=time.strftime("%F %T")+"\n"+data+"\n==========================\n"
    print (log)
    f.write(log)
    f.close()

def check(code):
    f=open("/var/log/smpp/msg.log", "r")
    str="code:\t"+code
    if str in f.read():
        return "bad"
    else:
        return "ok"

def get_data(sms,sender):
# check alloved numbers
    if (sender == "allowed number 1") or (sender == "allowed number 2"):
        try:
# parce sms
            text=re.search (r'pattern',sms)
            data_1 = text.group(1)
            data_2 = text.group(2)
# if you have some uniq code in text
            uniq_data = text.group(3)
            check_result=check(uniq_data)
            if check_result=="bad":
                log="code dublicated "+uniq_data
                l(log)
            else:
                db_write(data_1,data_2,sms)
                log="data_1:\t"+data_1+"\n"+"data_2:\t"+data_2+"\n"+"uniq code:\t"+uniq_data
                l(log)
        except AttributeError:
            log="Can\'t parce received message.\nText: "+sms
            l(log)
# if source number not in allowed list
    else:
        log="Spam from "+sender+"\nText: "+sms
        l(log)

def db_write(data_1,data_2,sms):
    import cx_Oracle
    CONN_INFO = {
        'host': 'ip oracle db server',
        'port': 'port',
        'user': 'db user',
        'psw': 'passwd for db user',
        'dbname': 'db name',
    }
    CONN_STR = '{user}/{psw}@{host}:{port}/{dbname}'.format(**CONN_INFO)
    try:
        conn = cx_Oracle.connect(CONN_STR)
        cursor=conn.cursor()
    except Exception as e:
        err="Error. Connect to db:\n"+str(e)+"\n"
        l(err)
    try:
# call oracle procedure with parced data
        cursor.callproc("procedure 1 name",[data_1,data_2])
    except Exception as e:
        err="Error. Procedure 1:\n"+str(e)+"\n"
        l(err)
    try:
# call oracle procedure with full sms text
        cursor.callproc("procedure 2 name",[sms])
    except Exception as e:
        err="Error. Procedure 2:\n"+str(e)+"\n"
        l(err)
