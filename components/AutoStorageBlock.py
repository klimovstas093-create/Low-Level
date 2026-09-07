from base.cursors import Cursor
from base.functions import save
from base.font import Font
from base.MusicPlayer import MusicPlayer

from components.StorageBlock import StorageBlock, Storage

class AutoStorage(Storage):
    @save
    def add(self, item, count):
            if item in self.dct:
                self.dct[item] += count
            else:
                self.dct[item] = count

            self.dct[item] = min(self.max_size, self.dct[item])

            return True

class AutoStorageBlock(StorageBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = AutoStorage(storage=kwargs.get("storage"), max_size=self.max_storage)