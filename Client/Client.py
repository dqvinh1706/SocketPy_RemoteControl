import tkinter as tk
from tkinter import messagebox,filedialog 
import tkinter.ttk as ttk
import tkinter.font as tkFont
from PIL import Image, ImageTk
import PIL

import threading
import socket

import os
import codecs
import sys

PORT = 5050
HEADER = 64
FORMAT = 'utf-8'

CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
"""SOCKET PART"""

"""Hàm gửi dữ liệu qua SERVER"""
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
    
"""Hàm nhận dữ liệu từ SERVER"""
def receive():
    msg = ""
    try:
        msg_length = CLIENT.recv(HEADER).decode(FORMAT)
    except socket.error:
        raise socket.error
    except OSError:
        raise OSError
    else:
        if msg_length:
            msg = CLIENT.recv(int(msg_length)).decode(FORMAT)  
        return msg   

"""Hàm bắt đầu kết nối đến SERVER"""
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

"""Hàm mở cửa sổ mới"""
def openNewWindow():
    newWindow = tk.Toplevel(root)
    
    newWindow.title("New Window")

    return newWindow

"""Tắt các nút bấm"""
def disabledButton(list_buttons):
    for item in list_buttons:
        item['state'] = 'disabled' 

"""Bật các nút bấm"""
def enabledButton(list_buttons):
    for item in list_buttons:
        item['state'] = 'normal'
 
"""Giao diện của process running"""             
def process_menu():
    """Hàm xem process list"""
    def Xem():
        """Gửi lệnh XEM"""
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
    
    """Giao diện của diệt process""" 
    def kill_form():
        for but in list_of_buttons:
            if but != delete_but:
                but['state'] = 'disabled'
                
        send("KILL")
        
        """Hàm diệt process theo ID"""
        def kill_id():
            """Gửi lệnh KILLID và ID của process qua SERVER"""
            send("KILLID")
            send(str(id.get()))
            
            """Nhận thông báo từ SERVER"""
            msg = receive()
            messagebox.showinfo("Status",msg,parent= kill_window)  
        
        """Hàm tắt cửa sổ kill"""
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
    
    """Hàm xoá bảng"""
    def xoa():
        for i in tree.get_children():
            tree.delete(i)
    
    """Hàm giao diện của bắt đầu process"""        
    def start_form():
        for but in list_of_buttons:
            if but != delete_but:
                but['state'] = 'disabled'
                
        send("START")
        
        """Hàm để bắt đầu chương trình theo tên"""
        def startID():
            """Gửi lệnh STARTID và tên của app"""
            send("STARTID")
            send(id.get())
            
            """Nhận thông báo từ SERVER"""
            msg = receive()
            messagebox.showinfo("Status",msg,parent = start_win)
            return 
        
        """Hàm tắt cửa sổ của bắt đầu process"""
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
    
    """Hàm tắt cửa sổ của process running"""    
    def exit():
        send("QUIT")
        enabledButton(list_of_main_but)
        proc_window.destroy()
        
    proc_window = openNewWindow()
    proc_window.title("Process")
    proc_window.geometry("600x600")
    
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
        tree.heading(col, text=col.title())
        # adjust the column's width to the header string
        tree.column(col,
            width=tkFont.Font().measure(col.title()))   
    
    proc_window.protocol("WM_DELETE_WINDOW",exit)       

"""Menu giao diện của App Running"""  
def app_menu():
    """Hàm để xem app running""" 
    def Xem(): 
        """Gửi lệnh XEM"""
        send("XEM")
        process_list = []
        n = receive()
        n = int(n)
        
        """Nhận danh sách cách app"""
        for i in range(0,n):
            s1 = receive()
            s2 = receive()
            s3 = receive()
            proc = (s1,s2,s3)
            process_list.append(proc)
            
        for i in tree.get_children():
            tree.delete(i)
         
        """Hiện lên bảng"""    
        for item in process_list:
                tree.insert('', 'end', values=item)
                # adjust column's width if necessary to fit each value
                for ix, val in enumerate(item): 
                    col_w = tkFont.Font().measure(val)
                    if tree.column(headers[ix],width=None)<col_w:
                        tree.column(headers[ix], width=col_w)
    
    """Giao diện của diệt app"""                    
    def kill_form():
        for but in list_of_buttons:
            if but != delete_but:
                but['state'] = 'disabled'
                
        send("KILL")
        """Hàm để tắt app theo ID"""
        def kill_id():
            """Gửi lệnh KILLID và ID của app qua SERVER"""
            send("KILLID")
            send(str(id.get()))
            
            """Nhận thông báo từ client"""
            msg = receive()
            messagebox.showinfo("Status",msg,parent= kill_window)
            return  
        
        """Hàm đóng cửa sổ kill app"""
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
    
    """Hàm để xoá bảng"""
    def xoa():
        for i in tree.get_children():
            tree.delete(i)
    
    """Giao diện của bắt đầu app"""        
    def start_form():
        for but in list_of_buttons:
                if but != delete_but:
                    but['state'] = 'disabled'
                    
        """Gửi lệnh START qua SERVER"""            
        send("START")
        
        """Hàm để bắt đầu chương trình theo tên"""
        def startID():
            """Gửi lệnh STARTID và tên của app"""
            send("STARTID")
            send(id.get())
            
            """Nhận thông báo từ SERVER"""
            msg = receive()
            messagebox.showinfo("Status",msg,parent = start_win)
            return 
        
        """Hàm thoát cửa sổ app running"""
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
        tree.heading(col, text=col.title())
        # adjust the column's width to the header string
        tree.column(col,
            width=tkFont.Font().measure(col.title()))   
    
    app_window.protocol("WM_DELETE_WINDOW",exit)

"""Menu giao diện của keystroke"""    
def keylog_menu():
    """Hàm gửi lệnh hook qua SERVER"""
    def hook():
        send("HOOK")
        
    """Hàm gửi lệnh unhook qua SERVER"""
    def unHook():
        send("UNHOOK")
        
    """Hàm gửi lệnh in phím qua SERVER và nhận chuỗi phím"""
    def printKeys():
        send("PRINT")
        text_box['state'] = 'normal'
        
        """Nhận chuỗi phím lưu vào s"""
        s = receive()
        if s != "":
            """Hiện s lên màn hình"""
            text_box.insert(tk.INSERT,s)
        text_box['state'] = 'disabled'
    
    """Hàm để xoá"""
    def xoa():
        text_box['state'] = 'normal'
        text_box.delete('1.0',tk.END)
        text_box['state'] = 'disabled'
    
    """Hàm để thoát keystroke"""    
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

"""Menu giao diện của chức năng chụp màn hình"""
def screen_shot_menu():
    """Hàm gửi yêu cầu và nhận hình từ SERVER"""
    def take_pic():
        send("TAKE")
        global img_save
        length_img = receive()
        length_img = int(length_img)
        print(length_img)
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
    
    """Hàm để lưu hình ảnh"""
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
    
    """Hàm khi nút thoát(X) được bấm """
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

"""Menu giao diện registry"""
def registry_menu():
    """Mở đọc file .reg bằng đường dẫn"""
    def open_reg():
        global linkPath
        filename = filedialog.askopenfilename(
            parent = registry_window,
            title="Open a file", 
            filetypes=(("reg file", "*.reg"), ("all files", "*.*"))
        )
        if filename:
            linkPath = filename
            link_entry.delete(0, tk.END)
            link_entry.insert(tk.END, linkPath)
            try:
                with codecs.open(linkPath, encoding='utf-16') as myfile:
                    data = myfile.read()
            except NameError:
                return
            else:    
                text_reg.delete(1.0, tk.END)
                text_reg.insert('1.0', data)
        else:
            messagebox.showerror("File","File is not chosen")
    
    """Gửi yêu cầu và nội dung chỉnh sửa qua SERVER"""        
    def open_reg_file_to_text():
        send("REG")
        send(str(text_reg.get(1.0,'end')))
        
        msg = receive()
        messagebox.showinfo("Status",msg,parent =registry_window)

    """Gửi lệnh SEND qua SERVER và nhận kết quả từ SERVER"""
    def send_registry():
        """Gửi yêu cầu và dữ liệu cho SERVER"""
        send("SEND")
        
        s = str(selection.get()) 
        send(s)
        
        s = str(choose_path.get())
        send(s)
        
        s = str(name_value.get())
        send(s)
        
        s = str(value.get())
        send(s)
        
        s = str(type.get())
        send(s) 
        
        s = receive()
        insert_to_text_box(s)
        
    """Giao diện để người dùng nhập"""
    def get_value_form():
        name_value.place(x = 5, y = 35 + 25 + 5, width = 130, height = 25)
        value.place_forget()
        type.place_forget()

    def set_value():
        name_value.place(x = 5, y = 35 + 25 + 5, width = 130, height = 25)
        value.place(x = 5 + 130 + 5, y = 35 + 25 + 5, width = 155, height = 25)
        type.place(x = 5 + 130 + 5 + 155 + 5, y = 35 + 25 + 5, width = 130, height = 25)

    def create_key_form():
        name_value.place_forget()
        value.place_forget()
        type.place_forget()
        
    def selected(): 
        selected_option = str(selection.get())  
        if selected_option == "Get value":
            get_value_form()
        elif selected_option == "Set value":
            set_value()
        elif selected_option == "Delete value":
            get_value_form()
        elif selected_option == "Create key":
            create_key_form()
        elif selected_option == "Delete key":
            create_key_form()

    """Điền giá trị vào text box"""
    def insert_to_text_box(s):
        value_text['state'] = 'normal'
        value_text.insert(tk.INSERT,s + "\n")
        value_text['state'] = 'disabled'
    """Xoá chữ trong ô text"""    
    def xoa():
        value_text['state'] = 'normal'
        value_text.delete(1.0, tk.END)
        value_text['state'] = 'disabled'
        
    """Hàm thoát cửa sổ"""    
    def exit():
        send("QUIT")
        enabledButton(list_of_main_but)
        registry_window.destroy()
            
    registry_window = openNewWindow()
    registry_window.title("Registry")
    registry_window.geometry("480x420")
    
    but = tk.Button(registry_window, text ="Browser", command=open_reg)
    but.place(x = 360, y = 17, width = 100, height = 30)

    reg = tk.StringVar()
    text_reg = tk.Text(registry_window)
    text_reg.config(font=("Calibri", 9))
    text_reg.place(x = 20, y = 60, width = 320, height = 90)

    link_entry = tk.Entry(registry_window)
    link_entry.insert(tk.END, "Nhập đường dẫn")
    link_entry.place(x = 20, y = 20, width = 320, height = 25)
    
    reg_to_text_button = tk.Button(registry_window, text="Gửi nội dung", command=open_reg_file_to_text)
    reg_to_text_button.place(x = 360, y = 60, width = 100, height = 50)

    Frame_Options = tk.LabelFrame(registry_window, text="Sửa giá trị trực tiếp")
    Frame_Options.place(x = 20, y = 165,width = 440,height =240)
        
    options1 = [
        "Get value",
        "Set value",
        "Delete value",
        "Create key",
        "Delete key"
    ]

    options2 = [
        "String",
        "Binary",
        "DWORD",
        "QWORD",
        "Multi-string",
        "Expandable String"
    ]

    selection = ttk.Combobox(Frame_Options, value=options1)
    selection.insert(0, "Chọn chức năng")
    selection.bind("<<ComboboxSelected>>",(lambda event: selected()))
    selection.place(x = 5, y = 5, width = 425, height = 25)

    choose_path = tk.Entry(Frame_Options)
    choose_path.insert(0, "Đường dẫn")
    choose_path.place(x = 5, y = 35, width = 425, height = 25)

    name_value = tk.Entry(Frame_Options)
    name_value.insert(0, "Name value")
    name_value.place(x = 5, y = 35 + 25 + 5, width = 130, height = 25)

    value = tk.Entry(Frame_Options)
    value.insert(0, "Value")
    value.place(x = 5 + 130 + 5, y = 35 + 25 + 5, width = 155, height = 25)

    type = ttk.Combobox(Frame_Options, value=options2)
    type.insert(0, "Kiểu dữ liệu")
    type.place(x = 5 + 130 + 5 + 155 + 5, y = 35 + 25 + 5, width = 130, height = 25)

    value_text = tk.Text(Frame_Options)
    value_text['state'] = 'disabled'
    value_text.config(font=("Calibri", 9))
    value_text.place(x = 5,y = 35 + 25 + 5 + 25 + 5, width = 425, height =90)
    
    send_button = tk.Button(Frame_Options, text = "Gửi",command = send_registry)
    send_button.place(x = 100, y = 35 + 25 + 5 + 25 + 5 + 90 + 5, width = 110, height = 25)

    del_button = tk.Button(Frame_Options, text = "Xóa",command = xoa)
    del_button.place(x = 160 + 5 + 50, y = 35 + 25 + 5 + 25 + 5 + 90 + 5, width = 120, height = 25)

    registry_window.resizable(False, False)
    registry_window.protocol("WM_DELETE_WINDOW",exit)

"""Hàm xử lí khi nút Process Running được bấm"""
def button_process_clicked():
    if len(str(CLIENT).split()) < 9:
        messagebox.showerror("Error","Chưa kết nối đến server")
        return 
    send("PROCESS")  
    disabledButton(list_of_main_but)
    process_menu()

"""Hàm xử lí khi nút App Running được bấm"""
def app_but_clicked():
    if len(str(CLIENT).split()) < 9:
        messagebox.showerror("Error","Chưa kết nối đến server")
        return 
    send("APPLICATION")  
    disabledButton(list_of_main_but)
    app_menu()
    
"""Hàm xử lí khi nút Chụp màn hình được bấm"""    
def screen_shot_but_clicked():
    if len(str(CLIENT).split()) < 9:
        messagebox.showerror("Error","Chưa kết nối đến server")
        return 
    send("TAKEPIC")  
    disabledButton(list_of_main_but)    
    screen_shot_menu()

"""Hàm xử lí khi nút KeyStroke được bấm"""    
def keylog_but_clicked():
    if len(str(CLIENT).split()) < 9:
        messagebox.showerror("Error","Chưa kết nối đến server")
        return 
    send("KEYLOG")  
    disabledButton(list_of_main_but)    
    keylog_menu()
    
"""Hàm xử lí khi nút Tắt máy được bấm"""        
def shutdown_but_clicked():
    if len(str(CLIENT).split()) < 9:
        messagebox.showerror("Error","Chưa kết nối đến server")
        return
    send("SHUTDOWN")
    CLIENT.close()

"""Hàm xử lí khi nút thoát được bấm"""    
def exit_but_clicked(): 
    try:
        send("QUIT") 
    finally:
        root.destroy()
        sys.exit()

"""Hàm xử lí khi nút Registry được bấm"""
def reg_but_clicked(): 
    if len(str(CLIENT).split()) < 9:
        messagebox.showerror("Error","Chưa kết nối đến server")
        return 
    send("REGISTRY") 
    disabledButton(list_of_main_but)   
    registry_menu()

"""Nút thoát(X) của cửa số chương trình"""    
def root_closing():
    if len(str(CLIENT).split()) == 9:
        try:
            send("QUIT")
        finally:
            CLIENT.close()
    root.destroy()
       
"""Menu chính"""    
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
                    command =shutdown_but_clicked
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
                command = reg_but_clicked)

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
                command = exit_but_clicked)

exit_but.place(
            x =100+10+10+5+300-100 -5 + 60,y =30+20+10 + 75*2,
            width = (70 + 50) / 2,
            height =70
)
list_of_main_but = [app_but,process_but,shutdown_but,screen_but,keystroke_but,reg_but,exit_but]
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", root_closing)

root.mainloop()