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
DIR = os.getcwd()

"""Tạo socket SERVER"""
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

"""Gửi dữ liệu qua client"""
def send(client,msg):
    """Gửi dữ liệu thành 2 phần: Độ dài của dữ liệu và dữ liệu"""
    """Mã hoá dữ liệu với format là utf_8"""
    message = msg.encode(FORMAT)
    """Lấy độ dài của dữ liệu"""
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    try:
        """Gửi độ dài dài của dữ liệu"""
        client.send(send_length)
        
        """Gửi dữ liệu đi"""
        client.send(message)
    except socket.error:
        raise socket.error

"""Hàm nhận dữ liệu từ client"""
def receive(conn):
    """Nhận theo protocol là nhận độ dài của dữ liệu trước 64 bytes"""
    """Sau đó nhận dữ liệu dựa trên độ dài vừa nhận""" 
    msg = ""
    try:
        """Nhận độ dài dữ liệu"""
        msg_length = conn.recv(HEADER).decode(FORMAT)
    except socket.error:
        return "QUIT"
    else:   
        if msg_length:
            msg_length = int(msg_length)
            """Nhận dữ liệu theo đúng độ dài đã nhận"""
            msg = conn.recv(msg_length).decode(FORMAT)
        return msg    
    
"""Hàm xử lí yêu cầu process running của client"""  
def process_menu(conn):
    """Hàm để xem process đang chạy của server"""
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
    
    """Hàm để diệt 1 process bằng ID"""    
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
            
        while True:
            msg = receive(conn) 
            if msg == "QUIT":
               break
            else:
                killID(conn) 
    """Hàm để bắt đầu 1 process bằng tên"""
    def start(conn):
        while True:
            msg = receive(conn)
            if msg=="QUIT":
                break 
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
    
    """Hàm nhận và xử lí yêu cầu của client"""        
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

"""Hàm xử lí yêu cầu app running"""
def application_menu(conn):
    """Hàm để xem app đang chạy của server"""
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
        
        """Gửi trả danh sách các chương trình đang chạy cho client"""
        send(conn,str(countProcess - 2))
        for proc in list_process:
            name = proc['name']
            send(conn,name)
            id = proc['pid']
            send(conn,str(id))
            threads = proc['num_threads']
            send(conn,str(threads))
            
    """Hàm để diệt app của server"""    
    def kill(conn):
        """Hàm diệt theo ID"""
        def killID(conn):
            """Nhận app ID từ client"""
            msg = receive(conn)
            success = False
            if msg:
                """Tìm app trong tất cả process bằng ID"""
                for proc in psutil.process_iter():
                    """Nếu tìm thấy chương trình thì sẽ diệt chương trình"""
                    if str(proc.pid) == msg:
                        try:
                            """Diệt thành công thì gửi trả thông báo"""
                            proc.kill()
                            send(conn,"Đã diệt Process")
                        except psutil.Error:
                            send(conn,"Lỗi")
                        else:
                            success = True
                            break
                        
            """Không tìm thấy chương trình thì gửi thông báo cho client"""
            if success == False:
                send(conn,"Không tìm thấy chương trình")
                return 
            
        """Hàm xử lí yêu cầu của client để diệt app"""    
        
        while True:
            msg = receive(conn) 
            if msg == "QUIT":
                break
            else:
                killID(conn)

    """Hàm để bắt đầu 1 app bằng tên"""
    def start(conn):
        while True:
            msg = receive(conn)
            if msg=="QUIT":
                break
            elif msg == "STARTID":
                name = receive(conn) 
                if name: 
                    name+=".exe"
                    try:
                        """Nếu bật thành công thì gửi thông báo tới client"""
                        Popen([name],creationflags=CREATE_NEW_CONSOLE)
                        send(conn,"Process đã được bật")
                    except:
                        send(conn,"Lỗi") 
                else:        
                    send(conn,"Lỗi") 
                    
                    
    """Hàm xử lí yêu cầu của client"""                
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

"""Hàm xử lí keystroke của server"""
def key_log(conn):
    """Hàm bắt sự kiện bàn phím ghi vào file keyLog.txt"""
    def get_keys(stop):
        def writeFile(key):
            with open(DIR + "\keyLog.txt","a") as f:
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
    
    """Hàm in phím gửi các phím đã bấm qua cho client"""       
    def printKeys(conn):
        with open(DIR + "\keyLog.txt","r") as file:
            s = file.read()
        with open(DIR + "\keyLog.txt","w") as file:
            file.write("")
        if s == "":
            s = "\0"
        """Đọc từ file keyLog.txt lưu vào biến s gửi qua cho client"""
        send(conn, s)
    
    """Hàm bắt đầu hook key: Tạo 1 luồng mới để bắt sự kiện"""          
    def hookKey():
        global stop_threads,t
        stop_threads = False
        t = threading.Thread(target= get_keys,args=(lambda : stop_threads, ))
        t.start()
        with open(DIR + "\keyLog.txt","w") as f:
            f.write("")
    
    """Hàm tắt hook key: Huỷ luồng mà hook key tạo ra"""    
    def unHook():   
        global stop_threads
        stop_threads = True
        t.join() 
        with open(DIR + "\keyLog.txt","w") as f:
            f.write("")
    
    """Nhận yêu cầu từ client và xử lí"""
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

"""Hàm chụp màn hình"""
def takeScreenshot(conn):
    """Chụp màn hình"""
    img = pyautogui.screenshot()
    
    """Lấy độ dài của bytes hình ảnh"""
    length_img = len(img.tobytes())
    
    """Gửi lần lượt độ dài bytes, kích thước, với chế độ của hình ảnh cho client"""
    send(conn,str(length_img))
    send(conn,str(img.size))
    send(conn,str(img.mode))
    
    """Gửi toàn bộ bytes hình ảnh qua cho client"""
    conn.send(img.tobytes())
  

"""Hàm xử lí yếu cầu chụp màn hình của server"""
def take_pic(conn):
    while True:
        ss = receive(conn)
        if ss == "TAKE":
            takeScreenshot(conn)
        elif ss == "QUIT":
            return

"""Hàm tắt máy của server"""
def shutdown(conn): 
    os.system("shutdown /s /t 5")

"""Hàm xử lí yếu cầu của client tham số là 1 socket type"""
def handle_client(conn):
    while True:
        msg = receive(conn)
        print(msg)
        if msg == "KEYLOG":
            key_log(conn)
        elif msg == "SHUTDOWN":
            shutdown(conn)
            break
        elif msg == "REGISTRY":
            #registry()
            pass
        elif msg == "TAKEPIC":
            take_pic(conn)
        elif msg == "PROCESS":
            process_menu(conn)
        elif msg == "APPLICATION":
            application_menu(conn)
        elif msg == "QUIT":
            conn.close()
            break


"""Mở SERVER và nhận kết nối của client"""    
def accept_incoming_connections():
    try:
        SERVER.bind(ADDR)
        SERVER.listen(5)
        print(f"Listen on {HOST}")
        conn,addr = SERVER.accept()
    except socket.error:
        return
    else:  
        handle_client(conn)
 
def on_closing():
    if SERVER.fileno() != -1:
        SERVER.close()      
    root.destroy()  

"""Giao diện"""    
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
root.mainloop()


    

