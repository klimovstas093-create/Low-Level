from base.MusicPlayer import MusicPlayer
from components.AutoStorageBlock import AutoStorageBlock

class Base(AutoStorageBlock):
    def __init__(self, *args, resource_panel=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.panel = resource_panel
        self.tree = self.w.pause_menu.tree

    def on_click(self):
        MusicPlayer.play("click_2")
        self.tree.Parent = None
        self.tree.Show()

    def remove(self): pass

    def update(self, tick, dt):
        if self.panel is not None:
            self.panel.update(self.storage.dict())
        super().update(tick, dt)