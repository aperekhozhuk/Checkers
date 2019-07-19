import tkinter as tk

class Board:
    def __init__(self):
        # Window settings
        self.root = tk.Tk()
        self.root.resizable(0,0)
        self.root.title('Checkers')
        self.size = 8 * (min(self.root.winfo_screenheight(),
                        self.root.winfo_screenwidth()) // 10)
        self.cellSize = self.size // 8
        self.canvas = tk.Canvas(width = self.size,
                                height = self.size)
        self.canvas.pack()
        self.canvas.bind('<Button-1>',self.Click())
        self.root.bind('<Return>',self.NewGameEvent())
        # Board drawing
        self.bg = ('#f9efeb','#c65c39')  # colors for cells background
        self.bg2 = ('#dbcece','#611010') # colors for highlighting active figure
        self.colors = ('white','black')  # colors of figure
        for i in range(8):
            for j in range(8):
                x1 = self.cellSize * i
                y1 = self.cellSize * j
                x2 = self.cellSize * (i + 1)
                y2 = self.cellSize * (j + 1)
                self.canvas.create_rectangle(
                    x1,y1,x2,y2,fill = self.bg[(i + j)%2])
        # Game Vars
        self.Player1 = None   # "white" player
        self.Player2 = None   # "black" player
        self.active = None    # say, who is going now. it's link to Player object
        self.activeFigure = None # link to active figure
        self.gameOn = 1       # Say, is game going on? Need for blocking board after victory    
        self.flag = True      # False - if you defeat enemy figure and waiting to beat some other
        self.NewGame(0)       # start game after runing window
        
    def NewGame(self, mode = 1):  # mode = 1 says that one game left, and we need to clean board
        if mode:                  # and we need to clean board
            self.ClearBoard()
        self.gameOn = 1
        self.flag = True
        self.Player1 = Player(self,0)
        self.Player2 = Player(self,1)
        self.Players = [self.Player1,self.Player2]
        self.active = self.Player1
        self.activeFigure = None
 
    def NewGameEvent(self):   # Method for restarting game by pressing Enter
        def _NewGameEvent(event):
           self.NewGame()
        return _NewGameEvent
    
    def ClearBoard(self):     # cleaning board when you restart game
        l1 = self.Player1.FigureList
        l2 = self.Player2.FigureList
        for figure in l1:
            self.canvas.delete(l1[figure].id)
        for figure in l2:
            self.canvas.delete(l2[figure].id)

    def Click(self):    # Handling click on window
        def _Click(event):
            if not self.gameOn: # if game is over: block allmoves
                return
            x, y = event.x, event.y
            i, j = x // self.cellSize, y // self.cellSize
            if (i + j)%2 == 0:    # if we click non playing cell - skip
                return
            if (i,j) in self.active.FigureList: # if we click on figure of active Player
                if not self.flag:               # if you can't change active figure - skip
                    return
                if self.activeFigure:           # switc off highlighting of previous active figure
                    self.Highlight(1)
                self.activeFigure = self.active.FigureList[(i,j)] # re init active figure
                self.Highlight(0)               # highlighting new active figure
            else:   
                if self.activeFigure:           # if we already select figure for moving
                    stepRes =  self.activeFigure.MakeStep(i,j)   # trying to move 
                    if stepRes:                 # checking results of try
                        # if just moved to empty cell or hit enemy figure without possibles to hit any other
                        # then just ending of current step
                        if stepRes == 1 or (self.activeFigure.CheckWays() == []):                 
                            self.EndStep()
                            self.activeFigure = None
        return _Click

    def CheckCell(self,x,y):
        # return: 0 if cells setled by white figure,
        # 1 if setled by black
        # -1 if cell if free
        if (x,y) in self.Player1.FigureList:
            return 0
        if (x,y) in self.Player2.FigureList:
            return 1
        return -1
            
    def EndStep(self): # ending of step
        self.Highlight(1)  # removing highlight
        self.flag = True   # restore possible to change active figure
        self.VictoryAlert()
        # changing active player
        if self.active == self.Player1:
            self.active = self.Player2
            return  
        if self.active == self.Player2:
            self.active = self.Player1
 
    def Highlight(self, mode):
        # mode = 0 - for activate highlighting,
        # 1 - for deactivate
        if mode == 0:
            colors = self.bg2
        else:
            colors = self.colors         
        color = colors[self.activeFigure.color]
        self.canvas.itemconfig(self.activeFigure.id, fill = color)

    def VictoryAlert(self):
        alert = ''
        if self.Player1.rest == 0:
            alert = 'Player1'
        if self.Player2.rest == 0:
            alert = 'Player2'
        if alert:
            alert = alert + ' wins!!!!'
            self.canvas.create_text(self.size//4,self.size//2, fill = 'red',
                                    font="Times 20 italic bold", text = alert)
        
class Figure:    # i,j - position on board, color = 0 - for white, 1 - for black
    def __init__(self,Board,i,j,color):
        self.Board = Board
        self.D = Board.cellSize
        self.r = self.D//10
        self.x = i
        self.y = j
        self.vip = False   # True - if figure is Queen
        self.color = color
        self.id = self.Board.canvas.create_oval(self.D*i + self.r, self.D*j + self.r,
                  self.D*(i + 1) - self.r,self.D*(j + 1) - self.r,fill = self.Board.colors[self.color])        

    def Move(self,x,y):  # just moving figure to new position
        self.Board.canvas.delete(self.id)
        self.id = self.Board.canvas.create_oval(self.D*x + self.r, self.D*y + self.r,
                  self.D*(x + 1) - self.r,self.D*(y + 1) - self.r,fill = self.Board.colors[self.color])

        if y == 0 or y == 7:
            self.vip = True    
        self.Board.Players[self.color].FigureList[(x,y)] = self
        del self.Board.Players[self.color].FigureList[(self.x,self.y)]
        self.x = x
        self.y = y    

    def MakeStep(self,x,y):  # trying to make move 
        isFree = self.Board.CheckCell(x,y) # checking, is cell settled by any player     
        if isFree >= 0 : # if cell settled by any figure - step impossible
            return 0
        # if cell is neighbour - just move
        if abs(self.x - x) == 1 and (y - self.y) == 2*self.color - 1:
            self.Move(x,y)
            return 1
        # if distance bewtween current position and new == 2 
        if abs(self.x - x) == 2 and abs(y - self.y) == 2:
            x1 = (self.x + x)//2
            y1 = (self.y + y)//2            
            if self.Board.CheckCell(x1,y1 ) == abs(1 - self.color):
                self.Board.Players[abs(1 - self.color)].DeleteFigure(x1,y1)
                self.Move(x,y)
                self.Board.Highlight(0)
                self.Board.flag = False
                return 2
    # Check possible moves after hiting enemy figure
    def CheckWays(self):
        routes = [(-2,-2),(2,-2),(-2,2),(2,2)]
        ways = []
        x,y = self.x,self.y
        for v in routes:
            x1,y1 = x + v[0], y + v[1]
            if x1 >= 0 and x1 <=7 and y1 >= 0 and y1 <= 7:
                if self.Board.CheckCell(x1,y1) >= 0:
                    continue
                x2,y2 = (x1 + x)//2, (y1 + y)//2
                if (x2,y2) in self.Board.Players[abs(1 - self.color)].FigureList:
                    ways.append((x1,y1))
        return ways            
                        
class Player:   # color = 0 - for white, 1 - for black
    def __init__(self,Board,color):
        self.color = color
        self.Board = Board
        self.FigureList = {}
        self.rest = 12    # count of figure which rest
        for i in range(3):
            y = (7 - i)*(1 -color) + i*color
            for j in range((color + i)%2,8,2):
                self.FigureList[(j,y)] = Figure(self.Board,j,y,self.color)
    # delete figure from board after hiting
    def DeleteFigure(self,x,y):
        self.Board.canvas.delete(self.FigureList[(x,y)].id)
        del self.FigureList[(x,y)]
        self.rest = self.rest - 1
        
Board = Board()




            
