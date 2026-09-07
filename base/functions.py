import applib, traceback
import base.folders as folders
from PyQt6.QtGui import QPixmap, QMovie

TEXTURE_CACHE = {}
ANIMATION_CACHE = {}

def try_int(n):
    if int(n) == float(n):
        return int(n)
    return float(n)

def save(func:callable):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if str((func.__qualname__, e)) not in save.errors:
                folders.folder.log.write(f"<{func.__qualname__}> - {traceback.format_exc()}", type="RuntimeError", set_error=True)
                save.errors.add(str((func.__qualname__, e)))
            else:
                applib.lprint(f"<{func.__qualname__}> - {e}", type="RuntimeError", set_error=True)
    return wrapper
save.errors = set()

@save
def get_texture(name) -> QPixmap:
    if name not in TEXTURE_CACHE:
        path = folders.textures.path(f"{name}.png")
        pixmap = QPixmap(path)
        if pixmap.isNull():
            folders.folder.log.write(f"Texture <{path}> not found", type="TextureCache")
            pixmap = QPixmap(folders.textures.path("404.png"))
        else:
            applib.lprint(f"Loaded: <{path}> ({pixmap.width()}x{pixmap.height()})", type="TextureCache")
        TEXTURE_CACHE[name] = pixmap
    
    return TEXTURE_CACHE[name]

@save
def get_animation(name):
    if name not in ANIMATION_CACHE:
        path = folders.textures.path(f"{name}.gif")
        movie = QMovie(path)
        if not movie.isValid():
            folders.folder.log.write(f"Animation <{path}> not found", type="TextureCache")
            movie = None
        else:
            applib.lprint(f"Loaded animation: <{path}>", type="TextureCache")
        ANIMATION_CACHE[name] = movie
    
    return ANIMATION_CACHE[name]