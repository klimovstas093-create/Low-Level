from components.StorageBlock import StorageBlock
from base.functions import save

class Conveyor(StorageBlock):
    def __init__(self, w, x, y, name, **kwargs):
        if "max_storage" in kwargs:
            del kwargs["max_storage"]
        super().__init__(w, x, y, name, max_storage=1, **kwargs)
        self.direction_start = self.states.get("direction_start")
        self.direction_end = self.states.get("direction_end")

    @save
    def update(self, tick, dt):
        if tick % 10 != 0:
            return
        
        start_block = self.w.block_map.get((self.x - self.direction_start[0], self.y - self.direction_start[1]))
        end_block = self.w.block_map.get((self.x - self.direction_end[0], self.y - self.direction_end[1]))

        if start_block is not None:
            for block in start_block:
                if hasattr(block, "storage"):
                    if len(block.storage) != 0:
                        for item in block.storage.dict():
                            if self.storage.add(item, 1):
                                block.storage.reduce(item, 1)
                                break

        if end_block is not None:
            for block in end_block:
                if hasattr(block, "storage"):
                    if hasattr(block, "direction_start"):
                        if self.direction_start == block.direction_start and self.direction_end == block.direction_end:
                            return
                    if len(self.storage) != 0:
                        for item in self.storage.dict():
                            if block.storage.add(item, 1):
                                self.storage.reduce(item, 1)
                                break
