from components.Block import Block
import PyQt6.QtGui as QtGui
from PyQt6.QtGui import QColor

class PowerBlock(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parents:set[PowerBlock] = set()
        self.max_energy = self.states.get("max_energy", 0.1)
        self.lines = set()
        self.energy = 0

    def update(self, tick, dt):
        for block in self.parents:
            if block.energy < self.energy:
                energy = (self.energy-block.energy)/2
                energy = min(energy, block.max_energy-block.energy)
                block.energy += energy
                self.energy -= energy
        opacity = max(min(self.energy/0.1, 0.9), 0.1)
        for line in self.lines:
            line.setOpacity(opacity)
        super().update(tick, dt)

    def on_click(self):
        print(f"parents: {self.parents}, energy: {self.energy}")

    def place(self):
        if super().place():
            for block in self.w.blocks:
                if block is self:
                    continue
                if hasattr(block, "energy"):
                    if (abs(block.x-self.x)**2)+(abs(block.y-self.y)**2) <= 75:
                        self.parents.add(block)
                        block.parents.add(self)
                        line = self.w.scene.addLine((block.x+block.size[0]/2)*32, (block.y+block.size[1]/2)*32, (self.x+self.size[0]/2)*32, (self.y+self.size[0]/2)*32, QtGui.QPen(QColor(255, 255, 0), 5))
                        line.setZValue(40)
                        line.setOpacity(max(min(self.energy/0.1, 1), 0.1))
                        self.lines.add(line)
                        block.lines.add(line)

    def remove(self, sound=True):
        for line in self.lines:
            self.w.scene.removeItem(line)
        for block in self.parents:
            block.parents.remove(self)
            for line in self.lines:
                block.lines.discard(line)
        self.energy = 0
        self.parents = set()
        super().remove(sound)
        