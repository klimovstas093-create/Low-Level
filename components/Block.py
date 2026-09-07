from __future__ import annotations

import base.folders as folders
import applib, random
import base.functions as func
from base.MusicPlayer import MusicPlayer
from PyQt6.QtWidgets import QGraphicsItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.GameWindow import GameWindow

blocks = folders.mainfolder.read("block_config.json", type="json")

class Block:
    @func.save
    def __init__(self, w:GameWindow, x, y, name:str, team, *args, **kwargs):
        if x >= w.sizeX or y >= w.sizeY or x < 0 or y < 0:
            self.exists = False
            folders.folder.log.write(f"Block <{name}(x:{x}, y:{y})> Located behind the world", type="BlockData")
        self.x = x
        self.y = y
        self.name = name
        self.team = team
        self.exists = True
        self.states = blocks.get(self.name, None)
        if self.states is None:
            applib.lprint(f"States for {self} not found in <{folders.mainfolder.path("block_config.json")}>", type="BlockWarning")
            self.states = blocks["none"]

        self.type = self.states["type"]
        self.centered = self.states.get("centered", False)
        self._hp = self.states.get("hardness", 0)

        if self._hp == 0:
            self._hp = -1
        self.w = w
        
        self.temperature = self.w.temperature
        self.pixmap = func.get_texture(self.name)
        self.size = (self.pixmap.width()//32, self.pixmap.height()//32)

        for name, value in kwargs.items():
            self.__setattr__(name, value)

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, f):
        if self._hp == -1:
            return
        if f <= 0:
            self.remove()
        self._hp = min(f, self.states.get("hardness", -1))

    def __str__(self):
        return self.name
    
    def draw(self):
        if self.exists:
            self.pixmap_item = self.w.scene.addPixmap(self.pixmap)
            if self.centered:
                self.pixmap_item.setPos((self.x-(self.size[0]/4))*32, (self.y-(self.size[1]/4))*32)
            else:
                self.pixmap_item.setPos(self.x*32, self.y*32)
            self.pixmap_item.setZValue(self.states["z"])  
            self.pixmap_item.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def get_info(self):
        return {
            "x": self.x,
            "y": self.y,
            "hp": self.hp
        }

    def on_click(self):
        print(self._hp)
    
    def get_occupied_cells(self):
        if self.centered:
            return {(self.x, self.y)}
        cells = set()
        for dx in range(self.size[0]):
            for dy in range(self.size[1]):
                cells.add((self.x + dx, self.y + dy))
        return cells

    def get_around(self):
        cells = set()
        for cell in self.get_occupied_cells():
            for coef in ((1, 0), (-1, 0), (0, 1), (0,-1)):
                cells.add((cell[0]+coef[0], cell[1]+coef[1]))
        return cells 

    @func.save
    def place(self):
        for cell in self.get_occupied_cells():
            blocks = self.w.block_map.get(cell)
            if blocks is None:
                continue
            for block in blocks:
                if block is self or block.states["z"] < 20:
                    continue
                return False
        self.draw()
        MusicPlayer.play("place", volume=0.7)
        self.w.append_block(self)
        self.w.scene.update()
        return True

    @func.save
    def remove(self, sound=True):
        if not folders.folder.config["devmode"] and self.states["z"] < 20:
            return
        self.exists = False
        if sound:
            MusicPlayer.play(random.choice(["destruction_1", "destruction_2"]), volume=0.7)
        if hasattr(self, 'pixmap_item'):
            self.w.scene.removeItem(self.pixmap_item)
            self.w.scene.update()

        self.w.remove_block(self)

    def info(self):
            output = ""
            for name, value in self.__dict__.items():
                output += f"{name}: {value}, "
            return f"<{type(self).__name__}({output[:-2]})>"

    def update(self, tick, dt):
        if self.states.get("relief", False) or self.temperature == 0:
            return

        for coords in self.get_around():
            block:Block = self.w.get_block_at(*coords)
            if block is None:
                if self.temperature > self.w.temperature:
                    self.temperature -= 0.02
                continue

            if abs(self.temperature - block.temperature) < 0.1:
                continue

            delta = (self.temperature - block.temperature)*0.1
            block.temperature += delta
            self.temperature -= delta

    def __repr__(self):
        return f"TEMPERATURE: {self.temperature}, <{type(self).__name__}>"