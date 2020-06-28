import random
from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

class Chooser(VisualizationApp):
    nextColor = 0

    def __init__(self, choices=['Yes', 'No'], title="Chooser", **kwargs):
        super().__init__(title=title, **kwargs)
        self.title = title
        self.choices = choices
        self.buttons = self.makeButtons()
        self.display()
        self.speedScale.set(SPEED_SCALE_MAX)

    def display(self):
        canvasDimensions = self.widgetDimensions(self.canvas)
        self.center = multiply_vector(canvasDimensions, 0.5)
        self.radius = min(*self.center) * 9 / 10
        self.angle = 0
        self.arrowLength = self.radius * 1 / 2
        self.textRadius = self.radius * 2 / 3
        self.sliceAngle = 360 / len(self.choices)
        self.textFont = ('Arial', 14)
        # go through each item in the list and create a pie slice for it
        delta = (self.radius, self.radius)
        self.slices = [
            self.canvas.create_arc(
               *subtract_vector(self.center, delta),
               *add_vector(self.center, delta),
               start = i * self.sliceAngle, extent = self.sliceAngle,
               fill = drawable.palette[
                   (self.nextColor + i) % len(drawable.palette)],
               style=PIESLICE, tags=['slice']
            )
            for i, names in enumerate(self.choices)]
        self.sliceLabels = [
            [self.canvas.create_text(
                 *add_vector(
                    add_vector(self.center, 
                               rotate_vector((self.textRadius, 0),
                                             (i + 0.5) * self.sliceAngle)),
                    (0, self.textFont[1] * 2 *
                     (j - (len(names) - 1) / 2) * (len(names) - 1) / 2)),
                 text=name, font=self.textFont, fill='black',
                 tags=['label']
            ) for j, name in enumerate(names)]
           for i, names in enumerate(self.choices)
        ]
        # Create a cover circle around the center
        delta = multiply_vector((0.5, 0.5), self.arrowLength)
        self.cover = self.canvas.create_oval(
            *subtract_vector(self.center, delta),
            *add_vector(self.center, delta),
            fill='white')

        # Create arrow to spin on top of pie slices
        self.arrow = self.canvas.create_line(
           *self.center, *add_vector(self.center, (self.arrowLength, 0)),
           arrow="last", width=6, fill="brown4")
        self.angle = 0

        self.window.update()

    def selectedIndex(self):
        return int(self.angle / self.sliceAngle) % len(self.choices)
     
    def makeButtons(self):
        self.chooseButton = self.addOperation(
           "Choose at random", self.spinAndChoose)
        self.addAnimationButtons()
        return [self.chooseButton]
     
    def rotateArrow(self, angle):
        self.angle += angle
        if self.angle > 360:
           self.angle -= 360
        self.canvas.coords(
           self.arrow, *self.center,
           *add_vector(self.center, 
                       rotate_vector((self.arrowLength, 0), self.angle)))
        
    def spinAndChoose(self):
        self.startAnimations()
        waitTime = 0.0005
        decay = 1.15
        increment = random.randrange(25) + 15
        while waitTime < 0.5 and self.animationState != STOPPED:
            steps = max(1, min(10, int(waitTime / 0.01)))
            for step in range(steps):
               self.rotateArrow(increment / steps)
               selected = self.selectedIndex()
               for i, texts in enumerate(self.sliceLabels):
                  for text in texts:
                     self.canvas.itemconfig(
                        text, font=self.textFont + (
                           ('underline', 'bold') if i == selected else ()))
               self.window.update()
               if self.wait(waitTime / steps):
                   break
            waitTime *= decay
        self.setMessage(
           '{} {} chosen!'.format(
              ', '.join(self.choices[selected]),
              'is' if len(self.choices[selected]) == 1 else 'are'))
        self.stopAnimations()

    def enableButtons(self, enable=True):
        for btn in self.buttons:
            btn.config(state=NORMAL if enable else DISABLED)

if __name__ == '__main__':
    choices = (
        [arg.split(',') for arg in sys.argv[1:]] if len(sys.argv) >= 3
        else [ ['Yes'], ['No'], ['Maybe'] ])
    chooser = Chooser(choices)

    chooser.runVisualization()
