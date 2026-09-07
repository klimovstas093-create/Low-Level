from __future__ import annotations

from PyQt6 import QtWidgets
from PyQt6.QtGui import QBrush, QColor, QPainter, QIcon
from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QListWidget, QListWidgetItem

from PyQt6.QtOpenGLWidgets import QOpenGLWidget

from PyQt6 import QtCore

from base.functions import save, get_texture
from base.font import Font
from base.cursors import Cursor
from base.MusicPlayer import MusicPlayer
from base.folders import folder, saves

from components.Block import Block, blocks
from components.Entity import Entity, entities

from ui.PauseMenu import PauseMenu

import terminal, json, time, os, applib, importlib, math

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from components.StorageBlock import StorageBlock
    from ui.MainWindow import MainWindow

components = {}

for module in applib.Storage("components").list():
    if not module.endswith(".py"):
        continue
    name = module[:-3]
    mod = importlib.import_module(f"components.{name}")
    components[name] = getattr(mod, name)

round = math.floor

class SectorManager:
    @staticmethod
    def save(world:GameWindow, filename):
            self = world
            data = []
            folder.plugins.call("save", filename)
            for coord, blocks in self.block_map.items():
                for block in blocks:
                    if not block.exists:
                        continue
                    entry = {}
                    for atr, value in block.__dict__.items():
                        if type(value) == tuple:
                            value = list(value)
                        try:
                            json.dumps(value)
                        except Exception: pass
                        else:
                            entry[atr] = value
                    data.append(entry)
        
            for entity in self.entities:
                            if not entity.exists:
                                continue
                            entry = {}
                            for atr, value in entity.__dict__.items():
                                if type(value) == tuple:
                                    value = list(value)
                                try:
                                    json.dumps(value)
                                except Exception:
                                    value = repr(value)
                                else:
                                    entry[atr] = value
                            data.append(entry)
                
            with open(saves.path(filename), "w", encoding="UTF-8") as f:
                json.dump(data, f, indent=2)
            folder.log.write(f"Sector saved in <{saves.path(filename)}>", type="StartInfo")

    @staticmethod
    def load(world, filename):
            for block in world.blocks.copy():
                block.remove()
            for entity in world.entities.copy():
                entity.remove()
            folder.plugins.call("load", filename)
            if not os.path.exists(saves.path(filename)):
                folder.log.write("File of sector not found", type="StartWarning", set_error=1)
                return
            try:
                with open(saves.path(filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                for b in data:
                    a = b.copy()
                    block_type_name = a.pop("type")

                    block_class = components[block_type_name]

                    if hasattr((obj:=block_class(world, **a)), "place"):
                        obj.place()
                folder.log.write(f"Sector loaded from <{saves.path(filename)}>", type="StartInfo")

            except (json.JSONDecodeError, KeyError) as e:
                folder.log.write(f"Error reading the sector file: <{e}>", type="StartError", set_error=True)
    
class GameWindow(QWidget):
    @save
    def __init__(self, window:MainWindow, sizeX=256, sizeY=256, devmode:bool=folder.config["devmode"], imagepath="image.jpg"):
        super().__init__()
        self.setWindowTitle("Low-Level")

        self.MainWindow = window
        self.temperature = 20
        
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, sizeX*32, sizeY*32))
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.blocks = set()
        self.block_map:dict = {}

        self.devmode = devmode

        self.opened = ["drill", "conveyor_down", "conveyor_up", "conveyor_left", "conveyor_right"]

        self.Base:StorageBlock = None

        self.entities = set()
        self.team = "PlayerTeam"
        
        background_brush = QBrush(QColor(30, 30, 30))
        self.scene.setBackgroundBrush(background_brush)

        self.view = QGraphicsView(self.scene, self)
        self.view.setViewport(QOpenGLWidget())
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)

        self.view.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
        self.view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)

        self.view.setCursor(Cursor.Cursor)
        
        self.keys_pressed = set()

        self.scale = 1

        self.trm = terminal.init(self, cmd=self.cmdparser)
        self.trm.output.append(f"[START] {folder.version}\n")

        folder.plugins.init()
        folder.plugins.call("pre_start", self)

        self.view.wheelEvent = self.wheelEvent

        self.placing_block = "drill"

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_tick)
        self.timer.start(16)
        self.tick = 0

        self.view.setMouseTracking(True)

        central = QtWidgets.QHBoxLayout()

        central.addWidget(self.view)

        self.tool_panel = QListWidget()
        self.tool_panel.setIconSize(QtCore.QSize(64, 64))
        self.tool_panel.setGridSize(QtCore.QSize(96, 196))
        self.tool_panel.setViewMode(QListWidget.ViewMode.IconMode)
        self.tool_panel.setFlow(QListWidget.Flow.TopToBottom) 
        self.tool_panel.setWrapping(False)
        self.tool_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tool_panel.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.tool_panel.setDragEnabled(False)
        self.tool_panel.setFont(Font.Bold)
        self.tool_panel.setFixedWidth(200)
        self.tool_panel.setCursor(Cursor.Hand)

        self.last_time = 0

        if not self.devmode:
            self.tool_names = {}
            for clt in [blocks, entities]:
                for name, value in clt.items():
                    if not value.get("relief", False) and not value.get("ignore_on_editor", False):
                        self.tool_names[name] = value
        else:
            self.tool_names = blocks
            self.tool_names.update(entities)

        self.tool_panel.setCurrentRow(0)

        self.update_tool_panel()

        self.target_scale = 1

        self.tool_panel.currentItemChanged.connect(self.on_tool_changed)

        central.addWidget(self.tool_panel)

        self.setLayout(central)

        self.vx = 0
        self.vy = 0
        self.max_speed = 10
        self.acceleration = 4

        self.pause_menu = PauseMenu(self)
        self.menu_active = None

    def update_tool_panel(self):
        self.tool_panel.clear()
        
        coef = folder.config.get("craft_coef", 1)
                
        for name, i in self.tool_names.items():
                    if not self.devmode:
                        if name not in self.opened:
                            continue
                    
                    pixmap = get_texture(name)
                    icon = QIcon(pixmap)
          
                    cost:dict = i.get("cost")
                    exc = ""
                    if cost is not None:
                        for namef, value in cost.items():
                            exc += f"\n{namef} x{int(value*coef)}"
        
                    item = QListWidgetItem(icon, f"{name.replace("_", " ").title()}{exc}")
                    item.setData(Qt.ItemDataRole.UserRole, name)
                    item.setToolTip(f"{name.replace("_", " ").title()}{exc}")

                    self.tool_panel.addItem(item)

    def remove_block(self, block:Block):
        if block in self.blocks:
            self.blocks.remove(block)
        for xcoord, ycoord in block.get_occupied_cells():
            if (xcoord, ycoord) in self.block_map:
                blocks:list = self.block_map.get((xcoord, ycoord))
                if block in blocks:
                    blocks.remove(block)
                if len(blocks) == 0:
                    del self.block_map[(xcoord, ycoord)]

        if not self.devmode:
            cost:dict = block.states.get("cost")
            coef = folder.config.get("craft_coef", 1)
            if cost is not None and self.Base is not None:
                for name, value in cost.items():
                    self.Base.storage.add(name, int(value*coef))

    def append_block(self, block:Block):
        if not block.states.get("relief", False):
            self.blocks.add(block)

        for xcoord, ycoord in block.get_occupied_cells():
            if (blocks:=self.block_map.get((xcoord, ycoord))) is not None:
                self.block_map[(xcoord, ycoord)] = [block, *blocks]
                continue
            self.block_map[(xcoord, ycoord)] = [block]

    def remove_entity(self, entity:Entity):
        pass

    def blur(self, radius=8):
        self.tool_panel.insertItems
        for item in self.scene.items():
            blur = QtWidgets.QGraphicsBlurEffect()
            blur.setBlurRadius(radius)
            item.setGraphicsEffect(blur)
        self.scene.update()

    def unblur(self):
        for item in self.scene.items():
            item.setGraphicsEffect(None)
        self.scene.update()

    @save
    def closeEvent(self, event):
        MusicPlayer.play("click_2")
        self.pause_menu.Back()
        self.MainWindow.MenuWindow.show()
        event.accept()

    def get_block_at(self, x, y):
        blocks = self.block_map.get((x, y), None)
        if blocks is not None:
            return max(blocks, key=lambda ex: ex.states["z"])

    @save
    def on_tool_changed(self, current, f):
        self.view.setFocus()
        MusicPlayer.play("click_1")
        self.placing_block = current.data(Qt.ItemDataRole.UserRole)

    @save
    def cmdparser(self, cmd:str):
                match cmd.split():
                    case ["place", x, y, type]:
                        try:
                            if Block(self, int(x), int(y), type).place():
                                self.trm.write(f"<{cmd}>: Success\n")
                            else:
                                self.trm.write(f"<{cmd}>: Block is occupied\n")
                        except Exception:
                            self.trm.write(f"<{cmd}>: An error has occurred, perhaps you have entered incorrect coordinates or a wrong block name\nFormat: place x, y, name\n")
                        return
                    case ["tp", x, y]:
                        try:
                            x=float(x)*32
                            y=float(y)*32
                            if x < 0 or y < 0:
                                self.trm.write(f"<{cmd}>: Invalid coordinates as <{x//32}, {y//32}>\n")
                                return
                            self.view.centerOn(x, y)
                            self.trm.write(f"<{cmd}>: Success\n")
                        except Exception:
                            self.trm.write(f"<{cmd}>: An error has occurred, perhaps you have entered incorrect coordinates\nFormat: tp (x, y)\n")
                        return
                    case ["view"]:
                        folder.view()
                    case ["switch", "team"]:
                        if self.team == "PlayerTeam":
                            self.team = "EnemyTeam"
                        else:
                            self.team = "PlayerTeam"
                        print(f"Team switched to <{self.team}>")
                    case ["save", name]:
                        self.save(f"{name}.json")
                    case ["load", name]:
                        self.load(f"{name}.json")
                    case _:
                        self.trm.write(f"Unknown command as <{cmd}>\n")

    @save
    def mousePressEvent(self, event):
        if self.menu_active is not None:
            return
        scene_pos = self.view.mapToScene(event.pos())
        x, y = round(scene_pos.x()/32), round(scene_pos.y()/32)
        
        if event.button() == Qt.MouseButton.LeftButton:
            existing = self.get_block_at(x, y)
            if existing and existing.states["z"] >= 20:
                if hasattr(existing, 'on_click'):
                    existing.on_click()
            else:
                scene_pos = self.view.mapToScene(event.pos())
                x, y = round(scene_pos.x()/32), round(scene_pos.y()/32)

                type_name = None
                cost = None

                if self.placing_block in blocks:
                    type_name = blocks[self.placing_block].get("type")
                    cost = blocks[self.placing_block].get("cost")

                if self.placing_block in entities:
                    type_name = entities[self.placing_block].get("type")
                    cost = entities[self.placing_block].get("cost")

                block_class = components.get(type_name)
                if block_class is None:
                    folder.log.write(f"Class <{type_name}> not exists", type=applib.ERROR)
                    return

                if not folder.config.get("devmode", False) and self.Base is not None:
                    coef = folder.config.get("craft_coef", 1)

                    if cost is not None:
                        for name, value in cost.items():
                            if not self.Base.storage.reduce(name, int(value*coef)):
                                return
                            
                obj = block_class(self, x, y, self.placing_block, team=self.team)
                if hasattr(obj, "place"):
                    obj.place()
        
        elif event.button() == Qt.MouseButton.RightButton:
            existing = self.get_block_at(x, y)
            if existing:
                existing.remove()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            MusicPlayer.play("click_2")
            if self.menu_active is not None:
                self.menu_active.Back()
            else:
                self.pause_menu.Show()

        self.keys_pressed.add(event.nativeScanCode())
    
    def keyReleaseEvent(self, event):
        self.keys_pressed.discard(event.nativeScanCode())

    @save
    def game_tick(self):
            self.now = time.time()
            dt = self.now - self.last_time 
            self.last_time = self.now
            
            folder.plugins.call("update", self.tick, dt)

            self.update_cam(dt)

            for block in self.blocks.copy():
                            if hasattr(block, "update"):
                                block.update(self.tick, dt)
            
            for entity in self.entities.copy():
                            if hasattr(entity, "update"):
                                entity.update(self.tick, dt)
            
            self.tick += 1

    def update_cam(self, dt):
            if abs(self.target_scale - self.scale) > 0.01:
                old_scale = self.scale
                self.scale = self.scale + (self.target_scale - self.scale) * 6.0 * dt

                factor = self.scale / old_scale
                self.view.scale(factor, factor)

            dx = 0
            dy = 0

            if self.menu_active is None:
                if 17 in self.keys_pressed:
                    dy -= 1
                if 31 in self.keys_pressed:
                    dy += 1
                if 30 in self.keys_pressed:   
                    dx -= 1
                if 32 in self.keys_pressed:   
                    dx += 1

                if dx != 0 and dy != 0:
                    dx *= 0.7071
                    dy *= 0.7071

            target_vx = dx * self.max_speed
            target_vy = dy * self.max_speed
            
            self.vx += (target_vx - self.vx) * self.acceleration * dt
            self.vy += (target_vy - self.vy) * self.acceleration * dt
            
            if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
                current_x = self.view.horizontalScrollBar().value()
                current_y = self.view.verticalScrollBar().value()
                
                self.view.horizontalScrollBar().setValue(current_x + int(self.vx * dt * 60))
                self.view.verticalScrollBar().setValue(current_y + int(self.vy * dt * 60))

    def wheelEvent(self, event):
        if self.menu_active is not None:
            return
        if event.angleDelta().y() > 0:
            self.target_scale *= 1.15
        else:
            self.target_scale /= 1.15
        
        self.target_scale = max(0.4, min(2.0, self.target_scale))
    
    def save(self, filename):
        SectorManager.save(self, filename)

    def load(self, filename):
        SectorManager.load(self, filename)

    def __repr__(self):
        return f"GameWindow(sizeX: {self.sizeX}, sizeY: {self.sizeY})"

    def show(self):
        self.MainWindow.widget.setCurrentIndex(1)
