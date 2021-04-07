import random
from tkinter.constants import E
from utils import *
from classes import *

#Constants
COLUMN_WIDTH = 12
HALF = COLUMN_WIDTH//2
THIRDS = COLUMN_WIDTH//3
QUARTERS = HALF//2
TWO_THIRDS = 2*THIRDS


SELECT1 = """SELECT userid, username 
        FROM app_user 
        WHERE LOWER(username) = LOWER(CONVERT(%s using utf8mb4)) 
        COLLATE utf8mb4_bin"""

#Base Page Class - Avoiding redundant __init__ methods across pages
class Page(tk.Frame):
    def __init__(self, parent,controller):
        self.style = ttk.Style()
        self.style.configure('Red.TLabel',foreground='#c33')
        self.style.configure('Green.TLabel',foreground='#3a3')
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.controller = controller
        self.previous = None
    
    def set_previous(self,previous):
        self.previous = previous

    def move_back(self):
        if self.previous:
            self.previous.tkraise()


    def create_back_button(self,command = 0):
        if not command:
            back_button = ttk.Button(self,text='Back',command=self.move_back)
        else:    
            back_button = ttk.Button(self,text='Back',command=command)
        back_button.grid(row=0,column=0,columnspan=QUARTERS,sticky='w')

#Base User Page Class - Avoiding redundant assigning of user to all Pages
class UserPage(Page):
    def __init__(self,parent,controller,user):
        super().__init__(parent,controller)
        self.user = user
        if not user.registered:
            warning = ttk.Label(self,text='Register to access the rest of the program!',wraplength=100,justify=tk.CENTER)
            signUp = ttk.Button(self,text='Register', command=self.sign_up)
            logout = ttk.Button(self,text='Logout',command=self.logout)

            warning.configure(style='Red.TLabel')
            
            warning.grid(row=0,column=QUARTERS,columnspan=QUARTERS,sticky='e',padx=7)
            signUp.grid(row=0,column=HALF+1,columnspan=QUARTERS,sticky='e',padx=7)
            logout.grid(row=0,column=HALF+QUARTERS+1,columnspan=QUARTERS,sticky='e',padx=7)
        else:
            logout = ttk.Button(self,text='Logout',command=self.logout)
            logout.grid(row=0,column=COLUMN_WIDTH,sticky='e')

    def logout(self):
        #Reset all frames
        for frame in self.controller.frames.values():
            frame.destroy()
        self.controller.update_title('Flashcard Login')
        self.controller.create_login()
        self.controller.show_frame('Login')
            
    def sign_up(self):
        frame = SignUp(self.parent,self.controller,self.user,self.controller.frames['View_Flashcards'])
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def reset_frames(self,Frame):
        #Reset all frames
        self.controller.delete_user_frames()
        frame_name = Frame.__name__    
        self.controller.create_user_frames(user=self.user,container = self.controller.container)
        self.controller.show_frame(frame_name)


#Login Page
class Login(Page):
    def __init__(self,parent,controller,errors=[]):
        super().__init__(parent,controller)
        title = "Login"
        label = ttk.Label(self, text=title, font=controller.title_font)
        label.pack(side="top", pady=10,anchor=tk.CENTER)
        
        input_label = ttk.Label(self, text = 'Enter your Username: ', font=('Helvetica',15))
        input_label.pack(side="top", fill="x", pady=10)
        
        self.username_input = ttk.Entry(self)
        self.username_input.pack(side="top", fill="x", pady=10)
        self.username_input.bind('<Return>',self.login_bind)

        if errors:
            for error in errors:
                error_label = ttk.Label(self,text=error,wraplength=300,justify=tk.CENTER)
                error_label.configure(style='Red.TLabel')
                error_label.pack()

        self.login_button = ttk.Button(self, text="Login",
                            command=lambda: self.login_check(self.username_input.get()))
        self.login_button.pack()

    def login_bind(self,event):
        self.login_check(self.username_input.get())

    #Checks the username to see if it already exists.
    def login_check(self,username):
        mycursor.execute(SELECT1,(username,))
        myresult = mycursor.fetchone()
        #If the username exists in the database:
        errors = validate_username(username)
        errors = errors.values()
        username = username.title()
        if errors:
            self.destroy()
            frame = Login(parent=self.parent, controller=self.controller,errors = errors)
            self.controller.frames['Login'] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            self.controller.show_frame('Login')
        else:    
            if myresult:
                user = RegisteredUser(username,myresult[0])
                createUserFrame(PasswordLogin,'PasswordLogin',self.parent,self.controller,user)
                self.controller.show_frame('PasswordLogin')
            else:
                user = User(username)
                self.controller.create_user_frames(self.parent,user)
                self.controller.update_title(f'Welcome, {user.username}')
                self.controller.show_frame('View_Flashcards')

#Password login page if the user exists in the database
class PasswordLogin(Page):
    def __init__(self,parent,controller,user,errors=[]):
        super().__init__(parent,controller)
        button = ttk.Button(self, text="Back",
            command=lambda:self.back())
        button.pack(side='top',anchor=tk.W)

        self.user = user

        title=f'Enter your Password, {user.username}'
        
        label = ttk.Label(self, text=title, font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        self.password_input = ttk.Entry(self, show='*')
        self.password_input.pack(side="top", fill="x", pady=10)
        self.password_input.bind('<Return>',self.login_bind)
        if errors:
            for error in errors:
                error_label = ttk.Label(self,text=error,wraplength=400,justify=tk.CENTER,style='Red.TLabel')
                error_label.pack()
        login_button = ttk.Button(self, text="Login",
                            command=self.login_bind)
        login_button.pack()

    def login_bind(self,event=None):
        self.login_check_password(self.user,self.password_input.get())

    #Checks to see if the password matches the username it's tied to     
    def login_check_password(self,user,password):
        if user.check_password(password):
            self.destroy()
            self.controller.create_user_frames(self.parent,user)
            self.controller.update_title(f'{user.username}\'s Flashcards')
            self.controller.show_frame('Home')
        else:
            self.destroy()
            createUserFrame(PasswordLogin,'PasswordLogin',self.parent,self.controller,user,['Invalid Password, please try again'])
            self.controller.show_frame('PasswordLogin')
    
    #Move Back
    def back(self):
        self.controller.show_frame('Login')
        self.destroy()

#Home page
class Home(UserPage):
    def __init__(self,parent,controller,user,errors=[]):
        super().__init__(parent,controller,user)
        title='Home'
        label = ttk.Label(self, text=title, font=controller.title_font)
        label.grid(row=1,columnspan=COLUMN_WIDTH+1)
        view = ttk.Button(self, text="View/Create Your Flashcards",
                           command=lambda: controller.show_frame("View_Flashcards"))
        view.grid(row=2,column=0,columnspan=HALF,padx=5,pady=10,ipadx=50,ipady=50)
        browse = ttk.Button(self, text="Browse All Flashcards",
                           command=lambda: controller.show_frame("Browse_Flashcards"))
        browse.grid(row=2,column=HALF+1,columnspan=HALF,padx=5,pady=10,ipadx=50,ipady=50)
 
class View_Flashcards(UserPage):
    def __init__(self,parent,controller,user,errors=[],create_flashcards = []):
        super().__init__(parent,controller,user)
        title='View Flashcards'
        self.set_previous(self.controller.frames['Home'])
        
        
        #Program is accessed if registered
        if user.registered:
            self.create_back_button()


        label = ttk.Label(self, text=title, font=controller.title_font)
        label.grid(row=1,columnspan=HALF+QUARTERS)
        create_container = Scrollable_Frame(self,row=2,columnspan=COLUMN_WIDTH-1,sticky='nsew')
        self.flashcards = [FlashcardSet(setNickname,iden=setID,user_iden=userID,score=score)
                        if setNickname
                        else FlashcardSet(setTitle,iden=setID,user_iden=userID,score=score)
                        for setID, setTitle, setNickname,userID,score 
                        in user.get_sets()]
        
        
        if not create_flashcards:
            self.create_flashcards = [ViewSetDetails(create_container.scroll_frame,self.controller,flashcard_set,row,user.registered) 
                                        for row, flashcard_set 
                                        in enumerate(self.flashcards)]
        else: self.create_flashcards = [ViewSetDetails(create_container.scroll_frame,self.controller,flashcard_set,row,user.registered) 
                                        for row, flashcard_set 
                                        in enumerate(create_flashcards)]
        
        
        button = ttk.Button(self, text="+ Create a new flashcard set",command=self.create_set)
        button.grid(row=3,columnspan=HALF+QUARTERS)

        if not user.registered:
            button.config(state=tk.DISABLED)
        
        container = ttk.Frame(self)
        container.grid(row=1,rowspan=2,column=COLUMN_WIDTH)
        self.create_sort_buttons(container)
        

    def create_set(self):
        frame = CreateTitle(parent = self.parent, controller = self.controller,user=self.user)
        frame.grid(row=0, column=0, sticky="nsew")

    def sort_sets(self,attr='',reverse = False):
        page_name = View_Flashcards.__name__
        sets = self.flashcards
        if sets and attr:
            sets = insertion_sort(sets,attr)
        else:
            sets = [FlashcardSet(setNickname,iden=setID,user_iden=userID,score=score)
                        if setNickname
                        else FlashcardSet(setTitle,iden=setID,user_iden=userID,score=score)
                        for setID, setTitle, setNickname,userID,score in self.user.get_sets()]
        if reverse:
            sets = sets[::-1]

        self.controller.destroy_frame(page_name)
        frame = View_Flashcards(parent = self.controller.container,controller = self.controller,user=self.user,create_flashcards = sets)
        self.controller.frames[page_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def create_sort_buttons(self,container):
        #Sorting Buttons
        sort_label = ttk.Label(container,text='SORT BY:',anchor = tk.CENTER)
        sort_label.grid(row=0,sticky='nsew',pady=2)

        title_asc = ttk.Button(container,text='Set Title (A-Z)',command = lambda:self.sort_sets('title'))
        title_asc.grid(row=1,sticky='nsew',pady=2)     
        title_desc = ttk.Button(container,text='Set Title (Z-A)',command = lambda:self.sort_sets('title',True))
        title_desc.grid(row=2,sticky='nsew',pady=2)     
        username_asc = ttk.Button(container,text='Author Name (A-Z)',command = lambda:self.sort_sets('username'))
        username_asc.grid(row=3,sticky='nsew',pady=2)     
        username_desc = ttk.Button(container,text='Author Name (Z-A)',command = lambda:self.sort_sets('username',True))
        username_desc.grid(row=4,sticky='nsew',pady=2)     
        score_asc = ttk.Button(container,text='Score (Lowest to Highest',command = lambda:self.sort_sets('score'))
        score_asc.grid(row=3,sticky='nsew',pady=2)     
        score_desc = ttk.Button(container,text='Score(Highest to Lowest)',command = lambda:self.sort_sets('score',True))
        score_desc.grid(row=4,sticky='nsew',pady=2)     
        reset = ttk.Button(container,text='Default',command =self.sort_sets)
        reset.grid(row=7,sticky='nsew',pady=2) 

#Keeps track of the individual set frames in View Flashcards
class ViewSetDetails(tk.Frame):
    def __init__(self,parent,controller,flashcard_set,row,registered=False):
        super().__init__(parent,bg='white')
        #Class Attributes
        self.flashcard_set = flashcard_set
        self.controller = controller
        self.parent = self.master.master.master

        #GUI initialization
        self.pack(fill='both',expand=1)
        self.grid_rowconfigure(0, weight=1,pad=10)
        self.grid_columnconfigure(0, weight=1)
        
        #GUI Widgets
        set_label = ttk.Label(self,text = flashcard_set.title,wraplength=50,justify=tk.CENTER)

        author_label = ttk.Label(self,text=f'Made By: {flashcard_set.get_user().username}',wraplength=50,justify=tk.CENTER)


        learn = ttk.Button(self,text='Learn',command=self.learn_set)
        
        revise = ttk.Button(self,text='Revise',command=self.revise_set)

        edit_options = ttk.Frame(self)
        edit = ttk.Button(edit_options,text='Edit',command=self.edit_set)
        delete = ttk.Button(edit_options,text='Remove',command = self.remove_current_set)
        

        #Conditional GUI - Check if the user is registered or not
        if registered:
            score_label = 'Untested'

            if flashcard_set.score is not None:
                score_label = f'{flashcard_set.score}%'
            
            score = ttk.Label(self,text=f'SCORE: {score_label}',wraplength=50,justify=tk.CENTER)
            score.grid(row=row,column = 1, sticky='nsew')

            user = flashcard_set.get_user()

            #Checks to see if the current user is the same as the author
            if self.parent.user == user: 
                delete = ttk.Button(edit_options,text='Delete',command=self.delete_current_set)
            else:
                edit = ttk.Button(edit_options,text='Edit Title',command=self.edit_title)
        else:
            revise.config(state=tk.DISABLED)
            edit.config(state=tk.DISABLED)
            delete.config(state=tk.DISABLED)
        
        #GUI POSITIONING
        set_label.grid(row=row, sticky='w',padx=5)
        author_label.grid(row=row,column=2,sticky='w',padx=5)
        learn.grid(row=row,column=3,padx=5)
        revise.grid(row=row,column=4,padx=5)
        edit_options.grid(row=row,column = 5,padx=5)
        edit.grid(row=0, sticky='nsew')
        delete.grid(row=1, sticky='nsew')

    #CLASS METHODS - Redirects
    def learn_set(self):
        cards = self.flashcard_set.get_cards()
        self.flashcard_set.shuffle_set()
        length = len(cards)
        for index,flashcard in enumerate(self.flashcard_set.cards):
            frame = LearnSet(self.parent.parent,self.controller,self.parent.user,flashcard,index,length,errors=[])
            frame.grid(row=0, column=0, sticky="nsew")
            self.controller.learn_set_frames.append(frame)
        self.controller.learn_set_frames[0].tkraise()
    
    def revise_set(self):
        cards = self.flashcard_set.get_cards()
        parent=self.master.master.master
        length = len(cards)
        for index,flashcard in enumerate(cards):
            frame = ReviseSet(parent.parent,self.controller,parent.user,flashcard,cards,index,length,flash_set = self.flashcard_set)
            self.controller.revise_set_frames.append(frame)
            frame.grid(row=0, column=0, sticky="nsew")
        self.controller.revise_set_frames[0].tkraise()
    
    def edit_set(self):
        cards = self.flashcard_set.get_cards()
        parent = self.master.master.master
        for index,flashcard in enumerate(cards):
            frame = CreateFlashcard(parent.parent,self.controller,self.flashcard_set.title,parent.user,flashcard = flashcard,mode='UPDATE',position=index,flashcard_set=self.flashcard_set)
            frame.grid(row=0, column=0, sticky="nsew")
        self.controller.create_set_frames[0].tkraise()

    def edit_title(self):
        frame = CreateTitle(parent = self.parent.parent, controller = self.controller,user=self.parent.user,flash_set=self.flashcard_set,title='Update')
        frame.grid(row=0, column=0, sticky="nsew")

    def delete_current_set(self):
        self.flashcard_set.delete_set()
        name = View_Flashcards.__name__
        frame = View_Flashcards(self.controller.frames[name].parent,self.controller,self.controller.frames[name].user)
        self.controller.frames[name] = frame
        self.controller.show_frame(name)
        self.destroy()

    def remove_current_set(self):
        self.parent.user.remove_set(self.flashcard_set)
        self.parent.reset_frames(View_Flashcards)


#Page to browse all the flashcards in the DB
class Browse_Flashcards(UserPage):
    def __init__(self,parent,controller,user,errors=[],sets = []):
        super().__init__(parent,controller,user)
        title='Browse Flashcards'
        self.sets = sets
        if not sets:
            sets = self.get_all_sets()
            self.sets = list(map(lambda x:FlashcardSet(*x),sets))
        self.set_previous(self.controller.frames['Home'])
        self.create_back_button()
        set_frame = Scrollable_Frame(self,row=2,columnspan=TWO_THIRDS)
        label = ttk.Label(self, text=title, font=controller.title_font)
        label.grid(row=1,columnspan=TWO_THIRDS)
        for row,f_set in enumerate(self.sets):
            BrowseSetDetails(set_frame.scroll_frame,controller,f_set,row=row,columnspan=THIRDS)

        sort_frame = ttk.Frame(self)
        sort_frame.grid(row=1,column=TWO_THIRDS,columnspan=THIRDS,rowspan=2)
        self.create_sort_buttons(sort_frame)

    #Sorting
    def sort_sets(self,attr='',reverse = False):
        page_name = Browse_Flashcards.__name__
        sets = self.sets
        if sets and attr:
            sets = insertion_sort(self.sets,attr)
        else:
            sets = self.get_all_sets()
            sets = list(map(lambda x:FlashcardSet(*x),sets))
        if reverse:
            sets = sets[::-1]

        self.controller.destroy_frame(page_name)
        frame = Browse_Flashcards(parent = self.controller.container,controller = self.controller,user=self.user,sets = sets)
        self.controller.frames[page_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def create_sort_buttons(self,container):
        #Sorting Buttons
        sort_label = ttk.Label(container,text='SORT BY:',anchor = tk.CENTER)
        sort_label.grid(row=0,sticky='nsew',pady=2)

        title_asc = ttk.Button(container,text='Set Title (A-Z)',command = lambda:self.sort_sets('title'))
        title_asc.grid(row=1,sticky='nsew',pady=2)     
        title_desc = ttk.Button(container,text='Set Title (Z-A)',command = lambda:self.sort_sets('title',True))
        title_desc.grid(row=2,sticky='nsew',pady=2)     
        username_asc = ttk.Button(container,text='Author Name (A-Z)',command = lambda:self.sort_sets('username'))
        username_asc.grid(row=3,sticky='nsew',pady=2)     
        username_desc = ttk.Button(container,text='Author Name (Z-A)',command = lambda:self.sort_sets('username',True))
        username_desc.grid(row=4,sticky='nsew',pady=2)     
        reset = ttk.Button(container,text='Default',command =self.sort_sets)
        reset.grid(row=5,sticky='nsew',pady=2)     

    def get_all_sets(self):
        if self.user.registered:
            query = """SELECT setName,setID,userID 
            FROM flashcard_set
            WHERE NOT setID IN(
                SELECT user_sets.setID
                FROM user_sets
                WHERE flashcard_set.setID = user_sets.setID
                AND userID = %s
            );"""
            userID =self.user.get_id()
            user=(userID,)
            mycursor.execute(query,user)
            return mycursor.fetchall()
        mycursor.execute('SELECT setName,setID,userID FROM flashcard_set')
        return mycursor.fetchall()

 #Keeps track of the individual set frames in Browse Flashcards       
class BrowseSetDetails(tk.Frame):
    def __init__(self,parent,controller,flashcard_set,row,columnspan=1):
        super().__init__(parent,bg='white')
        self.flashcard_set = flashcard_set
        self.parent = parent.master.master
        self.controller = controller
        self.pack(fill=tk.BOTH, expand=True, anchor = tk.CENTER)
        self.grid_rowconfigure(0, weight=1,pad=10)
        self.grid_columnconfigure(0, weight=1)
        
        set_label = ttk.Label(self,text = flashcard_set.title,wraplength=100,justify=tk.CENTER)
        set_label.grid(row=0,columnspan = columnspan,sticky='w',padx=10,pady=5)
        author = ttk.Label(self,text = f'Made by: {flashcard_set.get_user().username}',wraplength=100,justify=tk.CENTER)
        author.grid(row=0,column=THIRDS,columnspan=columnspan,sticky='w',padx=10,pady=5)
        add_self = ttk.Button(self,text= '+ Add to collection',command = self.add)
        add_self.grid(row=0,column=TWO_THIRDS,columnspan=columnspan,padx=10,pady=5)


        if not parent.master.master.user.registered:
            add_self.config(state=tk.DISABLED)

    def add(self):
        self.flashcard_set.add_user(self.parent.user)
        self.parent.reset_frames(Browse_Flashcards)

#Create Title Page
class CreateTitle(UserPage):
    def __init__(self,parent,controller,user,title='',flash_set = ''):
        super().__init__(parent,controller,user)
        #Instantiation
        self.flashcard_set = flash_set

        #GUI Widgets
        label = ttk.Label(self, text='Enter your set title', font=controller.title_font)
        self.title = ttk.Entry(self)
        create = ttk.Button(self, text="Continue",
                           command=self.create_set)
        if title:
            create = ttk.Button(self, text='Update Title',command=self.update_title)
        
        create.bind('<Return>',self.create_set)
        #Positioning
        label.grid(row=1,columnspan=COLUMN_WIDTH,sticky='nsew',pady=10)
        self.title.grid(row=2,columnspan=COLUMN_WIDTH,pady=10)
        create.grid(row=3,columnspan=COLUMN_WIDTH,pady=10)
        
        self.set_previous(self.controller.frames['Home'])
        self.create_back_button()
    
    def create_set(self,event=None):

        frame = CreateFlashcard(self.parent,self.controller,self.title.get(),self.user)
        frame.grid(row=0, column=0, sticky="nsew")

    def update_title(self):
        sql = """UPDATE user_sets 
        SET nickname = %s
        WHERE userID = %s
        AND setID = %s"""
        values = (self.title.get(),self.user.get_id(),self.flashcard_set.get_id())
        mycursor.execute(sql,values)
        appdb.commit()
        self.reset_frames(View_Flashcards)


#Create Flashcard Page
class CreateFlashcard(UserPage):
    def __init__(self,parent,controller,title,user,flashcard=None,mode ='CREATE',position = 0,flashcard_set = None):
        #Class Variables
        
        super().__init__(parent,controller,user)


        self.flashcard = flashcard
        self.position = position
        self.index = len(controller.create_set_frames)
        self.errors = tk.StringVar()

        self.controller.set_title.set(title)
        self.flash_set = flashcard_set
        self.mode = mode

        self.create_back_button(self.cancel)

        #GUI Initialise
        label = ttk.Label(self, text='Title:')
        self.title_widget = ttk.Entry(self,text = self.controller.set_title)
        phrase = ttk.Label(self, text='Word/Phrase:')
        self.phrase_var = tk.StringVar()
        self.phrase_widget = ttk.Entry(self,text=self.phrase_var)
        definition = ttk.Label(self, text='Definition:')
        self.definition_var = tk.StringVar()
        self.definition_widget = tk.Text(self,height=5,width=30)
        self.error_label = ttk.Label(self,textvariable=self.errors,wraplength=200,justify=tk.CENTER)


        self.create = ttk.Button(self, text="Continue", command=self.create_frame,state=tk.DISABLED)
        self.back = ttk.Button(self, text="Destroy",command=self.destroy_frame)
        self.finish = ttk.Button(self, text='Finish',command=self.finish, state=tk.DISABLED)

        self.definition_widget.bind('<KeyRelease>',self.update_var)
        self.definition_widget.bind('<BackSpace>',self.update_var)
        self.definition_widget.bind('<1>',self.update_var)

        #Setting Defaults
        if flashcard:
            self.phrase_var.set(flashcard.phrase)
            self.definition_var.set(flashcard.definition)
            self.definition_widget.replace('1.0','end-1c',flashcard.definition)
            
        #Variable Tracing
        self.phrase_var.trace_add('write',self.update_finish)
        self.definition_var.trace_add('write',self.update_finish)
        self.controller.set_title.trace_add('write',self.update_finish)

        if mode =='UPDATE':
            self.phrase_var.trace_add('write',self.update_frame)
            self.definition_var.trace_add('write',self.update_frame)
            
            self.create = ttk.Button(self, text='Next',command = self.move_forward,state=tk.NORMAL)
            self.back = ttk.Button(self,text='Back',command = self.move_back)
            self.update_frame()

        #GUI Positioning

        label.grid(row=1,columnspan=THIRDS,pady=5)
        self.title_widget.grid(row=1,column=THIRDS,columnspan=TWO_THIRDS,pady=5)
        phrase.grid(row=2,columnspan=THIRDS,pady=5)
        self.phrase_widget.grid(row=2,column=THIRDS,columnspan=TWO_THIRDS,pady=5)
        definition.grid(row=3,columnspan=THIRDS,pady=5)
        self.definition_widget.grid(row=3,column=THIRDS,columnspan=TWO_THIRDS,pady=5,ipadx=10)
        
        self.create.grid(row=4,columnspan=THIRDS,padx=5)
        self.back.grid(row=4,column=THIRDS,columnspan=THIRDS,padx=5)
        self.finish.grid(row=4,column=TWO_THIRDS,columnspan=THIRDS,padx=5)
        self.error_label.grid(row=5,columnspan=COLUMN_WIDTH)
        self.error_label.configure(style='Red.TLabel')

        controller.create_set_frames.append(self)

    def create_frame(self):
        frame = CreateFlashcard(self.parent,self.controller,self.controller.set_title.get(),self.user,position=self.position+1,flashcard_set=self.flash_set)
        frame.grid(row=0, column=0, sticky="nsew")
        self.controller.set_frames.set(len(self.controller.create_set_frames))

    def destroy_frame(self):
        self.controller.create_set_frames.remove(self)
        self.update_finish()
        self.destroy()

    def move_forward(self):
        if self.position == len(self.controller.create_set_frames)-1:
            self.create_frame()
        else:
            position = self.position + 1
            frame = self.controller.create_set_frames[position]
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()

    def move_back(self):
        if not self.position:
            self.back.config(state=tk.DISABLED)
        else:
            position = self.position - 1
            frame = self.controller.create_set_frames[position]
            frame.tkraise()

    def update_var(self,event):

        definition = self.definition_widget.get('1.0', 'end-1c')
        self.definition_var.set(definition)


    def update_frame(self,*args):
        phrase = self.phrase_var.get()
        definition = self.definition_var.get()

        self.create.config(state=tk.DISABLED)
        if not self.position:
            self.back.config(state=tk.DISABLED)

        if (phrase and definition):
            setID = self.flashcard.get_set_id()
            identity = self.flashcard.get_id()
            self.flashcard = Flashcard(phrase,definition,setID,identity)

            self.create.config(state=tk.NORMAL)

    def update_finish(self,*args):
        length = self.controller.set_frames
        set_frames = self.controller.create_set_frames
        
        title = self.controller.set_title.get()
        phrase = self.phrase_var.get()
        definition = self.definition_var.get()
        length.set(len(set_frames))
        
        if (title and phrase and definition):
            self.create.config(state= tk.NORMAL)
            if length.get() > 3 and all(frame.phrase_var.get() and frame.definition_var.get() for frame in set_frames):
                for frame in self.controller.create_set_frames:
                    frame.finish.config(state = tk.NORMAL)
            else:
                for frame in self.controller.create_set_frames:
                    frame.finish.config(state = tk.DISABLED)
            self.check_unique_phrase(phrase)
            self.validate_title(title)
            self.validate_phrase_and_definition(phrase,definition)
        else:
            self.create.config(state=tk.DISABLED)
            self.finish.config(state=tk.DISABLED)
    
    def validate_title(self,title):
        
        errors= validate_set_name(title)
        error = self.errors.get()
        self.errors.set(f'{error},{" ".join(errors)}')


    def check_unique_phrase(self,phrase):
        phrases = [card.phrase_widget.get() for card in self.controller.create_set_frames if card.position != self.position]
        if phrase in phrases:
            self.errors.set(f'{phrase} already exists in the flashcard set. Please create a unique phrase.')
            self.create.config(state=tk.DISABLED)
        else:
            self.errors.set('')
            self.create.config(state=tk.NORMAL)

    def validate_phrase_and_definition(self,phrase,definition):
        errors = self.errors.get()
        if len(phrase) > 20:
            self.errors.set(f'{errors},{phrase} is too long. Please enter a phrase shorter than 20 characters')
            self.create.config(state=tk.DISABLED)
        elif len(definition) > 100:
            errors = self.errors.get()
            self.errors.set(f'{errors},{phrase} is too long. Please enter a phrase shorter than 100 characters')
            self.create.config(state=tk.DISABLED)
        else:
            if not errors:
                self.create.config(state=tk.NORMAL)

    def finish(self):
        if self.flash_set:
            setID = self.flash_set.get_id()
            for frame in self.controller.create_set_frames:
                if frame.mode == 'UPDATE':
                    self.update_flashcard(frame)
                else:
                    flashcard = Flashcard(frame.phrase_widget.get(),frame.definition_widget.get('1.0', 'end-1c'),setID)
                    self.upload_flashcard(flashcard)
        else:
            flashSet = FlashcardSet(self.controller.set_title.get())
            setID = flashSet.addSetToDatabase(self.user)
            flashSet.set_id(setID)
        
            flashcards = [Flashcard(flashcard.phrase_widget.get(),flashcard.definition_widget.get('1.0', 'end-1c'),setID) for flashcard in self.controller.create_set_frames]
            
            flashSet.set_cards(flashcards)
            flashSet.add_flashcards()
        self.destroy_frames()
        page_name = View_Flashcards.__name__
        self.controller.destroy_frame(page_name)
        createUserFrame(View_Flashcards,page_name,self.parent,self.controller,self.user)
        self.controller.set_title.set('')
        self.controller.show_frame('View_Flashcards')


    def upload_flashcard(self,flashcard):
        self.flash_set.add_flashcard(flashcard)

    def update_flashcard(self,frame):
        flashcard = frame.flashcard
        flashcard.update()

    def destroy_frames(self):
        for frame in self.controller.create_set_frames:
            frame.destroy()
        del self.controller.create_set_frames[:]

    def cancel(self):
        self.destroy_frames()
        self.controller.show_frame('View_Flashcards')

#Signup Page for unregistered users
class SignUp(UserPage):
    def __init__(self,parent,controller,user,previous,errors=[]):
        super().__init__(parent,controller,user)
        title='Register'
        self.set_previous(previous)
        self.create_back_button()

        #Changes the Label at the top
        self.controller.update_title(f'Sign Up, {user.username}')
        
        #GUI WIDGETS
        label = ttk.Label(self, text=title, font=controller.title_font)
        self.username = ttk.Label(self,text=user.username)

        #Hides the password inputs
        self.password = ttk.Entry(self, show='*')
        self.confirm_password = ttk.Entry(self, show='*')
        
        finish = ttk.Button(self,text='Register!',command=self.register)

        #GUI POSITIONING
        label.grid(row=1,columnspan=COLUMN_WIDTH)
        self.username.grid(row=2,columnspan=COLUMN_WIDTH)
        self.password.grid(row=3,columnspan=COLUMN_WIDTH)
        self.confirm_password.grid(row=4,columnspan=COLUMN_WIDTH)
        finish.grid(row=5,columnspan= COLUMN_WIDTH)
    
    def register(self):
        password = self.password.get()
        confirm_password = self.confirm_password.get()

        if password and confirm_password and confirm_password != password:
            self.destroy()
            frame = SignUp(self.parent,self.controller,self.user,self.controller.frames['View_Flashcards'],errors=['Your Passwords must match'])
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()
        query = '''INSERT INTO app_user(username,password)
        VALUES(%s,%s)'''
        values = (self.username['text'],password,)
        mycursor.execute(query,values)
        appdb.commit()
        
        mycursor.execute(SELECT1,(self.username['text'],))
        myresult = mycursor.fetchone()
        self.controller.update_title(f'{self.user.username}\'s Flashcards')
        
        self.user = RegisteredUser(myresult[1],myresult[0])
        self.controller.delete_user_frames()
        self.controller.create_user_frames(self.parent,self.user)
        self.controller.show_frame('Home')
        self.destroy()
        
#LearnSet Page
class LearnSet(UserPage):
    def __init__(self,parent,controller,user,flashcard,index,length,errors=[]):
        super().__init__(parent,controller,user)
        #Class Attributes
        self.index = index
        self.flashcard = flashcard
        self.display_text = tk.StringVar()
        self.display_text.set(flashcard.phrase)


        #GUI Widgets
        self.create_back_button(self.cancel)

        self.create_button()
        
        nextButton = ttk.Button(self, text='Next', command=self.next)
        backButton = ttk.Button(self, text='Back',command=self.back)
        finishButton = ttk.Button(self,text='Finish',command=self.finish)

        #Checks if the user can go backwards or forwards (i.e. end of set or beginning of set)
        if self.index < length-1:
            finishButton['state']=tk.DISABLED     
        if self.index == 0:
            backButton['state']=tk.DISABLED
        if self.index == length-1:
            nextButton['state']=tk.DISABLED
        
        #GUI positioning
        nextButton.grid(row=2,column = 0)
        backButton.grid(row=2,column = 1)
        finishButton.grid(row=2,column = 2)


    def switch(self):
        if self.display_text.get() == self.flashcard.phrase:
            self.display_text.set(self.flashcard.definition)
        else:
            self.display_text.set(self.flashcard.phrase)
        self.word.destroy()
        self.create_button()

    def create_button(self):
        self.word = tk.Button(self,text=self.display_text.get(),command=self.switch,wraplength=200)
        self.word.grid(column=0,row=1,columnspan=6,padx=5,pady=5,ipadx=100,ipady=50)

    def next(self):
        self.controller.learn_set_frames[self.index+1].tkraise()
    
    def back(self):
        self.controller.learn_set_frames[self.index-1].tkraise()
 
    def finish(self):
        self.controller.show_frame('View_Flashcards')
        for frame in self.controller.learn_set_frames:
            frame.destroy()
        del self.controller.learn_set_frames[:]
    
    def cancel(self):
        for frame in self.controller.learn_set_frames:
            frame.destroy()
        del self.controller.learn_set_frames[:]
        self.reset_frames(View_Flashcards)

#Revise Set Page
class ReviseSet(UserPage):
    def __init__(self,parent,controller,user,flashcard,cards,index,length,errors=[],flash_set = ''):
        super().__init__(parent,controller,user)
        #Attributes
        self.flashcard = flashcard
        self.flashcard_set = flash_set
        self.index = index
        self.cards = cards
        self.answer = tk.StringVar()
        
        #Variables to use - choose 3 random cards that will be incorrect
        set_cards = [card for card in cards if card != self.flashcard]
        random.shuffle(set_cards)
        
        set_cards = set_cards[:3]
        
        #Add the corect answer and shuffle again
        answers = [(card,card.phrase) for card in set_cards]
        answers.append((self.flashcard,flashcard.phrase))
        random.shuffle(answers)
        
        #GUI
        title = ttk.Label(self,text=f'{self.flashcard.definition}',wraplength=150,justify=tk.CENTER)
        title.grid(row=1,columnspan=COLUMN_WIDTH+1)
        container = ttk.Frame(self)
        container.grid(row=2,columnspan=COLUMN_WIDTH+1,padx=10,ipadx=10)
        container.rowconfigure(2,weight=1)

        self.set_previous(self.controller.frames['View_Flashcards'])
        self.create_back_button(command=self.cancel)


        for num,(card,answer) in enumerate(answers):
            column = num%2
            row = num//2
            button = tk.Radiobutton(container,text=card.phrase,value = answer,variable=self.answer,indicator = 0,background='light blue')
            button.grid(row=row,column=column,padx=5,pady=5,ipadx=10,ipady=10,sticky='nsew')
            button.rowconfigure(row,weight=1)
            button.columnconfigure(column,weight=1)

        next_button = ttk.Button(self,text='Next',command=self.next)
        back_button = ttk.Button(self,text='Back',command=self.back)
        finish_button = ttk.Button(self,text='Finish',command = self.finish)
        #GUI CONDITIONS
        if self.index < length-1:
            finish_button['state']=tk.DISABLED     
        if self.index == 0:
            back_button['state']=tk.DISABLED
        if self.index == length-1:
            next_button['state']=tk.DISABLED

        next_button.grid(row=3,columnspan=THIRDS)
        back_button.grid(row=3,columnspan=THIRDS,column=THIRDS+1)
        finish_button.grid(row=3,columnspan=THIRDS,column=TWO_THIRDS+1)


    def next(self):
        self.controller.revise_set_frames[self.index+1].tkraise()
    
    def back(self):
        self.controller.revise_set_frames[self.index-1].tkraise()

    def finish(self):
        answers = [(frame.answer.get(),frame.answer.get() == frame.flashcard.phrase) 
        if frame.answer.get() else ('Unattempted',False)
        for frame in self.controller.revise_set_frames]
        
        frame = Results(self.parent,self.controller,self.user,answers,self.cards,self.flashcard_set)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()
        
        del self.controller.revise_set_frames[:]

    def cancel(self):
        for frame in self.controller.revise_set_frames:
            frame.destroy()
        del self.controller.revise_set_frames[:]
        self.reset_frames(View_Flashcards)

#Displays test results
class Results(UserPage):
    def __init__(self,parent,controller,user,answers,cards,flashcard_set):
        super().__init__(parent,controller,user)
        container = Scrollable_Frame(self,row=1,columnspan=COLUMN_WIDTH)
        self.answers = answers
        self.flashcard_set = flashcard_set
        
        for row,(answer,card) in enumerate(zip(answers,cards)):
            Result_Detail(container.scroll_frame,self.controller,answer,card,row,columnspan=COLUMN_WIDTH)
        self.score = self.get_score()

        self.total = ttk.Label(self,text=f'You scored: {self.score}%',style='Green.TLabel',font=controller.title_font,wraplength=100,justify=tk.CENTER)

        if self.score < 40:
            self.total.configure(style='Red.TLabel')

        self.update_scores()
        self.back_button = ttk.Button(self,text='Back',command=lambda:self.reset_frames(View_Flashcards))
        self.back_button.grid(row=0,column=0)
        self.total.grid(row=1,column=COLUMN_WIDTH)


    def update_scores(self):
        sql = """UPDATE user_sets
        SET score = %s
        WHERE userID = %s
        AND setID = %s;"""
        
        values = (self.score,self.user.get_id(),self.flashcard_set.get_id(),)
        mycursor.execute(sql,values)
        appdb.commit()

    def get_score(self):
        res = 0
        for _,correct in self.answers:
            res+=correct 
        percentage = (res/len(self.answers))*100
        return round(percentage,2)

#Contains the detail of each result
class Result_Detail(tk.Frame):
    def __init__(self,container,controller,answer,card,row,columnspan=1):
        super().__init__(container)
        self.correct = answer[1]
        user_answer = f'Your Answer: {answer[0]}'
        correct_answer = f'Correct Answer: {card.phrase}'

        result_container = ttk.Frame(container)

        question = ttk.Label(result_container,text=card.definition)
        question.grid(row=0,columnspan=columnspan)
        
        answers = ttk.Frame(result_container)
        answers.grid(row=1,columnspan=columnspan)
        if self.correct:
            your_answer = ttk.Label(answers,text=user_answer,style='Green.TLabel')
            correct = ttk.Label(answers,text='Correct! - '+correct_answer,style='Green.TLabel')
        else:
            your_answer = ttk.Label(answers,text=user_answer,style='Red.TLabel')
            correct = ttk.Label(answers,text='Incorrect - '+correct_answer,style='Red.TLabel')

        your_answer.grid(row=0,columnspan=columnspan)
        correct.grid(row=1,columnspan=columnspan)

        result_container.grid(row=row,columnspan=columnspan,pady=5,ipady=2,padx=2,ipadx=2)