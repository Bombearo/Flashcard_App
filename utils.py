from string import ascii_letters, digits
import mysql.connector
import tkinter as tk
from tkinter import ttk

appdb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database ='app'
)
mycursor = appdb.cursor()

def validate_username(username):
    errors = {}
    length = len(username)
    if length <= 2 or length > 20:
        errors['length'] = 'Your Username must be more than 2 characters and less than 20 characters'
    if not username.isalnum():
        chars = [char for char in username if not char.isalnum()]
        errors['invalid'] = f"{','.join(set(chars))} are not accepted character(s). Please only use alphanumeric characters (letters and numbers) in your username"
    return errors
    


def validate_password(password):
    errors = {}
    if len(password) < 4:
        errors['length'] = 'Your password must be 4 characters or longer'
    if password.isalnum():
        if not any(char for char in password if char.islower()):
            errors['lower'] = 'Your password must contain at least one lowercase letter'
        if not any(char for char in password if char.isupper()):
            errors['upper'] = 'Your password must contain at least one uppercase letter'
        if not any(char for char in password if char.isdigit()):
            errors['number'] = 'Your password must contain at least one digit'
    else:
        symbols = [char for char in password if not char.isalnum()]
        errors['invalid'] = f"{','.join(set(symbols))} are not accepted character(s). Please only use alphanumeric characters (letters and numbers) in your username"
    return errors

def createUserFrame(FrameClass,name,parent,controller,user,errors = []):
    frame = FrameClass(parent = parent, controller = controller, user = user, errors = errors)
    controller.frames[name] = frame
    frame.grid(row=0, column=0, sticky="nsew")


def get_attribute(val,attribute):
    if attribute == 'username':
        user = val.get_user()
        return getattr(user,attribute).lower()
    elif attribute == 'score':
        score = getattr(val,attribute)
        if score is not None:
            return score
        return 0
    res = getattr(val,attribute)

    if isinstance(res,str):
        return res.lower()
    return res


def insertion_sort(arr,attribute):
    for pos in range(1,len(arr)):
        current = arr[pos]

        new_pos = pos-1

        while new_pos >= 0 and get_attribute(current,attribute) < get_attribute(arr[new_pos],attribute):
            arr[new_pos+1] = arr[new_pos]
            new_pos -=1
        
        arr[new_pos+1] = current
    return arr

class Scrollable_Frame(tk.Frame):
    def __init__(self,master,row=0,column=0,sticky='',columnspan=1,*args,**kwargs):
        super().__init__(master,*args,**kwargs)
        canvas = tk.Canvas(master)
        frame_scrollbar = ttk.Scrollbar(master,orient='vertical',command=canvas.yview)

        self.scroll_frame = ttk.Frame(canvas)

        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=frame_scrollbar.set)

        canvas.grid(row=row,column=column,columnspan=columnspan,sticky=sticky,padx=(20,0),ipadx=20)
        frame_scrollbar.grid(row=row,column=column,columnspan=columnspan,sticky='nse',padx=(450,0))
