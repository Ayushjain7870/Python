from tkinter import *
import threading
from pprint import pprint
import json
import os
import requests
import pandas as pd
from tkinter import messagebox
from simple_salesforce import Salesforce, SalesforceLogin, SFType

def updateCurrentLogs(textInp):
    #print(textInp)
    CurrentLogs.configure(text = textInp)
    
def updateLabelAsny():
    print('first thread')
    loadingLabel.configure(text = 'Processing')   
    
def sfExecute():
    t1 = threading.Thread(target=updateLabelAsny)    
    t1.start()    
    t2 = threading.Thread(target=sfExecute_or)    
    t2.start()    
     
def sfExecute_or():
    print('second thread')
    
    #print(var.get(),user_value.get(),pass_value.get(), isSandbox.get(),security_token_var.get(),attachment_limit_var.get(),attachment_size_var.get())
    try:
        UserEmailVar = str(user_value.get())
        passVar = str(pass_value.get())
        sandboxVar = bool(isSandbox.get())
        secTokenVar = str(security_token_var.get())
        attLimitVar = int(attachment_limit_var.get())
        attSizeLimitVar = int(attachment_size_var.get())
    except:
        loadingLabel.configure(text = 'Invalid Entry')
        threading.Thread(target=updateCurrentLogs, args=('',)).start()
        print('exception-Invalid Entry')
        return
    #print(UserEmailVar,passVar,sandboxVar,attSizeLimitVar,attLimitVar)
    username = UserEmailVar
    password = passVar
    security_token = secTokenVar
    domain = 'login'
    AttSizeLimitKb_sec = attSizeLimitVar
    queryLimit = attLimitVar
    
    print('Parameters:',username,password,security_token,domain,AttSizeLimitKb_sec,queryLimit)
    

    if sandboxVar == True:        
        domain =  'test'

    goAhead = True
    noRecords = True
    if (username == '') or (password=='') or (security_token == '') or (AttSizeLimitKb_sec<0) or (queryLimit<=0):
        goAhead = False

    if (username == None) or (password==None) or (security_token == None) or (AttSizeLimitKb_sec==None) or (queryLimit==None):
        goAhead = False

    print('Executing:',goAhead)
    threading.Thread(target=updateCurrentLogs, args=('Executing:'+str(goAhead),)).start()  
        
    if goAhead == True:
        print(username,password,security_token,domain)
        try:
            threading.Thread(target=updateCurrentLogs, args=('Attempting to connect to Servers...',)).start()
            session_id, instance = SalesforceLogin(username=username, password=password, security_token=security_token, domain=domain)
            sf = Salesforce(instance=instance, session_id=session_id)
        except:
            loadingLabel.configure(text = 'Invalid Login')
            threading.Thread(target=updateCurrentLogs, args=('',)).start()
            print('exception')
            return
        querySOQL = 'SELECT Id, Name, ParentId, Body, BodyLength From Attachment WHERE BodyLength >' + str(AttSizeLimitKb_sec) + 'ORDER BY CreatedDate DESC LIMIT '+str(queryLimit)

        # query records method
        print('QUERY is going to Execute')
        threading.Thread(target=updateCurrentLogs, args=('QUERY is going to Execute',)).start()  
        response = sf.query(querySOQL)
        print('QUERY response received')
        threading.Thread(target=updateCurrentLogs, args=('QUERY response received',)).start()  
        
        lstRecords = response.get('records')
        print('records fetched')
        threading.Thread(target=updateCurrentLogs, args=('records fetched',)).start()  
        
        nextRecordsUrl = response.get('nextRecordsUrl')

        while not response.get('done'):
            response = sf.query_more(nextRecordsUrl, identifier_is_url=True)
            lstRecords.extend(response.get('records'))
            nextRecordsUrl = response.get('nextRecordsUrl')

        df_records = pd.DataFrame(lstRecords)    
        attachmentIDs = []
        instance_name = sf.sf_instance
        folder_path = '.\Attachments Download'
        if not os.path.exists(os.path.join(folder_path)):
                os.mkdir(os.path.join(folder_path))
                print('creating directory')
                threading.Thread(target=updateCurrentLogs, args=('creating directory',)).start()  
        
        counter = 0
        
        for row in df_records.iterrows():
            noRecords = False
            counter += 1
            print('counter: ' , counter)
            #threading.Thread(target=updateCurrentLogs, args=('QUERY response received',)).start()  
        
            attachment_id = row[1]['Id']
            attachmentIDs.append(attachment_id)            
            record_id = row[1]['ParentId']
            file_name = row[1]['Name']
            print('original',file_name)
            #threading.Thread(target=updateCurrentLogs, args=('QUERY response received',)).start()  
        
            fileSaveName = file_name
            attachment_url = row[1]['Body']
            file_name = file_name.rpartition('2')[0]
            file_name = file_name +  record_id 
        
            print('fileSaveName :  ', fileSaveName )
            threading.Thread(target=updateCurrentLogs, args=('file_name :  '+ fileSaveName,)).start()  
        
            if not os.path.exists(os.path.join(folder_path, record_id)):
                os.mkdir(os.path.join(folder_path, record_id))        
        
            request = sf.session.get('https://{0}{1}'.format(instance_name, attachment_url), headers=sf.headers)
            print('folder_path:  ' ,folder_path )
            print('file_name:  ' ,file_name )   
            with open(os.path.join(folder_path,record_id, fileSaveName), 'wb') as f:
                f.write(request.content)
                f.close()


        print(attachmentIDs)
        #delete records
        deleteRec = False
        if int(var.get()) == 2:
           deleteRec = True
        print('Delete Records:',deleteRec)
        threading.Thread(target=updateCurrentLogs, args=('Delete Records:'+str(deleteRec),)).start()  
        
        if deleteRec == True and len(attachmentIDs)>0:
            recIDs = '('
            for i in range(0,len(attachmentIDs)-1):
                recIDs = recIDs + '\''+attachmentIDs[i]+'\','

            recIDs = recIDs + '\'' +attachmentIDs[len(attachmentIDs)-1]+'\')'
            
            print('Deleting selected records')
            threading.Thread(target=updateCurrentLogs, args=('Deleting selected records',)).start()  
        
            #delete record
            stringAnon = 'delete [SELECT Id FROM Attachment WHERE Id IN'+recIDs+'];'
            print(stringAnon)
            threading.Thread(target=updateCurrentLogs, args=(stringAnon,)).start()  
        
            sf.restful(
                "tooling/executeAnonymous",
                {"anonymousBody": stringAnon},
            )
            #threading.Thread(target=updateCurrentLogs, args=('Done',)).start()  
        
        threading.Thread(target=updateCurrentLogs, args=('',)).start()
        if noRecords== False:           
            loadingLabel.configure(text = 'Done')
        else:
            loadingLabel.configure(text = 'No records To Download/Delete')
    else:
        print('Fields Missing')
        loadingLabel.configure(text = 'Fields Missing')
        #threading.Thread(target=updateCurrentLogs, args=('Fields Missing',)).start()        
    
        
#sf END
def print_values():
    #print(f"The user value is {user_value.get()}")
    #print(f"The pass value is {pass_value.get()}")
    print(var.get(),user_value.get(),pass_value.get(), isSandbox.get())


def sel():
    print(var.get())
    
def sel_2():
    print(isSandbox.get())

def update_progress_label():
    return f"{pb['value']}%"

    
root = Tk()
root.geometry("550x200")
root.maxsize(550, 250)
root.minsize(550, 250)
root.title("Salesforce Attachment Downloader")
frame = Frame(root, borderwidth=3, relief=SUNKEN, bg='red').grid(row=0)
var = IntVar()
var.set(1)

isSandbox = BooleanVar()
isSandbox.set(False)
l1 = Label(frame, text="User email", font="aerial 10 bold").grid(row=0)
l2 = Label(frame, text="Password", font="aerial 10 bold").grid(row=1)
secTok =  Label(frame, text="Security Token", font="aerial 10 bold").grid(row=2)
l3 = Label(frame, text="Attachment Size greater than (Kb) >", font="aerial 10 bold",).grid(row=3)
l4 = Label(frame, text="No. of Attachment Download limit", font="aerial 10 bold").grid(row=4)
rb1 =Radiobutton(frame, text="Download Only", variable=var, value=1,command=sel).grid(row=6, column=0)
rb2 =Radiobutton(frame, text="Download & Delete from SF", variable=var, value=2,command=sel).grid(row=6, column=1)
test_domain =Radiobutton(frame, text="Sandbox", variable=isSandbox, value=True,command=sel_2).grid(row=7, column=0)
prod_domain =Radiobutton(frame, text="Production & Dev Org", variable=isSandbox, value=False,command=sel_2).grid(row=7, column=1)

#variables
user_value = StringVar()
pass_value = StringVar()
security_token_var = StringVar()
attachment_size_var = StringVar()
attachment_limit_var = StringVar()
myService = IntVar()

user_value.set('')
pass_value.set('')
security_token_var.set('')
attachment_size_var.set(0)
attachment_limit_var.set(1)

user_entry = Entry(root, textvariable=user_value, width=50).grid(row=0, column=1)
pass_entry = Entry(root,show='*', textvariable=pass_value, width=50).grid(row=1, column=1)
security_token = Entry(root, textvariable=security_token_var, width=50).grid(row=2, column=1)
attachment_size_entry = Entry(root, textvariable=attachment_size_var).grid(row=3, column=1)
attachment_limit_entry = Entry(root, textvariable=attachment_limit_var).grid(row=4, column=1)

b1 = Button(frame, text="Submit", font="aerial 10 bold", command=sfExecute).grid(row=8,column=0, padx=50)
quitBtn = Button(frame, text="Quit", font="aerial 10 bold", command=root.destroy).grid(row=8,column=1, padx=50)

loadingLabel = Label(frame, text='Click To Run', font="aerial 10 bold")
loadingLabel.grid(row=9)
creditsDesc = Label(frame, text="Developed by Ayush Jain", font="aerial 10 bold").grid(row=9, column=1)
CurrentLogs = Label(frame, text="", font="aerial 10 bold",anchor="center")
CurrentLogs.grid(row=10, column=0)
CurrentLogs.place(anchor = CENTER, relx = 0.5, rely = 0.9)
root.mainloop()
