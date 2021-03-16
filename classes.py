from utils import *
import random
class User:
    def __init__(self,username,registered=False):
        self.username=username
        self.user_sets = []
        self.registered = registered

    def get_sets(self):
        sql = """SELECT flashcard_set.setID,setName,nickname,flashcard_set.userID,score
        FROM user_sets,flashcard_set 
        WHERE user_sets.setID=flashcard_set.setID
        AND user_sets.userID = flashcard_set.userID"""
        mycursor.execute(sql)
        return mycursor.fetchall()


class RegisteredUser(User):
    #Initialises the class
    def __init__(self,username,identity):
        super().__init__(username,True)
        self.__id = identity
        self.created_cards = []

    #Checks the password
    def check_password(self,password):
        sql = "SELECT password FROM app_user WHERE username = %s"
        mycursor.execute(sql,(self.username,))
        myresult = mycursor.fetchone()
        return (password == myresult[0])

    #Getter method
    def get_id(self):
        return self.__id

    #Gets all the setID, setName, setNickname, and authorID from the user_sets table if the userID is equal to the current userID
    def get_sets(self):
        sql = """SELECT user_sets.setID,setName,nickname,flashcard_set.userID,score
        FROM user_sets,flashcard_set
        WHERE user_sets.setID = flashcard_set.setID 
        AND user_sets.userID = %s
        """
        identity = (str(self.__id),)
        mycursor.execute(sql,identity)
        return mycursor.fetchall()


    #Removes a given set from the user_sets table
    def remove_set(self,flashcard_set):
        sql = """DELETE FROM user_sets
        WHERE setID = %s
        AND userID = %s
        """
        setID = flashcard_set.get_id()
        values = (setID,self.get_id(),)
        mycursor.execute(sql,values)
        appdb.commit()
    

    #Defining what User() = User() is
    def __eq__(self, other):
        return self.get_id() == other.get_id()

class FlashcardSet:
    def __init__(self,title,iden = -1,user_iden = -1,score = None):
        self.title = title
        self.cards = []
        self.__id = iden
        self.__created_user = user_iden
        self.score = score
        if user_iden >= 0:
            self.__created_user = self.init_user(user_iden)
        

    def shuffle_set(self):
        random.shuffle(self.cards)

    def addSetToDatabase(self,user):
        query1 = "INSERT INTO flashcard_set(setName,userID) VALUES (%s,%s);"
        query2 = "INSERT INTO user_sets(setID,userID) VALUES (%s,%s)"
        user_id = str(user.get_id())
        values = (self.title,user_id,)
        mycursor.execute(query1,values)
        appdb.commit()
        mycursor.execute('SELECT LAST_INSERT_ID()')
        myresult = mycursor.fetchone()
        setID = myresult[0]
        mycursor.execute(query2,(setID,user_id,))
        return setID

    def add_flashcard(self,flashcard):
        sql = "INSERT INTO flashcard(phrase,definition,setID) VALUES(%s,%s,%s);"
        values = (flashcard.phrase,flashcard.definition,self.get_id())
        mycursor.execute(sql,values)
        appdb.commit()

    def add_flashcards(self):
        sql = "INSERT INTO flashcard(phrase,definition,setID) VALUES(%s,%s,%s);"
        values = [(card.phrase,card.definition,self.__id,) for card in self.cards]
        mycursor.executemany(sql,values)
        appdb.commit()

    def get_id(self):
        return self.__id

    def get_cards(self):
        sql = 'SELECT * FROM flashcard WHERE setID = %s'
        mycursor.execute(sql,(self.__id,))
        self.cards = [Flashcard(phrase,definition,setID,cardID) for cardID,phrase,definition,setID in mycursor.fetchall()]
        return self.cards

    def init_user(self,user_id):
        query = 'SELECT username FROM app_user WHERE userID = %s'
        mycursor.execute(query,(user_id,))
        result = mycursor.fetchone()
        username = result[0]
        return RegisteredUser(username,user_id)

    def get_user(self):
        return self.__created_user

    def set_id(self,identity):
        self.__id = identity
        return self

    def set_cards(self,cards):
        self.cards = cards
        return self
    
    def delete_set(self):
        setID = self.get_id()
        query1 = "DELETE FROM flashcard WHERE setID=%s;"
        query2 = "DELETE FROM user_sets WHERE setID=%s;"
        query3 = "DELETE FROM flashcard_set WHERE setID = %s"
        
        mycursor.execute(query1,(setID,))
        mycursor.execute(query2,(setID,))
        mycursor.execute(query3,(setID,))
        appdb.commit()

    def add_user(self,user):
        userID = user.get_id()
        setID = self.get_id()

        query = 'INSERT INTO user_sets(setID,userID) VALUES(%s,%s)'
        mycursor.execute(query,(setID,userID,))
        appdb.commit()

class Flashcard:
    def __init__(self,phrase,definition,setID,identity = -1):
        self.phrase = phrase
        self.definition = definition
        self.__set_id = setID
        self.__id = identity
    
    def get_id(self):
        return self.__id
    def get_set_id(self):
        return self.__set_id
    
    def set_id(self,identity):
        self.__id = identity
        return self

    def update(self):
        query = '''UPDATE flashcard 
        SET phrase=%s, definition=%s
        WHERE cardID=%s'''
        values = (self.phrase,self.definition,self.__id)
        if self.__id >-1:
            mycursor.execute(query,values)
            appdb.commit()

    def __str__(self):
        return f'{self.phrase},{self.definition}'