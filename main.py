#Imports
import tkinter as tk             
from tkinter import font as tkfont  
from pages import *

#Main Application Class - Controls the window of the application
class MainApplication(tk.Tk):

    #Application initialisation
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.update_title('Flashcard Login')
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.userPages=[Home,Browse_Flashcards,View_Flashcards]
        ''' the container is where we'll stack a bunch of frames
        on top of each other, then the one we want visible
        will be raised above the others'''
        self.container = tk.Frame(self,padx=50)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.create_login()
        self.show_frame("Login")

    def create_login(self):
        self.frames = {}
        self.create_set_frames = []
        self.learn_set_frames = []
        self.revise_set_frames = []
        self.set_frames = tk.IntVar()
        self.set_title = tk.StringVar()
        frame = Login(parent=self.container, controller=self)
        self.frames['Login']= frame

        frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    #Creates all the frames that require a user to operate - frames after logging in
    def create_user_frames(self,container,user):
        for Frame in self.userPages:
            page_name = Frame.__name__
            createUserFrame(Frame,page_name,container,self,user=user)
     
    #Deleted all the frames that require a user to operate - frames after logging in
    def delete_user_frames(self):
        for Frame in self.userPages:
            page_name = Frame.__name__
            self.frames[page_name].destroy()

    def destroy_frame(self,frame_name):
        self.frames[frame_name].destroy()

    def update_title(self,title_name):
        self.title(title_name)

#Main Program
if __name__ == "__main__":
    app = MainApplication()
    app.minsize(480,270) # e the size of the window
    app.mainloop()