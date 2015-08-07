'''
Created on Aug 7, 2015

@author: linesprower
'''

from PyQt4 import QtGui, QtCore
import json, sys, copy
import io#, time
import common as cmn

fname = '../../qualifier-problems/problem_%d.json'

SIZE = 25

def unp_cell(cell):
    return cell['x'], cell['y']

class Unit:
    
    def __init__(self, pivot = (0, 0), members = []):
        self.pivot = pivot
        self.members = members
     
    @staticmethod   
    def load(data):
        res = Unit()
        res.pivot = unp_cell(data['pivot'])
        res.members = [unp_cell(x) for x in data['members']]
        return res
    
    def __str__(self):
        return '%s | %s' % (str(self.pivot), str(self.members))

class TileWidget(QtGui.QDockWidget):
    
    def __init__(self, owner):
        self.pivot = (0, 0)
        self.cells = []
        self.w = 0
        self.h = 0
        QtGui.QDockWidget.__init__(self, owner)
        
    def setData(self, data):
        self.pivot = data.pivot
        self.cells = data.members
        self.w = max([t[0] for t in self.cells] + [self.pivot[0]]) + 1 
        self.h = max([t[1] for t in self.cells] + [self.pivot[1]]) + 1
        #print(self.w)
        #print(self.h)
        self.update()
        
    def paintEvent(self, ev):        
        p = QtGui.QPainter(self)
        p.setBrush(QtGui.QColor('white'))
        for i in range(self.h):
            dx = SIZE // 2 if i % 2 == 1 else 0
            for j in range(self.w):                
                p.drawEllipse(dx + j * SIZE, i * SIZE * 42 // 50, SIZE, SIZE)
                
        p.setBrush(QtGui.QColor('blue'))
        for j, i in self.cells:
            dx = SIZE // 2 if i % 2 == 1 else 0
            p.drawEllipse(dx + j * SIZE, i * SIZE * 42 // 50, SIZE, SIZE)
            
        p.setBrush(QtGui.QColor('gray'))
        j, i = self.pivot
        dx = SIZE // 2 if i % 2 == 1 else 0
        p.drawEllipse(QtCore.QPoint(dx + j * SIZE + SIZE // 2, i * SIZE * 42 // 50 + SIZE // 2), 5, 5)
        
    
class TileWidget2(QtGui.QDockWidget):
    
    def __init__(self, owner):
        QtGui.QDockWidget.__init__(self, owner)
        self.h = None
        self.cur_unit = None
    
    def setData(self, data, h, w):
        self.h = h
        self.w = w 
        self.init_data = data
        self.initPos()
        self.cur_unit = None
                
    
    def canMove(self, move):
        pivot = self.cur_unit.pivot
        def f(p):            
            if move <= 3:
                res = self.move_pnt(p, move, 1)
            else:
                p_end = pivot
                p1 = self.move_pnt(pivot, 5, pivot[1] - p[1])
                p_end = self.move_pnt(p_end, 4 if move == 4 else 0, pivot[1] - p[1])
                p_end = self.move_pnt(p_end, 5 if move == 4 else 1, p1[0] - p[0])
                res = p_end
            x, y = res
            if not (0 <= x < self.w) or not (0 <= y < self.h):
                return False
            if self.cells[y][x]:
                return False
            return True
        
        return cmn.allF(self.cur_unit.members, f)        
    
    def move_pnt(self, p, dir, d):
        if d < 0:
            d *= -1
            dir += 3
            if dir >= 6: dir -= 6
        x, y = p
        if (y & 1) == 0:
            if dir == 0: 
                x -= d
            elif dir == 1:
                x -= (d + 1) // 2
                y += d
            elif dir == 2:
                x += d // 2
                y += d
            elif dir == 3:
                x += d
            elif dir == 4:
                x += d // 2
                y -= d
            elif dir == 5:
                x -= (d + 1) // 2
                y -= d
        else:
            if dir == 0: 
                x -= d
            elif dir == 1:
                x -= d // 2
                y += d
            elif dir == 2:
                x += (d + 1) // 2
                y += d
            elif dir == 3:
                x += d
            elif dir == 4:
                x += (d + 1) // 2
                y -= d
            elif dir == 5:
                x -= d // 2
                y -= d
        return x, y    
    
    def doMove(self, move):        
        pivot = self.cur_unit.pivot
        def f(p):
            if move <= 3:
                return self.move_pnt(p, move, 1)
            else:
                p_end = pivot
                p1 = self.move_pnt(pivot, 5, pivot[1] - p[1])
                p_end = self.move_pnt(p_end, 4 if move == 4 else 0, pivot[1] - p[1])
                p_end = self.move_pnt(p_end, 5 if move == 4 else 1, p1[0] - p[0])
                return p_end
        self.cur_unit = Unit(f(pivot), [f(x) for x in self.cur_unit.members])        
    
    def placeUnit(self, unit):        
        mi = min([ t[1] - unit.pivot[1] for t in unit.members ])
        unit = Unit( self.move_pnt(unit.pivot, 5, mi), [ self.move_pnt(p, 5, mi) for p in unit.members ] )
        mi = min( t[0] for t in unit.members )
        ma = max( t[0] for t in unit.members )
        d = (self.w - (ma - mi + 1)) // 2 - mi
        unit = Unit( self.move_pnt(unit.pivot, 3, d), [ self.move_pnt(p, 3, d) for p in unit.members ] )
        
        for x, y in unit.members:
            assert(not self.cells[y][x])
        
        self.cur_unit = unit
        print(d)
        print(unit)
        #return unit
    
    def initPos(self):
        self.cells = [[0] * self.w for _ in range(self.h)]
        for ce in self.init_data:
            self.cells[ ce['y'] ][ ce['x'] ] = 1        
    
    def lockUnit(self):
        for x, y in self.cur_unit.members:
            self.cells[y][x] = 1
    
    def paintEvent(self, ev):
        if not self.h:
            return        
        p = QtGui.QPainter(self)
        
        def draw_cell(x, y, col):
            p.setBrush(QtGui.QColor(col))
            dx = SIZE // 2 if y % 2 == 1 else 0
            p.drawEllipse(dx + x * SIZE, y * SIZE * 42 // 50, SIZE, SIZE)
            
        def draw_pivot(x, y):
            p.setBrush(QtGui.QColor('gray'))
            dx = SIZE // 2 if y % 2 == 1 else 0
            p.drawEllipse(QtCore.QPoint(dx + x * SIZE + SIZE // 2, y * SIZE * 42 // 50 + SIZE // 2), 5, 5)
            
        for i in range(self.h):            
            for j in range(self.w):
                draw_cell(j, i, 'blue' if self.cells[i][j] else 'white')
                
        if self.cur_unit:
            for x, y in self.cur_unit.members:
                draw_cell(x, y, 'red')
            draw_pivot(self.cur_unit.pivot[0], self.cur_unit.pivot[1])                


class UnitsPanel(QtGui.QDockWidget):
    
    def __init__(self, owner):
        
        QtGui.QDockWidget.__init__(self, ' Units')
        
        self.owner = owner
        self.setObjectName('object_creator') # for state saving
        
        self.cbx = QtGui.QComboBox()        
        self.wi = TileWidget(self)
        
        self.cbx.currentIndexChanged.connect(self.onChanged)        
        
        layout = cmn.VBox([self.cbx, self.wi])          
        self.setWidget(cmn.ensureWidget(layout))
        self.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
    
    def setData(self, units):
        self.units = units
        self.cbx.clear()
        self.cbx.addItems([str(i) for i in range(len(units))])
        
    def onChanged(self, idx):
        if idx < 0:
            return
        self.wi.setData(self.units[idx])
        
def gen_rand(seed, cnt):    
    cur = seed
    res = []
    mod = 2 ** 32
    for _ in range(cnt):
        res.append((cur >> 16) & 0x7fff)
        cur = (1103515245 * cur + 12345) % mod
    return res        

CMDW = 0
CMDE = 3
CMDSW = 1
CMDSE = 2
CMDCW = 4
CMDCCW = 5

cmd_names = ['L', 'LD', 'RD', 'R', 'CW', 'CCW']

cmd_lets = {}
for c in ['p', "'", '!', '0', '3', '.']: cmd_lets[c] = CMDW
for c in ['b', "c", 'e', 'f', 'y', '2']: cmd_lets[c] = CMDE
for c in ['a', "g", 'h', 'i', 'j', '4']: cmd_lets[c] = CMDSW
for c in ['l', "m", 'n', 'o', ' ', '5']: cmd_lets[c] = CMDSE
for c in ['d', "q", 'r', 'v', 'z', '1']: cmd_lets[c] = CMDCW
for c in ['k', "s", 't', 'u', 'w', 'x']: cmd_lets[c] = CMDCCW

def decode_cmd(s):
    return ' '.join([cmd_names[cmd_lets[c]] for c in s])

class TileEditor(QtGui.QMainWindow):
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        
        #self.img = QtGui.QImage(self.w * 50, self.h * 50,
        #                        QtGui.QImage.Format_ARGB32)
        #self.setCentralWidget(self.img)
        self.frames = []        
        self.resize(800, 600)
        
        self.units_list = UnitsPanel(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.units_list)        
        
        
        s = QtCore.QSettings('PlatBox', 'Davar')
        t = s.value("mainwnd/geometry")
        if t:
            self.restoreGeometry(t)
        t = s.value("mainwnd/dockstate")
        if t:
            self.restoreState(t, 0)
                
        self.cbx = QtGui.QComboBox()                    
        self.wi = TileWidget2(self)        
        
        self.frame_lbl = QtGui.QLabel('None')
        self.act_next = cmn.Action(self, 'Next frame', 'next.png', self.nextFrame, 'F3', enabled=False)
        self.act_prev = cmn.Action(self, 'Prev frame', 'prev.png', self.prevFrame, 'F2', enabled=False)
        self.act_play = cmn.Action(self, 'Play', 'play.png', None, 'F5', checkable=True)
        
        layout = cmn.HBox([self.cbx, self.frame_lbl, cmn.ToolBtn(self.act_prev), cmn.ToolBtn(self.act_next), cmn.ToolBtn(self.act_play)])
        layout = cmn.VBox([layout, self.wi])
        self.setCentralWidget(cmn.ensureWidget(layout))
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Menu')
        self.act_showsol = cmn.Action(self, 'Show solution', '', self.showSol, 'F9')
        fileMenu.addAction(self.act_showsol)
        
        self.backup_timer = QtCore.QTimer()
        self.backup_timer.timeout.connect(self.doPlay)
        self.backup_timer.start(200)
        
        self.cbx.currentIndexChanged.connect(self.onChanged)
        self.cbx.addItems([str(i) for i in range(24)])
                
        self.show() 
    
    
    def showSol(self):
        with io.open('test.json', 'r') as f:
            sol = json.loads(f.read())
        sol = sol[0]
        id = sol["problemId"]
        seed = sol["seed"]
        tag = sol["tag"]
        self.cmds = sol['solution']
        print(decode_cmd(self.cmds))
        if self.data['id'] != id:
            print('wrong id!')
            #return
        print('Tag = %s, seed = %d' % (tag, seed))
        self.seq = gen_rand(seed, self.data['sourceLength'])
        
        
        next_unit = True
        unit_idx = 0
        #cur_pos = None
        #cur_unit = None
        
        frames = []
        
        def check():
            #self.wi.cur_unit = cur_unit
            frames.append((copy.deepcopy(self.wi.cells), self.wi.cur_unit, unit_idx))
            #self.wi.repaint()
            #time.sleep(0.1)        
        
        self.wi.initPos()
        for c in self.cmds:
            if c in ['\n', 't', 'r']:
                continue
            c = cmd_lets[c]
            if next_unit:
                # determine position
                cur_unit = self.units[self.seq[unit_idx] % len(self.units)]
                unit_idx += 1
                next_unit = False
                self.wi.placeUnit(cur_unit)
                check()
                
            if self.wi.canMove(c):
                self.wi.doMove(c)
                check()
            else: 
                self.wi.lockUnit()
                next_unit = True              
            
        self.frames = frames
        self.setFrame(0) 
                
    def nextFrame(self):
        self.setFrame(self.cur_frame + 1)
        
    def prevFrame(self):
        self.setFrame(self.cur_frame - 1)
        
    def setFrame(self, idx):
        n_frames = len(self.frames)
        if n_frames == 0:
            self.frame_lbl.setText('None')
            self.act_next.setEnabled(False)
            self.act_prev.setEnabled(False)
            self.update()
            return
        if idx < 0:
            return
        if idx >= n_frames:
            return
        self.cur_frame = idx
        self.wi.cells = self.frames[idx][0]
        self.wi.cur_unit = self.frames[idx][1]
        unit_idx = self.frames[idx][2]
        unit_ty = self.seq[unit_idx] % len(self.units)
        self.frame_lbl.setText('%d/%d - %d(%d)' % (idx+1, n_frames, unit_idx, unit_ty))
        self.act_next.setEnabled(idx + 1 < n_frames)
        self.act_prev.setEnabled(idx > 0)
        self.update()
    
    def doPlay(self):
        if self.act_play.isChecked():
            self.nextFrame()    
    
    def onChanged(self, idx):
        with io.open(fname % idx, 'r') as f:            
            data = json.loads(f.read())
            
        self.data = data
        self.h = data['height']
        self.w = data['width']        
        self.units = [ Unit.load(x) for x in data['units'] ]
            
        self.units_list.setData(self.units)
        descr = 'id = %s, count = %s, games = %s' % (data['id'], data['sourceLength'], len(data['sourceSeeds']))                                                     
        self.statusBar().showMessage(descr)
        self.wi.setData(data['filled'], self.h, self.w)
        self.frames = []
        self.setFrame(0)
        self.update()
    
    def closeEvent(self, event):
        s = QtCore.QSettings('PlatBox', 'Davar')
        s.setValue("mainwnd/geometry", self.saveGeometry())
        s.setValue('mainwnd/dockstate', self.saveState(0))        
        
        
def main():
    #print(gen_rand(17, 10))
    #print(decode_cmd('ctulhu'))
    #return
    app = QtGui.QApplication(sys.argv)
    _ = TileEditor()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()