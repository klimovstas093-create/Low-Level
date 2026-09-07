from __future__ import annotations

from components.Block import Block

from base.cursors import Cursor
from base.functions import save
from base.font import Font
from base.MusicPlayer import MusicPlayer

class Storage:
    def __init__(self, storage:dict=None, max_size=100, **kwargs):
        if storage is None:
            self.dct = {}
        else:
            self.dct = storage
        self.max_size = max_size

    @save
    def add(self, item, count):
        if count == 0:
            return True
        if item in self.dct:
            self.dct[item] += count
        else:
            self.dct[item] = count

        if self.dct[item] > self.max_size: 
            self.dct[item] = self.max_size
            return False
        return True

    @save
    def empty(self):
        if len(self.dict()) == 0:
            return True
        return False
    
    @save
    def reduce(self, item, count):
        if item in self.dct:
            self.dct[item] -= count
        else:
            return False
        
        if self.dct[item] < 0: 
            del self.dct[item]
            return False
        return True

    def dict(self):
        return self.dct

    def show(self):
        if len(self.dict()) == 0:
            return "Empty"
        
        ex = ""

        for name, value in self.dict().items():
            ex += f"{name}: {value}\n"

        return ex[:-1]
    
    def __eq__(self, f:Storage):
        return self.dict() == f.dict()

    def __len__(self):
        return len(self.dict())

class StorageBlock(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_storage = self.states.get("max_storage", 10)
        self.storage = Storage(storage=kwargs.get("storage"), max_size=self.max_storage)

        self.center = self.w.scene.addText("Empty")
        self.center.setPos((self.x+self.size[0]/2)*32-25, (self.y+self.size[1])*32)
        self.center.setZValue(40)
        self.center.setFont(Font.Bold)
        self.center.setOpacity(0)

        self.old_lst = []
    
    def accept(self, item, count=1):
        return self.storage.add(item, count) == 0

    def draw(self):
        super().draw()
        self.pixmap_item.setCursor(Cursor.Hand)

    def update(self, tick, dt):
        super().update(tick, dt)

        if self.old_lst != self.storage.dict():
            self.old_lst = self.storage.dict().copy()
            text = self.storage.show()
            self.center.setPlainText(text)

    def remove(self):
        self.w.scene.removeItem(self.center)
        super().remove()

    def on_click(self):
        self.center.setOpacity(1 if self.center.opacity() == 0 else 0)
        MusicPlayer.play("click_1")
