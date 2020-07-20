import random, argparse
from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

def abbreviateChoiceName(choice, maxChoiceWidth=20):
    fullname = ', '.join(choice) if isinstance(choice, list) else choice
    if len(fullname) < maxChoiceWidth:
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
            self, choices=['Yes', 'No', 'Maybe'], title="Chooser",
            maxChoiceWidth=40, minSpeed=360, maxSpeed=1200, decay=0.985, 
            allowSpeedIndicator=True, **kwargs):
        super().__init__(title=title, **kwargs)
        self.title = title
        self.choices = choices
        self.maxChoiceWidth = maxChoiceWidth
        self.minSpeed = minSpeed
        self.maxSpeed = maxSpeed
        self.decay = decay
        self.speedScale.set(self.SPEED_SCALE_MAX)
        self.slices, self.sliceLabels, self.selectors = [], [], []
        self.bottom, self.arrow, self.cover = None, None, None
        self.buttons = self.makeButtons(choices, allowSpeedIndicator)
        self.display()

    def display(self):
        canvasDimensions = self.widgetDimensions(self.canvas)
        self.center = multiply_vector(canvasDimensions, 0.5)
        self.radius = min(*self.center) * 98 / 100
        delta = (self.radius, self.radius)
        background = 'white'
        if self.bottom is None:
            self.bottom = self.canvas.create_oval(
                *subtract_vector(self.center, delta), 
                *add_vector(self.center, delta), fill = background)
        self.angle = 0
        self.arrowLength = self.radius * 1 / 2
        self.textRadius = self.radius * 0.65
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
     
    def makeButtons(self, choices, allowSpeedIndicator=True):
        self.chooseButton = self.addOperation(
           "Choose at random", self.spinAndChoose)
        buttons = [self.chooseButton]
        self.showSpeed = IntVar()
        self.showSpeed.set(0)
        if allowSpeedIndicator:
            self.showSpeed.set(1)
            self.showSpeedButton = self.addOperation(
                "Show speed", lambda: 0, buttonType=Checkbutton, 
                variable=self.showSpeed)
            buttons.append(self.showSpeedButton)
            
            # For testing
            if False:
                self.addOperation(
                    "Spin at {}".format(self.minSpeed),
                    lambda: self.spinAndChoose(self.minSpeed))
                self.addOperation(
                    "Spin at {}".format(self.maxSpeed),
                    lambda: self.spinAndChoose(self.maxSpeed))
        self.selectors = []
        for choice in choices:
           stateVar = IntVar()
           self.selectors.append(stateVar)
           stateVar.set(1)
           buttons.append(self.addOperation(
              abbreviateChoiceName(choice, self.maxChoiceWidth), self.display, 
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
        
    def spinAndChoose(self, speed=None):
        self.startAnimations()
        waitTime = 0.01
        if speed is None:
            speed = random.randrange(self.minSpeed, self.maxSpeed)
        if self.showSpeed.get():
            speedIndicator = self.canvas.create_text(
                30, 30, text="Speed = {}".format(speed), anchor=NW)
        while speed * waitTime > 0.1:
            self.rotateArrow(speed * waitTime)
            selected = self.selectedIndex()
            for i, texts in enumerate(self.sliceLabels):
                for text in texts:
                    self.canvas.itemconfig(
                        text, font=self.textFont + (
                            ('underline', 'bold') if i == selected else ()))
            if self.wait(waitTime):
                break
            speed *= self.decay
            if self.showSpeed.get():
                self.canvas.itemconfigure(
                    speedIndicator, text = "Speed = {:5.2f}".format(speed))
        self.setMessage(
           '{} {} chosen!'.format(
              ', '.join(self.choices[selected]),
              'is' if len(self.choices[selected]) == 1 else 'are'))
        if self.showSpeed.get():
            self.canvas.delete(speedIndicator)
        self.stopAnimations()

    def enableButtons(self, enable=True):
        for btn in self.buttons:
            btn.config(state=NORMAL if enable else DISABLED)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Visual application to select a choice randomly using a '
        'spinner.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'choices', nargs='*', default=[ 'Yes', 'No', 'Maybe' ],
        metavar='CHOICE',
        help='Choice description.  Use comma to separate lines.')
    parser.add_argument(
        '--min-speed', default=600, type=int,
        help='Minimum angular speed of spin at start in degrees / second')
    parser.add_argument(
        '--max-speed', default=1800, type=int,
        help='Maximum angular speed of spin at start in degrees / second')
    parser.add_argument(
        '-d', '--decay', default=0.985, type=float,
        help='Decay rate of spin speed.')
    parser.add_argument(
        '-v', '--speed-visible', default=False, action='store_true',
        help='Add button to allow speed to visible while spinning')
    parser.add_argument(
        '-m', '--max-choice-width', default=40, type=int,
        help='Maximum number of characters in choice button label.')

    args = parser.parse_args()

    args.choices = [choice.split(',') for choice in args.choices]
    chooser = Chooser(args.choices, maxChoiceWidth=args.max_choice_width,
                      minSpeed=args.min_speed, maxSpeed=args.max_speed,
                      decay=args.decay, allowSpeedIndicator=args.speed_visible)

    chooser.runVisualization()
