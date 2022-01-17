import os
import sys
import glob
import requests
import smtplib
import fnmatch
import time
import onetimepad
import configparser
import xml.etree.ElementTree as ET
import urllib.request

from zeep import Client
from datetime import datetime
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException

path = "E:\RI_SHARE\RI\INPUTFILES\CSV"
isExist = os.path.exists(path)

FROM_ADDRESS = 'aowindows@sapiens.com'

# read the config.ini file and build the variables with values from configuration


config = configparser.ConfigParser()
config.read('E:\Programs\Python\Python37\libertyAutomation\config.ini')

# source system name from config file
basesourceSystem1 = config['SOURCE_SYSTEM']['sourceSystemName1'] 
basesourceSystem2 = config['SOURCE_SYSTEM']['sourceSystemName2']
basesourceSystem3 = config['SOURCE_SYSTEM']['sourceSystemName3']

def webserviceCall():
    try:
        health_check = (urllib.request.urlopen("http://azlibmusriwsua1:4421/ri-web/ws/jaxws/runProcSetWs?wsdl").getcode())
        if(health_check == 200):
            client = Client(wsdl='http://azlibmusriwsua1:4421/ri-web/ws/jaxws/runProcSetWs?wsdl')
            #print(str(datetime.today().strftime('%Y-%m-%d')))
            result= client.service.runProcess('LTV',str(datetime.today().strftime('%Y-%m-%d')),'','','','','','1','','','')
            file = open("E:\Programs\Python\Python37\libertyAutomation\log.txt","w")
            file.write(str(result))
            file.close()
            res = result['message']
            print(res)
        else:
            sendAPIdown_Mail("API_Down")
            sys.exit(9)
    except Exception as e:
        print('Unexpected error encountered ...')
        print(e)
        sys.exit(9)
    return res
#end of webservice call

def get_contacts(filename):
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails

def read_template(filename):
    """
    Returns a Template object comprising the contents of the 
    file specified by filename.
    """
    
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)



#Testing Purpose
'''def sendEmail():
 
    sender = 'aowindows@domain.com'
    receivers = ['*******@gmai.com']
    port = 587
    pwd = '********'
    msg = MIMEText('This is test mail')
    message_template = read_template('message3.txt')
    msg['Subject'] = 'Test mail'
    msg['From'] = 'aowindows@domain.com'
    msg['To'] = 'abcd@domain.com'

    with smtplib.SMTP('smtp.sendgrid.net', port) as server:
         server.login('*********',pwd)
         server.sendmail(sender, receivers, msg.as_string())
         print("Successfully sent email")'''

def sendMail(msgdata):
        names, emails = get_contacts('E:\Programs\Python\Python37\libertyAutomation\contactgroup1.txt') # read contacts
        #message_template = read_template('message3.txt')
        print(emails)
        if(msgdata == "PatternNotMatched"):
            message_template = read_template('E:\Programs\Python\Python37\libertyAutomation\mail_template.txt')
        if(msgdata == "CountNotEqual"):
            message_template = read_template('E:\Programs\Python\Python37\libertyAutomation\mail_template1.txt')
        if(msgdata == "PathNotFound"):
            message_template = read_template('E:\Programs\Python\Python37\libertyAutomation\mail_template2.txt')
        if(msgdata == "inprogress"):
            message_template = read_template('E:\Programs\Python\Python37\libertyAutomation\mail_template3.txt')

        # set up the SMTP server
        cipher = os.environ['cipher']
        key = os.environ['key']
        token = onetimepad.decrypt(cipher,key)
        
        
        s = smtplib.SMTP(host='smtp.sendgrid.net',port=587)
        s.login('**********',token) 

        # For each contact, send the email:
        for name, email in zip(names, emails):
            msg = MIMEMultipart() #create a message
            # add in the actual person name to the message template
            message = message_template.substitute(PERSON_NAME=name.title())
            # setup the parameters of the message
            msg['From']=FROM_ADDRESS
            msg['To']=email
            msg['Subject']="This is UAT TEST Mail"        
            # add in the message body
            msg.attach(MIMEText(message, 'plain'))        
            # send the message via the server set up earlier.
            s.send_message(msg)
            del msg        
        # Terminate the SMTP session and close the connection
        s.quit()
        
 
def sendAPIdown_Mail(msgdata):
        names, emails = get_contacts('E:\Programs\Python\Python37\libertyAutomation\contactgroup2.txt') # read contacts
        print(emails)
        if(msgdata == "API_Down"):
            message_template = read_template('E:\Programs\Python\Python37\libertyAutomation\mail_template4.txt')
            # set up the SMTP server
            cipher = os.environ['cipher']
            key = os.environ['key']
            token = onetimepad.decrypt(cipher,key)
            
            
            s = smtplib.SMTP(host='smtp.sendgrid.net',port=587)
            s.login('srazuresmtp',token) 

        # For each contact, send the email:
        for name, email in zip(names, emails):
            msg = MIMEMultipart() #create a message
            # add in the actual person name to the message template
            message = message_template.substitute(PERSON_NAME=name.title())
            # setup the parameters of the message
            msg['From']=FROM_ADDRESS
            msg['To']=email
            msg['Subject']="This is UAT TEST Mail"        
            # add in the message body
            msg.attach(MIMEText(message, 'plain'))        
            # send the message via the server set up earlier.
            s.send_message(msg)
            del msg        
        # Terminate the SMTP session and close the connection
        s.quit()

#Setting the Status file value to Completed
def Set_statusFile():
        fin = open(r"E:\Programs\Python\Python37\libertyAutomation\status.txt", "rt")
        data = fin.read()
        data = data.replace('In-Progress', 'Completed')
        fin.close()
        fin = open(r"E:\Programs\Python\Python37\libertyAutomation\status.txt", "wt")
        fin.write(data)
        fin.close()
        
def main():
    try:
        with open(r"E:\Programs\Python\Python37\libertyAutomation\status.txt") as infile:
            for line in infile:
                line = line.rstrip('\n')
                
                if line == "Completed":
                    fin = open(r"E:\Programs\Python\Python37\libertyAutomation\status.txt","rt")
                    data = fin.read()
                    data = data.replace('Completed', 'In-Progress')
                    fin.close()
                    fin = open(r"E:\Programs\Python\Python37\libertyAutomation\status.txt", "wt")
                    fin.write(data)
                    fin.close()
                    
                    if isExist == True:
                        list = os.listdir(path) 
                        number_files = len(list)
                        
                        if number_files >= 5:
                            
                            count = 0  #To Maintain the count of the file
                            count1 = 0
                            count2 = 0
                            for file in os.listdir(r'E:\RI_SHARE\RI\INPUTFILES\CSV'):
                                #print(file)
                                if (fnmatch.fnmatch(file, '*_inbound_smme_*')):
                                    pattern = file.split("_")
                                    sourcesys = [pattern][0][0]
                                    #print(sourcesys)
                                    #print(basesourceSystem1)
                                    if(fnmatch.fnmatchcase(file, '*_loaded*') == False | fnmatch.fnmatchcase(file, '*_corrupted*') == False):
                                        if(sourcesys == basesourceSystem1):
                                            count = count + 1
                                            if(count == 5):
                                                print("i am calling web service for ncci")                                            
                                                webserviceCall()
                                                time.sleep(60) # Waits 60 Seconds after Every WebService call
                                                count = 0
                                                #Set_statusFile()
        
                                        if(sourcesys == basesourceSystem2):
                                            count1 = count1 + 1
                                            if(count1 == 5):
                                                print("i am calling web service for aipso")                                            
                                                webserviceCall()
                                                time.sleep(60) # Waits 60 Seconds after Every WebService call
                                                count1 = 0
                                                #Set_statusFile()

                                        if(sourcesys == basesourceSystem3):
                                            count2 = count2 + 1
                                            if(count2 == 5):
                                                print("i am calling web service for masscar")                                            
                                                webserviceCall()
                                                time.sleep(60) # Waits 60 Seconds after Every WebService call
                                                count2 = 0
                                                #Set_statusFile()

                                    #Add Here if any new Source System comes
                                            
                                    Set_statusFile()    
                                    
                                else:
                                    print ("Pattern not matched")
                                    Set_statusFile()
                                    #sendMail("PatternNotMatched") # SMTP Liberty process is failed because pattern not matched
                                    #sys.exit(9)

                            if count in (1, 2, 3, 4): 
                                print (str(5 -count)+ " Files are missing in ncci")
                                sendMail("CountNotEqual")  #SMTP Liberty process is failed because Count Not Equal
                               

                            if count1 in (1, 2, 3, 4):  
                                print(str(5 -count1)+ " Files are missing in sourcesytemname2")
                                sendMail("CountNotEqual")  #SMTP Liberty process is failed because Count Not Equal
                              

                            if count2 in (1, 2, 3, 4):
                                print(str(5 -count2)+ " Files are missing in sourcesytemname3")
                                sendMail("CountNotEqual")  #SMTP Liberty process is failed because Count Not Equal
                                #sys.exit(9)

                        else:
                            print ("File Count is not equal to 5")
                            Set_statusFile()
                            sendMail("CountNotEqual") #SMTP Liberty process is failed because File Count is not equal to 5
                            sys.exit(9)

                    else:
                        print ("Path not found")
                        Set_statusFile()
                        sendMail("PathNotFound")  #SMTP Liberty process is failed because Path not found
                        sys.exit(9)
                else:
                    #sendEmail()
                    sendMail('inprogress') #Sending mail if status is In progress
                    print("The Web Service call is In Progress Only Please wait for Control file to Show the value completed")
                    
    except Exception as e:
        print('Unexpected error encountered ...')
        print(e)
        sys.exit(9)
        
#end of main function

# starting point to this program
if __name__ == "__main__":
    # run the main program
    main()
   
    print('Exiting normally ...')
    sys.exit(9)
    exit(0)

# end of program


