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
        self.bg = ('#f9efeb','#c65c39')
        self.bg2 = ('#dbcece','#611010')
        self.colors = ('white','black')
        for i in range(8):
            for j in range(8):
                x1 = self.cellSize * i
                y1 = self.cellSize * j
                x2 = self.cellSize * (i + 1)
                y2 = self.cellSize * (j + 1)
                self.canvas.create_rectangle(
                    x1,y1,x2,y2,fill = self.bg[(i + j)%2])
        # Game Vars
        self.Player1 = None
        self.Player2 = None
        self.active = None    # say, who is going now
        self.activeFigure = None
        self.gameOn = 1
        self.NewGame(0)
        
    def NewGame(self, mode = 1):  # mode = 1 says that one game left, and we need to clean board
        if mode:                  # and we need to clean board
            self.ClearBoard()
        self.gameOn = 1    
        self.Player1 = Player(self,0)
        self.Player2 = Player(self,1)
        self.Players = [self.Player1,self.Player2]
        self.active = self.Player1
        self.activeFigure = None

    def NewGameEvent(self):
        def _NewGameEvent(event):
           self.NewGame()
        return _NewGameEvent
    
    def ClearBoard(self):
        l1 = self.Player1.FigureList
        l2 = self.Player2.FigureList
        for figure in l1:
            self.canvas.delete(l1[figure].id)
        for figure in l2:
            self.canvas.delete(l2[figure].id)

    def DeleteFigure(self,x,y,player):
        self.canvas.delete(player.FigureList[(x,y)].id)
        del player.FigureList[(x,y)]

    def Click(self):
        def _Click(event):
            if not self.gameOn:
                return
            x, y = event.x, event.y
            i, j = x // self.cellSize, y // self.cellSize
            if (i + j)%2 == 0:
                return
            if (i,j) in self.active.FigureList:
                #self.Highlight(1)
                self.activeFigure = self.active.FigureList[(i,j)]
                self.Highlight(0)
            else:
                if self.activeFigure:
                    stepRes =  self.activeFigure.MakeStep(i,j)
                    if stepRes:
                        print(self.activeFigure.CheckWays())
                        if stepRes == 1 or (self.activeFigure.CheckWays() == []):                 
                            self.EndStep()
                            self.activeFigure = None
        return _Click

    def CheckCell(self,x,y):
        if (x,y) in self.Player1.FigureList:
            return 0
        if (x,y) in self.Player2.FigureList:
            return 1
        return -1
            
    def EndStep(self):
        self.Highlight(1)
        if self.Player1.rest == 0:
            print('Black wins')
            self.gameOn = 0
            return
        if self.Player2.rest == 0:
            print('White wins')
            self.gameOn = 0
            return
        if self.active == self.Player1:
            self.active = self.Player2
            return  
        if self.active == self.Player2:
            self.active = self.Player1

    def Highlight(self, mode):
        if mode == 0:
            colors = self.bg2
        else:
            colors = self.colors
          
        color = colors[self.activeFigure.color]
        print(color)  
        self.canvas.itemconfig(self.activeFigure.id, fill = color)
                        
class Figure:    # i,j - position on board, color = 0 - for white, 1 - for black
    def __init__(self,Board,i,j,color):
        self.Board = Board
        self.D = Board.cellSize
        self.r = self.D//10
        self.x = i
        self.y = j
        self.vip = False
        self.color = color
        self.id = self.Board.canvas.create_oval(self.D*i + self.r, self.D*j + self.r,
                  self.D*(i + 1) - self.r,self.D*(j + 1) - self.r,fill = self.Board.colors[self.color])
        
    def Move(self,x,y):
        self.Board.canvas.delete(self.id)
        self.id = self.Board.canvas.create_oval(self.D*x + self.r, self.D*y + self.r,
                  self.D*(x + 1) - self.r,self.D*(y + 1) - self.r,fill = self.Board.colors[self.color])

        if y == 0 or y == 7:
            self.vip = True    
        self.Board.Players[self.color].FigureList[(x,y)] = self
        del self.Board.Players[self.color].FigureList[(self.x,self.y)]
        self.x = x
        self.y = y    

    def MakeStep(self,x,y):
        isFree = self.Board.CheckCell(x,y)     
        if isFree >= 0 : # if cell settled by any figure - step impossible
            return 0
        if abs(self.x - x) == 1 and (y - self.y) == 2*self.color - 1:
            self.Move(x,y)
            return 1
        if abs(self.x - x) == 2 and abs(y - self.y) == 2:
            x1 = (self.x + x)//2
            y1 = (self.y + y)//2            
            if self.Board.CheckCell(x1,y1 ) == abs(1 - self.color):
                self.Board.Players[abs(1 - self.color)].DeleteFigure(x1,y1)
                self.Move(x,y)
                return 2

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
        
                
class Player:    #color = 0 - for white, 1 - for black
    def __init__(self,Board,color):
        self.color = color
        self.Board = Board
        self.FigureList = {}
        self.rest = 12    # count of figure
        for i in range(3):
            y = (7 - i)*(1 -color) + i*color
            for j in range((color + i)%2,8,2):
                self.FigureList[(j,y)] = Figure(self.Board,j,y,self.color)

    def DeleteFigure(self,x,y):
        self.Board.canvas.delete(self.FigureList[(x,y)].id)
        del self.FigureList[(x,y)]
        self.rest = self.rest - 1
        
Board = Board()




            
