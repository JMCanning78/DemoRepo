import random
from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

def abbreviateChoiceName(choice):
    fullname = ', '.join(choice) if isinstance(choice, list) else choice
    if len(fullname) < 20:
        return fullname
    last = None
    name = ''
    for char in fullname:
        cType = characterType(char)
        if cType != last:
            name += char
            last = cType
    return name

def characterType(char):
    return ('A' if char.isalpha() else 
            '1' if char.isdigit() else
            ' ' if char.isspace() else '#')

class Chooser(VisualizationApp):
    nextColor = 0

    def __init__(
            self, choices=['Yes', 'No', 'Maybe'], title="Chooser", **kwargs):
        super().__init__(title=title, **kwargs)
        self.title = title
        self.choices = choices
        self.speedScale.set(self.SPEED_SCALE_MAX)
        self.slices, self.sliceLabels, self.selectors = [], [], []
        self.bottom, self.arrow, self.cover = None, None, None
        self.buttons = self.makeButtons(choices)
        self.display()

    def display(self):
        canvasDimensions = self.widgetDimensions(self.canvas)
        self.center = multiply_vector(canvasDimensions, 0.5)
        self.radius = min(*self.center) * 9 / 10
        delta = (self.radius, self.radius)
        background = 'white'
        if self.bottom is None:
            self.bottom = self.canvas.create_oval(
                *subtract_vector(self.center, delta), 
                *add_vector(self.center, delta), fill = background)
        self.angle = 0
        self.arrowLength = self.radius * 1 / 2
        self.textRadius = self.radius * 2 / 3
        nChoices = sum(selector.get() for selector in self.selectors)
        self.sliceAngle = 360 / max(1, nChoices)
        self.textFont = ('Arial', 14)
        # go through each item in the list and create a pie slice for it
        if self.slices:
            current = [self.canvas.itemconfig(s) for s in self.slices]
            new = [{} for s in self.slices]
            angle = 0
            for i in range(len(self.selectors)):
                current[i]['start'] = float(current[i]['start'][-1])
                current[i]['extent'] = float(current[i]['extent'][-1])
                if i > 0 and current[i]['start'] < (
                        current[i-1]['start'] + current[i-1]['extent']):
                    current[i]['start'] += 360
                on = self.selectors[i].get()
                new[i]['start'] = angle
                new[i]['extent'] = self.sliceAngle if on else 0
                if on:
                    angle += self.sliceAngle
                    
            # Animate change in slices
            self.startAnimations()
            steps = max(1, int(self.sliceAngle) // 2)
            for j in range(steps):
                for i in range(len(self.selectors)):
                    on = self.selectors[i].get()
                    if not on and j == 0:
                        for label in self.sliceLabels[i]:
                            self.canvas.tag_lower(label, self.bottom)
                    start = ((new[i]['start'] - current[i]['start']) * 
                             (j+1) / steps + current[i]['start'])
                    extent = min(359.9,
                                 ((new[i]['extent'] - current[i]['extent']) * 
                                  (j+1) / steps + current[i]['extent']))
                    self.canvas.itemconfig(
                        self.slices[i], start = start, extent = extent)
                    if on:
                        for k, label in enumerate(self.sliceLabels[i]):
                            self.canvas.coords(
                                label, 
                                *self.sliceLabelPosition(
                                    k, len(self.sliceLabels[i]), start, extent))
                            if j == steps - 1:
                                self.canvas.tag_raise(label, self.slices[i])
                self.wait(0.001)
            self.stopAnimations()
        else:
            self.slices = [
                self.canvas.create_arc(
                    *subtract_vector(self.center, delta),
                    *add_vector(self.center, delta),
                    start = i * self.sliceAngle, 
                    extent = min(359.9, self.sliceAngle),
                    fill = drawable.palette[
                        (self.nextColor + i) % len(drawable.palette)],
                    style=PIESLICE, tags=['slice'])
                for i, names in enumerate(self.choices)]
            self.sliceLabels = [
                [self.canvas.create_text(
                    *self.sliceLabelPosition(
                        j, len(names), i * self.sliceAngle, self.sliceAngle),
                    text=name, font=self.textFont, fill='black',
                    tags=['label']
                ) for j, name in enumerate(names)]
                for i, names in enumerate(self.choices)
            ]

        # Create a cover circle around the center
        delta = multiply_vector((0.5, 0.5), self.arrowLength)
        if not self.cover:
            self.cover = self.canvas.create_oval(
                *subtract_vector(self.center, delta),
                *add_vector(self.center, delta),
                fill = background)

        # Create arrow to spin on top of pie slices
        if not self.arrow:
            self.arrow = self.canvas.create_line(
                *self.center, *add_vector(self.center, (self.arrowLength, 0)),
                arrow="last", width=6, fill="brown4", arrowshape=(16, 20, 6))
            self.angle = 0

        self.window.update()

    def sliceLabelPosition(self, textIndex, nTexts, start, extent):
        return add_vector(
            add_vector(self.center, 
                       rotate_vector((self.textRadius, 0), start + extent / 2)),
            (0,
             self.textFont[1] * (textIndex - (nTexts - 1) / 2) * (nTexts - 1)))
    
    def selectedIndex(self):
        while self.angle >= 360:
            self.angle -= 360
        for i in range(len(self.selectors)):
            if self.selectors[i].get():
                slice = self.canvas.itemconfig(self.slices[i])
                start = float(slice['start'][-1])
                extent = float(slice['extent'][-1])
                if start <= self.angle and self.angle - start < extent:
                    return i
     
    def makeButtons(self, choices):
        self.chooseButton = self.addOperation(
           "Choose at random", self.spinAndChoose)
        buttons = [self.chooseButton]
        self.selectors = []
        for choice in choices:
           stateVar = IntVar()
           self.selectors.append(stateVar)
           stateVar.set(1)
           buttons.append(self.addOperation(
              abbreviateChoiceName(choice), self.display, 
              buttonType=Checkbutton, variable=stateVar))
        return buttons
    
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
        while waitTime < 0.5:
            steps = max(1, min(10, int(waitTime / 0.01)))
            for step in range(steps):
               self.rotateArrow(increment / steps)
               selected = self.selectedIndex()
               for i, texts in enumerate(self.sliceLabels):
                  for text in texts:
                     self.canvas.itemconfig(
                        text, font=self.textFont + (
                           ('underline', 'bold') if i == selected else ()))
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
