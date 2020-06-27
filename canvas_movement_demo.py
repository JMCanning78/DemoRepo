
from tkinter import *
import random

WIDTH = 400
HEIGHT = 400

window = Tk()

buttonFrame = Frame(window, bg="white")
buttonFrame.pack(side=BOTTOM, fill=X)
circleButton = Button(
   buttonFrame, text="Move Shapes", command= lambda: beginMovement())
circleButton.pack()
msg = Label(buttonFrame, text="")
msg.pack(side=BOTTOM)

canvas = Canvas(window, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

canvas.create_rectangle(
   105, 160, 145, 190, fill="yellow", tags="rectangle")
canvas.create_text(
   125, 175, text="text 2", tags=("rectangle", "text"))
canvas.create_oval(
   100, 150, 150, 200, fill="red", tags=("red", "circle"))
canvas.create_oval(
   175,  75, 225, 125, fill="blue", tags=("blue", "circle"))
canvas.create_oval(
   175, 225, 225, 275, fill="purple", tags=("purple", "circle"))
canvas.create_oval(
   250, 150, 300, 200, fill="green", tags=("green", "circle"))
canvas.create_rectangle(50, 90, 100, 175, tags="rectangle")

def beginMovement():
   msg["text"] = ""
   for oval in canvas.find_withtag("circle"):
      x, y = genRandMove(oval)
      canvas.move(oval, x, y)

maxMove = 50

# Genrate a random movement that does not move the oval off the screen
def genRandMove(oval):
   x = random.randint(-maxMove, maxMove)
   y = random.randint(-maxMove, maxMove)
   # Oval coords are (x1, y1, x2, y2) of the bounding box
   coords = canvas.coords(oval)

   # Make sure the x and y coordinates do not go off the canvas
   while coords[2] + x > WIDTH or coords[0] + x < 0:
      x = random.randint(-maxMove, maxMove)
   while coords[3] + y > HEIGHT or coords[1] + y < 0:
      y = random.randint(-maxMove, maxMove)

   return x,y

# Callback routines to handle click and drag movements on circles
move_start, move_items = (), ()

def start_move(event):
   global move_start, move_items
   move_start = (event.x, event.y)
   move_items = canvas.find_closest(move_start[0], move_start[1], 1)
   text = "Item(s) to move: "
   for i, item in enumerate(move_items):
      text += ((': ' if i == 0 else ', ') +
               canvas.itemconfig(item, 'fill')[-1] + 
               " oval")
   msg['text'] = text

def move(event):
   global move_start, move_items
   dx, dy = event.x - move_start[0], event.y - move_start[1]
   for item in move_items:
      canvas.move(item, dx, dy)
   move_start = (event.x, event.y)

# Attach callbacks for dragging circles
canvas.tag_bind("circle", '<Button-1>', start_move)
canvas.tag_bind("circle", '<B1-Motion>', move)

window.mainloop()
