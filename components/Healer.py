from components.PowerBlock import PowerBlock
from base.functions import save, get_texture

class Healer(PowerBlock):
    def __init__(self, *args, **kwargs):
        self.heal_timer = 0
        self.effects = set()
        super().__init__(*args, **kwargs)
        
        self.cells = []
        for x in range(-5, 6): 
            for y in range(-5, 6):
                if x*x + y*y <= 25:
                    self.cells.append((self.x+x, self.y+y))

    @save
    def update(self, tick, dt):
        super().update(tick, dt)
        
        self.heal_timer += dt
        if self.heal_timer >= 1.0:
            self.heal_timer = 0
            
            if self.energy > 0.01:
                for x, y in self.cells:
                    block = self.w.get_block_at(x, y)
                    if block is not None:
                        if block.hp < block.states["hardness"]:
                            obj = self.w.scene.addPixmap(get_texture("core_1"))
                            obj.setPos((self.x+self.size[0]/2)*32-8, (self.y+self.size[1]/2)*32-8)
                            obj.setZValue(40)
                            obj.setOpacity(0.6)
                            self.energy -= 0.02
                            block.hp += 0.1
