'''
Created on Aug 7, 2015

@author: linesprower
'''

from PyQt4 import QtGui, QtCore
import json, sys, copy, os
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
    
    def __repr__(self):
        return self.__str__()

class State:
    def __init__(self, cur_unit, unit_idx, score, ls_old):
        self.cur_unit = cur_unit
        self.unit_idx = unit_idx # index of the next unit to put
        self.score = score
        self.ls_old = ls_old
        
    def __str__(self):
        return str((self.cur_unit, self.unit_idx, self.score, self.ls_old))
    
    def __repr__(self):
        return self.__str__()
    

class Frame:
    def __init__(self, cells, state):
        self.cells = copy.deepcopy(cells)
        self.state = copy.deepcopy(state)        
    

class TileWidget(QtGui.QWidget):
    
    def __init__(self, owner):
        self.pivot = (0, 0)
        self.cells = []
        self.w = 0
        self.h = 0        
        QtGui.QWidget.__init__(self)        
        
    def setData(self, data):
        self.pivot = data.pivot
        self.cells = data.members
        self.w = max([t[0] for t in self.cells] + [self.pivot[0]]) + 1 
        self.h = max([t[1] for t in self.cells] + [self.pivot[1]]) + 1
        #print(self.w)
        #print(self.h)
        self.setMinimumSize((self.w+1) * SIZE, self.h * SIZE + 10)
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
        


    
class TileWidget2(QtGui.QWidget):
    
    def __init__(self, owner):
        QtGui.QWidget.__init__(self)
        self.owner = owner
        self.h = None        
        self.state = None        
        
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
    
    def setData(self, data, h, w):
        self.h = h
        self.w = w 
        self.init_data = data
        self.initPos()        
                
    def keyPressEvent(self, ev):
        if ev.key() in qt_keys:
            self.owner.doCommand(qt_keys[ev.key()])
            
    def canMove(self, move):
        pivot = self.state.cur_unit.pivot
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
        
        return cmn.allF(self.state.cur_unit.members, f)
    
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
        pivot = self.state.cur_unit.pivot
        def f(p):
            if move <= 3:
                return self.move_pnt(p, move, 1)
            else:
                p_end = pivot
                p1 = self.move_pnt(pivot, 5, pivot[1] - p[1])
                p_end = self.move_pnt(p_end, 4 if move == 4 else 0, pivot[1] - p[1])
                p_end = self.move_pnt(p_end, 5 if move == 4 else 1, p1[0] - p[0])
                return p_end
        self.state.cur_unit = Unit(f(pivot), [f(x) for x in self.state.cur_unit.members])        
    
    def placeUnit(self, seq, units):
        assert(self.state.unit_idx < len(seq))
        unit = units[seq[self.state.unit_idx]]        
        mi = min([ t[1] for t in unit.members ])
        unit = Unit( self.move_pnt(unit.pivot, 5, mi), [ self.move_pnt(p, 5, mi) for p in unit.members ] )
        mi = min( t[0] for t in unit.members )
        ma = max( t[0] for t in unit.members )
        d = (self.w - (ma - mi + 1)) // 2 - mi
        unit = Unit( self.move_pnt(unit.pivot, 3, d), [ self.move_pnt(p, 3, d) for p in unit.members ] )
        
        for x, y in unit.members:
            if self.cells[y][x]:
            #assert(not self.cells[y][x])
                return False
        
        self.state.cur_unit = unit
        self.state.unit_idx += 1
        return True
        #print(d)
        #print(unit)
        #return unit
    
    def initPos(self):
        if not self.h:
            return
        self.cells = [[0] * self.w for _ in range(self.h)]
        for ce in self.init_data:
            self.cells[ ce['y'] ][ ce['x'] ] = 1
        self.state = State(None, 0, 0, 0)        
    
    def lockUnit(self):
        for x, y in self.state.cur_unit.members:
            self.cells[y][x] = 1
            
        # collapse here
        new_cells = [row for row in self.cells if not cmn.allF(row, lambda x: x == 1)]
        size = len(self.state.cur_unit.members)
        ls = self.h - len(new_cells)
        if ls > 0:
            new_cells = [[0] * self.w for _ in range(ls)] + new_cells
            self.cells = new_cells
        ls_old = self.state.ls_old
        
        '''
        move_score = points + line_bonus
          where
          points = size + 100 * (1 + ls) * ls / 2
          line_bonus  = if ls_old > 1
                        then floor ((ls_old - 1) * points / 10)
                        else 0
        '''
        points = size + 100 * (1 + ls) * ls // 2
        if ls_old > 1:
            points += (ls_old - 1) * points // 10
        self.state.cur_unit = None
        self.state.ls_old = ls
        self.state.score += points
    
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
                
        if self.state.cur_unit:
            for x, y in self.state.cur_unit.members:
                draw_cell(x, y, 'red')
            draw_pivot(self.state.cur_unit.pivot[0], self.state.cur_unit.pivot[1])                


class UnitsPanel(QtGui.QDockWidget):
    
    def __init__(self, owner):
        
        QtGui.QDockWidget.__init__(self, ' Units')
        
        self.owner = owner
        self.setObjectName('object_creator') # for state saving
        
        #self.cbx = QtGui.QComboBox()        
        #self.wi = TileWidget(self)
        
        #self.cbx.currentIndexChanged.connect(self.onChanged)        
        
        #layout = cmn.VBox([self.cbx, self.wi])          
        #self.setWidget(cmn.ensureWidget(layout))
        
        self.setWidget(QtGui.QWidget())
        self.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
    
    def setData(self, units):
        self.units = units
        def make(x):
            t = TileWidget(self)
            t.setData(x)
            return t
            
        layout = cmn.VBox([make(x) for x in units])
        wrap = QtGui.QScrollArea()
        wrap.setWidget(cmn.ensureWidget(layout))        
        self.setWidget(wrap)
        
        #self.cbx.clear()
        #self.cbx.addItems([str(i) for i in range(len(units))])
        
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

qt_keys = {
          QtCore.Qt.Key_A : 'a',
          QtCore.Qt.Key_B : 'b',
          QtCore.Qt.Key_C : 'c',
          QtCore.Qt.Key_D : 'd',
          QtCore.Qt.Key_E : 'e',
          QtCore.Qt.Key_F : 'f',
          QtCore.Qt.Key_G : 'g',
          QtCore.Qt.Key_H : 'h',
          QtCore.Qt.Key_I : 'i',
          QtCore.Qt.Key_J : 'j',
          QtCore.Qt.Key_K : 'k',
          QtCore.Qt.Key_L : 'l',
          QtCore.Qt.Key_M : 'm',
          QtCore.Qt.Key_N : 'n',
          QtCore.Qt.Key_O : 'o',
          QtCore.Qt.Key_P : 'p',
          QtCore.Qt.Key_Q : 'q',
          QtCore.Qt.Key_R : 'r',
          QtCore.Qt.Key_S : 's',
          QtCore.Qt.Key_T : 't',
          QtCore.Qt.Key_U : 'u',
          QtCore.Qt.Key_V : 'v',
          QtCore.Qt.Key_W : 'w',
          QtCore.Qt.Key_X : 'x',
          QtCore.Qt.Key_Y : 'y',
          QtCore.Qt.Key_Z : 'z',
          QtCore.Qt.Key_0 : '0',
          QtCore.Qt.Key_1 : '1',
          QtCore.Qt.Key_2 : '2',
          QtCore.Qt.Key_3 : '3',
          QtCore.Qt.Key_4 : '4',
          QtCore.Qt.Key_Apostrophe : "'",
          QtCore.Qt.Key_Space : ' ',
          QtCore.Qt.Key_Period : '.',
          QtCore.Qt.Key_Exclam : '!',
          QtCore.Qt.Key_Up : 'd',
          QtCore.Qt.Key_Down : 'k',
          QtCore.Qt.Key_Left : 'p',
          QtCore.Qt.Key_Right : 'b'
          }

def decode_cmd(s):
    return ' '.join([cmd_names[cmd_lets[c]] for c in s])

class TileEditor(QtGui.QMainWindow):
    
    def __init__(self, solname):
        QtGui.QMainWindow.__init__(self)
        
        self.solname = solname        
        
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
        self.act_next = cmn.Action(self, 'Next frame (F3)', 'next.png', self.nextFrame, 'F3', enabled=False)
        self.act_prev = cmn.Action(self, 'Prev frame (F2)', 'prev.png', self.prevFrame, 'F2', enabled=False)
        self.act_playb = cmn.Action(self, 'Play back (F4)', 'control-180.png', self.startPlayback, 'F4', checkable=True)
        self.act_play = cmn.Action(self, 'Play (F5)', 'play.png', self.startPlay, 'F5', checkable=True)
        self.act_gotomove = cmn.Action(self, 'Go to move... (F1)', 'hand-point.png', self.gotoMove, 'F1')
        
        layout = cmn.HBox([self.cbx, self.frame_lbl, cmn.ToolBtn(self.act_gotomove), cmn.ToolBtn(self.act_prev), 
                           cmn.ToolBtn(self.act_next), cmn.ToolBtn(self.act_playb), cmn.ToolBtn(self.act_play)])
        layout = cmn.VBox([layout, self.wi])
        self.setCentralWidget(cmn.ensureWidget(layout))
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Menu')
        self.act_showsol = cmn.Action(self, 'Show solution', '', self.showSol, 'F9')
        self.act_savesol = cmn.Action(self, 'Save solution', '', self.doSave, 'Ctrl+S')
        self.act_opensol = cmn.Action(self, 'Open solution file...', '', self.doOpen, 'Ctrl+O')
        fileMenu.addAction(self.act_opensol)
        fileMenu.addAction(self.act_showsol)
        fileMenu.addAction(self.act_savesol)
        
        self.backup_timer = QtCore.QTimer()
        self.backup_timer.timeout.connect(self.doPlay)
        self.backup_timer.start(50)
        self.backup_timer2 = QtCore.QTimer()
        self.backup_timer2.timeout.connect(self.doPlayb)
        self.backup_timer2.start(50)
        
        self.cbx.currentIndexChanged.connect(self.onChanged)
        self.cbx.addItems([str(i) for i in range(24)])
        
        if self.solname:                
            self.show() 
            self.showSol()
    
    def calcScore(self, fname):
        with io.open(fname, 'r') as f:
            sols = json.loads(f.read())
        res = []
        print(fname)
        print(len(sols))
        for sol in sols:
            id = sol["problemId"]
            if self.data['id'] != id:
                self.cbx.setCurrentIndex(id)        
            seed = sol["seed"]
            self.seed = seed
            tag = sol["tag"]                  
                #return
            print('Tag = %s, seed = %d' % (tag, seed))
            
            self.startGameInternal(seed)
            self.cmds = sol['solution']
            #print(decode_cmd(self.cmds))
            print('%d commands' % len(self.cmds))
            for i, c in enumerate(self.cmds):
                #print(c)
                try:
                    if not self.doCommandInternal(c, True):
                        print('Cannot spawn after %d' % i)
                        break
                except:
                    print('Move = %d' % i)
                    raise
            
            #print(len(self.frames))
            #self.setFrame(0)
            res.append(self.wi.state.score)
        return res
    
    def startPlay(self):
        self.act_playb.setChecked(False)
        
    def startPlayback(self):
        self.act_play.setChecked(False)
    
    def doSave(self):
        if not self.frames:
            return
        sol = {}
        sol["problemId"] = self.data['id']
        sol["seed"] = self.seed
        sol["tag"] = 'davar_visualizer'
        sol['solution'] = self.cmds
        sol = [sol]        
        fname = 'saves/task_%d_%s.json' % (self.data['id'], cmn.isoNow())
        os.makedirs('saves', exist_ok=True)
        with io.open(fname, 'w') as f:
            f.write(json.dumps(sol))
        print('Saved')
    
    def doOpen(self):
        fname = cmn.getOpenFileName(self, 'sol', 'Open solution', 'JSON Files (*.json)')
        if fname:
            self.solname = fname
        self.showSol()
    
    def gotoMove(self):
        val, ok = QtGui.QInputDialog.getInt(self, 'Go to move', 'Go to move', self.cur_frame+1)
        if ok:
            self.setFrame(val-1)
    
    def startGameInternal(self, seed):
        self.seed = seed
        self.cmds = ''
        self.seq = [x % len(self.units) for x in gen_rand(seed, self.data['sourceLength'])]
        
        self.wi.initPos()
        self.wi.placeUnit(self.seq, self.units)
        
        self.frames = []
        self.frames.append(Frame(self.wi.cells, self.wi.state))
    
    def startGame(self):        
        seed = self.data['sourceSeeds'][0]
        self.startGameInternal(seed)        
        self.setFrame(0)
    
    def printFrames(self):
        return
        print('!!')
        for x in self.frames:
            print(x.state)
    
    def doCommand(self, letter):
        if not self.frames:
            self.startGame()        
        
        if self.wi.state.cur_unit == None:
            print('No more units!')
            return
        
        self.frames = self.frames[0 : self.cur_frame+1]
        self.printFrames()
        
        self.cmds = self.cmds[0 : self.cur_frame]
        
        self.doCommandInternal(letter) 
        #print(self.cmds)
        self.cmds = self.cmds + letter
        self.printFrames()
        self.setFrame(self.cur_frame+1)
    
    def doCommandInternal(self, letter, no_frame=False):
        c = cmd_lets[letter]        
        
        self.printFrames()
        
        res = True
        if self.wi.canMove(c):
            self.wi.doMove(c)
        else:
            self.wi.lockUnit()
            if self.wi.state.unit_idx < len(self.seq):
                if not self.wi.placeUnit(self.seq, self.units):
                    res = False
        
        #print('???')
        if not no_frame:
            self.frames.append(Frame(self.wi.cells, self.wi.state))
        return res        
    
    def showSol(self):
        with io.open(self.solname, 'r') as f:
            sol = json.loads(f.read())
            
        if len(sol) > 0:
            val, ok = QtGui.QInputDialog.getInt(self, 'Seed', 'seed', 0)
            if not ok:
                return
            if val < 0 or val >= len(sol):
                return
            sol = sol[val]
        else:
            sol = sol[0]        
        
        
        id = sol["problemId"]
        seed = sol["seed"]
        self.seed = seed
        tag = sol["tag"]        
        if self.data['id'] != id:
            print('wrong id, reloading')
            self.cbx.setCurrentIndex(id)
            #return
        print('Tag = %s, seed = %d' % (tag, seed))
        
        self.startGameInternal(seed)
        self.cmds = sol['solution']
        #print(decode_cmd(self.cmds))
        print('%d commands' % len(self.cmds))
        for i, c in enumerate(self.cmds):
            #print(c)
            if not self.doCommandInternal(c):
                print('Cannot spawn after %d' % i)
                break
                
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
            idx = 0
        if idx >= n_frames:
            idx = n_frames - 1
        self.cur_frame = idx
        self.wi.state = copy.deepcopy(self.frames[idx].state)
        self.wi.cells = copy.deepcopy(self.frames[idx].cells)        
        unit_idx = self.frames[idx].state.unit_idx
        unit_ty = -1 if unit_idx >= len(self.seq) else self.seq[unit_idx] % len(self.units)
        score = self.frames[idx].state.score
        self.frame_lbl.setText('%d/%d - %d(%d) | %d' % (idx+1, n_frames, unit_idx, unit_ty, score))
        self.act_next.setEnabled(idx + 1 < n_frames)
        self.act_prev.setEnabled(idx > 0)
        self.printFrames()
        self.update()
    
    def doPlay(self):
        if self.act_play.isChecked():
            if self.cur_frame == len(self.frames) - 1:
                self.act_play.setChecked(False)
            self.nextFrame()    
            
    def doPlayb(self):
        if self.act_playb.isChecked():
            if self.cur_frame == 0:
                self.act_playb.setChecked(False)
            self.prevFrame()
        
    
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
        
app = None

def getScore(filename):
    global app
    if app == None:
        app = QtGui.QApplication(sys.argv)
    x = TileEditor('')
    return x.calcScore(filename)
            
        
def main():
    #print(gen_rand(17, 10))
    #print(decode_cmd('ctulhu'))
    #print(getScore('../../solutions/solution_1_rip_2.json'))
    #print(getScore('../../solutions/solution_2_rip_2.json'))
    #return
    
    #return
    app = QtGui.QApplication(sys.argv)
    fname = 'test.json'
    if len(sys.argv) > 1:
        fname = sys.argv[1]    
    _ = TileEditor(fname)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()