import tkinter
import threading
import time

HIGHLIGHT_COLOUR = "#FF00FF"
BACKGROUND_COLOUR = "#000000"
POPULATED_COLOUR = "#FFFFFF"

class R90:
    def __init__(self, width, height, scale):
        self.width = width
        self.height = height
        self.scale = scale

        self.running = True
        self.halt = False
        self.paused = True
        self.delay = 1

        self.constants = []
    
        self.gui = R90GUI(self, width, height, scale)
        self.gui.update()

        self.makeTable()

        self.start()

    def start(self):
        t = threading.Thread(target=self.clock)
        t.start()
        self.gui.window.mainloop()

    #Construction funcs       
    def makeTable(self):
        self.table = {}
        for x in range(self.width):
            for y in range(self.height):
                self.table[(x, y)] = False

    #Keybinded functions
    def reset(self):
        if not self.halt and self.paused:
            self.halt = True
            self.constants = []
            self.makeTable()
            self.gui.reset()
            self.halt = False
        
    def togglePause(self):
        if not self.halt:
            self.paused = not self.paused
            self.gui.update()
            for constant in self.constants:
                self.gui.changeColour(
                    constant[0], constant[1],
                    HIGHLIGHT_COLOUR if self.paused else POPULATED_COLOUR)
            for x in range(0, self.width):
                for y in range(0, self.height):
                    self.gui.changeHighlightColour(
                        x,y,
                        HIGHLIGHT_COLOUR if self.paused else "")

    def changeSpeed(self, increment):
        if round(self.delay+increment, 2) > 0 and round(self.delay+increment, 2) <= 2:
            self.delay = round(self.delay+increment, 2)
            self.gui.update()

    def togglePop(self, event):
        if (not self.halt) and self.paused:
            x = int(event.x/self.scale)
            y = int(event.y/self.scale)

            if x >= 0 and x < self.width and y >= 0 and y < self.height:
                self.table[(x, y)]= not self.table[(x, y)]
                
                if self.table[(x,y)]:
                    self.constants.append((x, y))
                    self.gui.changeColour(x, y, HIGHLIGHT_COLOUR)
                else:
                    self.constants.remove((x, y))
                    self.gui.changeColour(x, y, BACKGROUND_COLOUR)

    #Update funcs
    def clock(self):
        while self.running:
            if (not self.paused) and (not self.halt):
                self.tick()
            time.sleep(self.delay)

    def tick(self):        
        nextTable = {}
        
        for x in range(self.width):
            for y in range(self.height):
                if not (x, y) in self.constants:
                    if self.table.get((x-1, y-1), False) != self.table.get((x+1, y-1), False):
                        nextTable[(x, y)] = True
                        if nextTable[(x, y)] != self.table[(x, y)]:
                            self.gui.changeColour(x, y, POPULATED_COLOUR)
                    else:
                        nextTable[(x, y)] = False
                        if nextTable[(x, y)] != self.table[(x, y)]:
                            self.gui.changeColour(x, y, BACKGROUND_COLOUR)
                else:
                    nextTable[(x, y)] = True
                    
        self.gui.window.update()
        self.table = nextTable

class R90GUI:
    def __init__(self, game, width, height, scale):
        self.game = game

        self.window = tkinter.Tk()
        self.window.geometry("{0}x{1}".format(
            self.game.width*self.game.scale,
            self.game.height*self.game.scale+40))
        self.window.resizable(False, False)

        self.canvas = tkinter.Canvas(
            self.window,
            width=self.game.width*self.game.scale,
            height=self.game.height*self.game.scale)
        self.canvas.grid(row=0, column=0, columnspan=4, sticky="nesw")

        self.makeGrid()

        self.pauseButton = tkinter.Button(
            self.window,
            text="Pause (Return)",
            command=self.game.togglePause)
        self.pauseButton.grid(row=1,column=0,sticky="nesw")

        self.clearButton = tkinter.Button(
            self.window,
            text="Clear (Backspace)",
            command=self.game.reset)
        self.clearButton.grid(row=1,column=1,sticky="nesw")

        self.slowButton = tkinter.Button(
            self.window,
            text="Delay (-)",
            command=lambda: self.game.changeSpeed(-0.05))
        self.slowButton.grid(row=1,column=2,sticky="nesw")

        self.fastButton = tkinter.Button(
            self.window,
            text="Delay (+)",
            command=lambda: self.game.changeSpeed(0.05))
        self.fastButton.grid(row=1,column=3,sticky="nesw")

        self.window.grid_columnconfigure(0, weight=4)
        self.window.grid_columnconfigure(1, weight=4)
        self.window.grid_columnconfigure(2, weight=1)
        self.window.grid_columnconfigure(3, weight=1)
        self.window.grid_rowconfigure(1, weight=1)

        self.canvas.bind("<Button-1>", lambda a: self.game.togglePop(a))
        self.canvas.bind("<B1-Motion>", lambda a: self.game.togglePop(a))
        self.window.bind("<Return>", lambda a: self.game.togglePause())
        self.window.bind("-", lambda a: self.game.changeSpeed(-0.05))
        self.window.bind("+", lambda a: self.game.changeSpeed(0.05))
        self.window.bind("<BackSpace>", lambda a: self.game.reset())

        self.window.protocol("WM_DELETE_WINDOW",self.close)

    #
    def close(self):
        self.game.running = False
        self.window.destroy()
        quit()

    #Construction funcs
    def makeGrid(self):
        self.boxes = {}
        
        for x in range(0, self.game.width):
            for y in range(0, self.game.height):
                self.boxes[(x, y)] = self.canvas.create_rectangle(
                    x*self.game.scale,
                    y*self.game.scale,
                    (x*self.game.scale)+self.game.scale,
                    (y*self.game.scale)+self.game.scale,
                    fill=BACKGROUND_COLOUR,
                    activefill=HIGHLIGHT_COLOUR)

    #Update funcs
    def update(self):
        if self.game.paused:
            self.window.wm_title("{0}s | PAUSED".format(self.game.delay))
            self.pauseButton.config(text="Play (Return)")
            self.clearButton.config(state=tkinter.NORMAL)
        else:
            self.window.wm_title("{0}s".format(self.game.delay))
            self.pauseButton.config(text="Pause (Return)")
            self.clearButton.config(state=tkinter.DISABLED)
            
    def changeColour(self, x, y, col):
        self.canvas.itemconfig(self.boxes[(x, y)], fill=col)

    def changeHighlightColour(self, x, y, col):
        self.canvas.itemconfig(self.boxes[(x, y)], activefill=col)

    def reset(self):
        if self.game.paused:
            for x in range(self.game.width):
                for y in range(self.game.height):
                    self.canvas.itemconfig(self.boxes[(x, y)], fill=HIGHLIGHT_COLOUR)
                self.canvas.update()
                
            time.sleep(0.1)
            for x in range(self.game.width):
                for y in range(self.game.height):
                    self.canvas.itemconfig(self.boxes[(x, y)], fill=BACKGROUND_COLOUR)
                self.canvas.update()

main = R90(64, 64, 8)
