import tkinter as tk
from tkinter import messagebox,filedialog 
import tkinter.ttk as ttk
import tkinter.font as tkFont
import threading
import socket
from PIL import Image, ImageTk
import PIL
import os

PORT = 5050
HEADER = 64
FORMAT = 'utf-8'


CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
"""SOCKET PART"""
def send(msg):
    
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    try:
        CLIENT.send(send_length)
        CLIENT.send(message)
    except socket.error as e:
        raise socket.error(e)

def receive():
    """Handles receiving of messages."""
    msg = ""
    try:
        msg_length = CLIENT.recv(HEADER).decode(FORMAT)
    except socket.error:
        raise socket.error
    except OSError:  # Possibly client has left the chat.
        raise OSError
    else:
        if msg_length:
            msg = CLIENT.recv(int(msg_length)).decode(FORMAT)  
        return msg   

def start_connect():
    HOST = ip_input.get()
    ADDR = (HOST,PORT)
    try:
        CLIENT.connect(ADDR)
    except socket.error:
        messagebox.showerror("Error","Chưa kết nối đến server")
        return
    else:
        messagebox.showinfo("Status","Kết nối đến server thành công")
        return


"""UI PART"""
def openNewWindow():
    # Toplevel object which will 
    # be treated as a new window
    newWindow = tk.Toplevel(root)
    
    # sets the title of the
    # Toplevel widget
    newWindow.title("New Window")

    return newWindow

def disabledButton(list_buttons):
    for item in list_buttons:
        item['state'] = 'disabled' 

def enabledButton(list_buttons):
    for item in list_buttons:
        item['state'] = 'normal'
             
def process_menu():
    def Xem():
        send("XEM")
        process_list = []
        n = receive()
        n = int(n)
        
        """Nhận process list từ server"""
        for i in range(0,n):
            s1 = receive()
            s2 = receive()
            s3 = receive()
            proc = (s1,s2,s3)
            process_list.append(proc)
        for i in tree.get_children():
            tree.delete(i)
        for item in process_list:
                tree.insert('', 'end', values=item)
                # adjust column's width if necessary to fit each value
                for ix, val in enumerate(item): 
                    col_w = tkFont.Font().measure(val)
                    if tree.column(headers[ix],width=None)<col_w:
                        tree.column(headers[ix], width=col_w)
     
    def kill_form():
        for but in list_of_buttons:
            if but != delete_but:
                but['state'] = 'disabled'
        send("KILL")
        def kill_id():
            send("KILLID")
            send(str(id.get()))
            msg = receive()
            messagebox.showinfo("Status",msg,parent= kill_window)
            return  
        
        def kill_closing():
            send("QUIT")
            for but in list_of_buttons:
                if but != delete_but:
                    but['state'] = 'normal'
            kill_window.destroy()
        kill_window = openNewWindow()

        kill_window.title("KILL")
        id = tk.Entry(kill_window,text = "Kill",width = 40)
        id.delete(0,'end')
        id.insert(tk.END,"Nhập ID")
        id.pack(side = tk.LEFT,pady = (2,2),padx = (5,5))
        
        but = tk.Button(kill_window,text= "Kill",command =lambda : threading.Thread(target =  kill_id).start(),width = 20)
        but.pack(side = tk.LEFT,pady = (2,2),padx = (5,5))
        
        kill_window.protocol("WM_DELETE_WINDOW",kill_closing)
    
    def xoa():
        for i in tree.get_children():
            tree.delete(i)
            
    def start_form():
        for but in list_of_buttons:
            if but != delete_but:
                but['state'] = 'disabled'
        send("START")
        def startID():
            send("STARTID")
            send(id.get())
            msg = receive()
            messagebox.showinfo("Status",msg,parent = start_win)
            return 
        
        def start_closing():
            send("QUIT")
            for but in list_of_buttons:
                if but != delete_but:
                    but['state'] = 'normal'
            start_win.destroy()
        start_win = openNewWindow()
        start_win.title("START")
        
        id = tk.Entry(start_win,text = "Start",width = 40)
        id.delete(0,'end')
        id.insert(tk.END,"Nhập tên")
        id.pack(side = tk.LEFT,pady = (2,2),padx = (5,5))
        
        but = tk.Button(start_win,text= "Start",command = lambda : threading.Thread(target = startID).start(),width = 20)
        but.pack(side = tk.LEFT,pady = (2,2),padx = (5,5))
        
        start_win.protocol("WM_DELETE_WINDOW",start_closing)
        
    def exit():
        send("QUIT")
        enabledButton(list_of_main_but)
        proc_window.destroy()
        
    proc_window = openNewWindow()
    proc_window.title("Process")
    proc_window.geometry("600x600")
    process_but['state'] = 'disabled'
    list_but = tk.Frame(proc_window)
    list_but.pack(pady = 10)
    kill_but = tk.Button(list_but,text="Kill",width= 5,height=2,command = kill_form)
    kill_but.grid(row= 0,column = 0,padx = 10)
    
    watch_but = tk.Button(list_but,text= "Xem",width= 5,height=2,command =lambda : threading.Thread(target = Xem).start())
    watch_but.grid(row= 0,column = 1,padx = 10)
    
    delete_but = tk.Button(list_but,text="Xoá",width= 5,height=2,command = xoa)
    delete_but.grid(row= 0,column = 2,padx = 10)
    
    start_but = tk.Button(list_but,text = "Start",width= 5,height=2,command= start_form)
    start_but.grid(row= 0,column = 3,padx = 10)
    
    list_of_buttons = [kill_but,watch_but,delete_but,start_but]
    
    container = ttk.Frame(proc_window)
    container.pack(fill='both', expand=True)
    headers = ['Name Process' , 'ID Process' , 'Count Threads']
    tree = ttk.Treeview(proc_window,columns=headers, show="headings")
    vsb = ttk.Scrollbar(proc_window,orient="vertical",
        command=tree.yview)
    hsb = ttk.Scrollbar(proc_window,orient="horizontal",
        command=tree.xview)
    tree.configure(yscrollcommand=vsb.set,
        xscrollcommand=hsb.set)
    tree.grid(column=0, row=0, sticky='nsew', in_=container)
    vsb.grid(column=1, row=0, sticky='ns', in_=container)
    hsb.grid(column=0, row=1, sticky='ew', in_=container)
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(0, weight=1)
    
    for col in headers:
        tree.heading(col, text=col.title(),
            command=lambda c=col: sortby(tree, c, 0))
        # adjust the column's width to the header string
        tree.column(col,
            width=tkFont.Font().measure(col.title()))   
    
    proc_window.protocol("WM_DELETE_WINDOW",exit)       
  
def app_menu():
    def Xem(): 
        send("XEM")
        process_list = []
        n = receive()
        n = int(n)
        
        for i in range(0,n):
            s1 = receive()
            s2 = receive()
            s3 = receive()
            proc = (s1,s2,s3)
            process_list.append(proc)
            
        for i in tree.get_children():
            tree.delete(i)
            
        for item in process_list:
                tree.insert('', 'end', values=item)
                # adjust column's width if necessary to fit each value
                for ix, val in enumerate(item): 
                    col_w = tkFont.Font().measure(val)
                    if tree.column(headers[ix],width=None)<col_w:
                        tree.column(headers[ix], width=col_w)
                        
    def kill_form():
        for but in list_of_buttons:
            if but != delete_but:
                but['state'] = 'disabled'
        send("KILL")
        def kill_id():
            send("KILLID")
            send(str(id.get()))
            msg = receive()
            messagebox.showinfo("Status",msg,parent= kill_window)
            return  
        
        def kill_closing():
            send("QUIT")
            for but in list_of_buttons:
                if but != delete_but:
                    but['state'] = 'normal'
            kill_window.destroy()
        kill_window = openNewWindow()

        kill_window.title("KILL")
        id = tk.Entry(kill_window,text = "Kill",width = 40)
        
        id.delete(0,'end')
        id.insert(tk.END,"Nhập ID")
        id.pack(side = tk.LEFT,pady = (2,2),padx = (5,5))
        
        but = tk.Button(kill_window,text= "Kill",command =lambda : threading.Thread(target = kill_id).start(),width = 20)
        but.pack(side = tk.LEFT,pady = (2,2),padx = (5,5))
        
        kill_window.protocol("WM_DELETE_WINDOW",kill_closing)
    
    def xoa():
        for i in tree.get_children():
            tree.delete(i)
            
    def start_form():
        for but in list_of_buttons:
                if but != delete_but:
                    but['state'] = 'disabled'
        send("START")
        def startID():
            send("STARTID")
            send(id.get())
            msg = receive()
            messagebox.showinfo("Status",msg,parent = start_win)
            return 
        
        def start_closing():
            send("QUIT")
            for but in list_of_buttons:
                if but != delete_but:
                    but['state'] = 'normal'
            start_win.destroy()
        start_win = openNewWindow()
        start_win.title("START")
        
        id = tk.Entry(start_win,text = "Start",width = 40)
        id.delete(0,'end')
        id.insert(tk.END,"Nhập tên")
        id.pack(side = tk.LEFT,pady = (2,2),padx = (5,5))
        
        but = tk.Button(start_win,text= "Start",command = lambda : threading.Thread(target = startID).start(),width = 20)
        but.pack(side = tk.LEFT,pady = (2,2),padx = (5,5))
        
        start_win.protocol("WM_DELETE_WINDOW",start_closing)
        
    def exit():
        send("QUIT")    
        enabledButton(list_of_main_but)
        app_window.destroy()
        
    app_window = openNewWindow()
    app_window.title("List App")
    app_window.geometry("600x600")
    app_but['state'] = 'disabled'
    list_but = tk.Frame(app_window)
    list_but.pack(pady = 10)
    kill_but = tk.Button(list_but,text="Kill",width= 5,height=2,command = kill_form)
    kill_but.grid(row= 0,column = 0,padx = 10)
    
    watch_but = tk.Button(list_but,text= "Xem",width= 5,height=2,command =lambda : threading.Thread(target = Xem).start())
    watch_but.grid(row= 0,column = 1,padx = 10)
    
    delete_but = tk.Button(list_but,text="Xoá",width= 5,height=2,command = xoa)
    delete_but.grid(row= 0,column = 2,padx = 10)
    
    start_but = tk.Button(list_but,text = "Start",width= 5,height=2,command= start_form)
    start_but.grid(row= 0,column = 3,padx = 10)
    
    list_of_buttons = [kill_but,watch_but,delete_but,start_but]
    
    container = ttk.Frame(app_window)
    container.pack(fill='both', expand=True)
    headers = ['Name Process' , 'ID Process' , 'Count Threads']
    tree = ttk.Treeview(app_window,columns=headers, show="headings")
    vsb = ttk.Scrollbar(app_window,orient="vertical",
        command=tree.yview)
    hsb = ttk.Scrollbar(app_window,orient="horizontal",
        command=tree.xview)
    tree.configure(yscrollcommand=vsb.set,
        xscrollcommand=hsb.set)
    tree.grid(column=0, row=0, sticky='nsew', in_=container)
    vsb.grid(column=1, row=0, sticky='ns', in_=container)
    hsb.grid(column=0, row=1, sticky='ew', in_=container)
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(0, weight=1)
    
    for col in headers:
        tree.heading(col, text=col.title(),
            command=lambda c=col: sortby(tree, c, 0))
        # adjust the column's width to the header string
        tree.column(col,
            width=tkFont.Font().measure(col.title()))   
    
    app_window.protocol("WM_DELETE_WINDOW",exit)
    
def keylog_menu():
    def hook():
        send("HOOK")
    def unHook():
        send("UNHOOK")
    def printKeys():
        send("PRINT")
        text_box['state'] = 'normal'
        s = receive()
        if s != "":
            text_box.insert(tk.INSERT,s)
        text_box['state'] = 'disabled'
    def xoa():
        text_box['state'] = 'normal'
        text_box.delete('1.0',tk.END)
        text_box['state'] = 'disabled'
        
    def exit():
        send("QUIT")
        enabledButton(list_of_main_but)
        keylog_window.destroy()
    keylog_window = openNewWindow()
    keylog_window.title("Key strokes")
    keylog_window.geometry("400x300")
    
    hook_button =tk.Button(keylog_window,text= "Hook",command = hook)
    hook_button.place(
        x = 20,y=15,
        width = 82.5,height = 50
    )
    
    unhook_button = tk.Button(keylog_window,text= "Unhook",command = unHook)
    unhook_button.place(
         x = 112.5,y=15,
        width = 82.5,height = 50
    )
    
    print_button = tk.Button(keylog_window,text= "In phím",command = printKeys)
    print_button.place(
         x = 205,y=15,
        width = 82.5,height = 50
    )
    
    delete_button = tk.Button(keylog_window,text= "Xoá",command = xoa)
    delete_button.place(
         x = 297.5,y=15,
        width = 82.5,height = 50
    )
    
    text_box = tk.Text(keylog_window)
    text_box.place(
        x = 20,y=75,
        width = 360,height = 210
    )

    text_box['state']= 'disabled'
    
    keylog_window.protocol("WM_DELETE_WINDOW",exit)
    return

def screen_shot_menu():
    def take_pic():
        send("TAKE")
        global img_save
        length_img = receive()
        length_img = int(length_img)
        
        img_size = receive()
        img_size = eval(img_size)
        
        img_mode = receive()
        
        img = CLIENT.recv(length_img)  
        img = Image.frombytes(img_mode,img_size,img)
        img = img.resize((600,400), Image.ANTIALIAS)
        img_save = img
        pic = ImageTk.PhotoImage(img)
        img_label = tk.Label(screen_shot_window,image=pic)
        img_label.image = pic
        img_label.place(x=25, y=25)
    
    def save():
        global img_save
        if img_save:
            file_path = filedialog.asksaveasfilename(defaultextension='.bmp')    
            if file_path:
                img_save.save(file_path)
                messagebox.showinfo("Success","Image is saved successfully!",parent=screen_shot_window) 
            else:
                messagebox.showwarning("Cancel","Image is not saved!",parent=screen_shot_window) 
        else:
            messagebox.showerror("Error","No screenshot has taken!",parent=screen_shot_window)
    def exit():
        send("QUIT")
        enabledButton(list_of_main_but)
        screen_shot_window.destroy()
    screen_shot_window = openNewWindow()
    screen_shot_window.title("Pic")
    screen_shot_window.geometry("720x450")
    global img_save
    img_save = ""
    screen_shot_button = tk.Button(screen_shot_window,text= "Chụp",command= take_pic)
    screen_shot_button.place(x = 620 + 10,y = 25,
                             height = 250,width = 80)
   
    save_button = tk.Button(screen_shot_window,text="Save",command= save)
    save_button.place(x = 620 + 10,y = 25+ 250 + 30,
                             height = 120,width = 80)

    screen_shot_window.protocol("WM_DELETE_WINDOW",exit)
    return  

def button_process_clicked():
    if len(str(CLIENT).split()) < 9:
        messagebox.showerror("Error","Chưa kết nối đến server")
        return 
    send("PROCESS")  
    disabledButton(list_of_main_but)
    process_menu()

def app_but_clicked():
    if len(str(CLIENT).split()) < 9:
        messagebox.showerror("Error","Chưa kết nối đến server")
        return 
    send("APPLICATION")  
    disabledButton(list_of_main_but)
    app_menu()

def screen_shot_but_clicked():
    if len(str(CLIENT).split()) < 9:
        messagebox.showerror("Error","Chưa kết nối đến server")
        return 
    send("TAKEPIC")  
    disabledButton(list_of_main_but)    
    screen_shot_menu()

def keylog_but_clicked():
    if len(str(CLIENT).split()) < 9:
        messagebox.showerror("Error","Chưa kết nối đến server")
        return 
    send("KEYLOG")  
    disabledButton(list_of_main_but)    
    keylog_menu()
    
def root_closing():
    if len(str(CLIENT).split()) == 9:
        try:
            send("QUIT")
        finally:
            CLIENT.close()
    root.destroy()
       
    
root = tk.Tk()
root.title("CLIENT")
root.geometry("450x300")

ip_input = tk.Entry(root,
                text= "HOST",
                width = 20
                )
ip_input.insert(tk.END,"Nhập IP")
ip_input.bind("<Return>",lambda args : threading.Thread(target=start_connect).start())
ip_input.place(
    x =10,y =20,
    width = 300,
    height =30)
enter = tk.Button(root,
            text= "Kết nối",
            command=lambda : threading.Thread(target=start_connect).start()
            )
enter.place(x =300+10+10,y =20,
            width = 70 + 50,
            height =30
            )

process_but = tk.Button(root,
                    text= "Process Running",
                    command= button_process_clicked,
                    )
process_but.place(
    x =10,y =30+20+10,
    width = 100,
    height =220
    )

app_but = tk.Button(root,
                text= "App Running",
                command= app_but_clicked,
                )
app_but.place(
            x =100+10+5,y =30+20+10,
            width = 300 - 100 - 5,
            height =70
            )

shutdown_but = tk.Button(root,
                    text = "Tắt máy",
                    command =None
                    )
shutdown_but.place(
                x =100+10+5,y =30+20+10+75,
                width = 58,
                height =70
                )

screen_but = tk.Button(root,
                    text = "Chụp màn hình", 
                    command = screen_shot_but_clicked)

screen_but.place(
            x =100+10+5 + 58 + 5,y =30+20+10+75,
            width = 132,
            height =70 
            )


reg_but = tk.Button(root,
                text= "Sửa Registry",
                command = None)

reg_but.place(
            x =100+10+5,y =30+20+10+75+75,
            width = 300 - 100 - 5 + 60,
            height =70
            )

keystroke_but = tk.Button(root,
                text= "Keystroke",
                command = keylog_but_clicked)

keystroke_but.place(
            x =100+10+10+5+300 - 100 - 5,y =30+20+10,
            width = 70 + 50,
            height =70 + 75
            )

exit_but = tk.Button(root,
                text = "Thoát",
                command = None)

exit_but.place(
            x =100+10+10+5+300-100 -5 + 60,y =30+20+10 + 75*2,
            width = (70 + 50) / 2,
            height =70
)
list_of_main_but = [app_but,process_but,shutdown_but,screen_but,keystroke_but,reg_but,exit_but]
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", root_closing)
root.mainloop()