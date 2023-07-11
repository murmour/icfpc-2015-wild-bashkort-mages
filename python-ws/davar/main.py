'''
Created on Aug 7, 2015

@author: linesprower
'''

from PyQt4 import QtGui, QtCore
import json, sys, copy, os, itertools, io, re
from datetime import datetime


def allF(lst, f):
    """
    return True if all elements of lst satisfy f
    """
    for x in lst:
        if not f(x):
            return False
    return True


kTopAlign = 1
kBottomAlign = 2

def VBox(items, margin = 0, spacing = 5, align = None, stretch = None):
    box = QtGui.QVBoxLayout()
    box.setMargin(margin)
    box.setSpacing(spacing)
    if stretch == None:
        stretch = [0] * len(items)
    else:
        assert(len(stretch) == len(items))
    if align == kBottomAlign:
        box.setAlignment(QtCore.Qt.AlignBottom)
    elif align == kTopAlign:
        box.setAlignment(QtCore.Qt.AlignTop)
    for x, st in zip(items, stretch):
        if isinstance(x, QtGui.QLayout):
            box.addLayout(x, st)
        else:
            box.addWidget(x, st)
    return box


kLeftAlign = 1
kRightAlign = 2

def HBox(items, margin = 0, spacing = 5, align = None, stretch = None):
    box = QtGui.QHBoxLayout()
    box.setMargin(margin)
    box.setSpacing(spacing)
    if stretch == None:
        stretch = [0] * len(items)
    else:
        assert(len(stretch) == len(items))
    if align == kRightAlign:
        box.setAlignment(QtCore.Qt.AlignRight)
    elif align == kLeftAlign:
        box.setAlignment(QtCore.Qt.AlignLeft)
    for x, st in zip(items, stretch):
        if isinstance(x, QtGui.QLayout):
            box.addLayout(x, st)
        elif isinstance(x, QtGui.QSpacerItem):
            box.addSpacerItem(x)
        else:
            box.addWidget(x, st)
    return box


icons_cache = {}

def GetIcon(fname):
    if not fname:
        fname = ''
    if fname not in icons_cache:
        icons_cache[fname] = QtGui.QIcon(fname)
    return icons_cache[fname]


def Action(owner, descr, icon, handler = None, shortcut = None,
           statustip = None, enabled = True, checkable = False,
           checked = None, *, bold = False):
    act = QtGui.QAction(GetIcon(icon), descr, owner)
    act.setIconVisibleInMenu(True)

    if bold:
        f = act.font()
        f.setBold(True)
        act.setFont(f)

    if not (shortcut is None):
        act.setShortcut(shortcut)

    if not (statustip is None):
        act.setStatusTip(statustip)
    if not (handler is None):
        act.triggered.connect(handler)
    act.setEnabled(enabled)
    if checkable:
        act.setCheckable(True)
    if checked != None:
        act.setCheckable(True)
        act.setChecked(checked)
    return act

def Separator(owner):
    res = QtGui.QAction(owner)
    res.setSeparator(True)
    return res

def ToolBtn(action):
    res = QtGui.QToolButton()
    res.setDefaultAction(action)
    res.setAutoRaise(True)
    return res

def ensureLayout(widget):
    if isinstance(widget, QtGui.QWidget):
        return VBox([widget])
    return widget

def ensureWidget(layout):
    if isinstance(layout, QtGui.QWidget):
        return layout
    tmp = QtGui.QWidget()
    tmp.setLayout(layout)
    return tmp

def getOpenFileName(owner, ident, title, filters, save=False):
    ident = 'openfile_' + ident
    s = QtCore.QSettings('PlatBox', 'PlatBox')
    path = s.value(ident, defaultValue='')
    if save:
        opts = QtGui.QFileDialog.DontConfirmOverwrite if save == 1 else 0
        fname = QtGui.QFileDialog.getSaveFileName(None, title, path, filters, opts)
    else:
        fname = QtGui.QFileDialog.getOpenFileName(None, title, path, filters)
    if fname:
        path = os.path.dirname(fname)
        s.setValue(ident, path)
    return fname

def Frame(widget, width = 2):
    """
    Adds a frame around a given widget/layout
    """
    fr = QtGui.QFrame()
    fr.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
    fr.setLineWidth(width)
    fr.setStyleSheet(".QFrame { color:gray }")
    fr.setLayout(ensureLayout(widget))
    widget.cmn_frame = fr
    return fr


fname = '../../data/problems/problem_%d.json'

SIZE = 25
N_PROBLEMS = 25
MAX_PLEN = 60
SKIP_FRAMES = 50

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
        self.pscore = 0
        self.usedp = set()
        self.pvisual = ''
        self.move_num = 0
        self.history = ''
        self.rot = 0
        self.max_rot = 0
        self.last_spawn = 0

    def __str__(self):
        return str((self.cur_unit, self.unit_idx, self.score, self.ls_old))

    def __repr__(self):
        return self.__str__()


class Frame:
    def __init__(self, cells, state):
        self.cells = copy.deepcopy(cells)
        self.state = copy.deepcopy(state)


class InfoPanel(QtGui.QDockWidget):

    def __init__(self, owner):

        QtGui.QDockWidget.__init__(self, ' Solution info')

        self.owner = owner
        self.setObjectName('info_panel') # for state saving

        e = QtGui.QTextEdit()
        e.setFont(QtGui.QFont('Consolas', 10))
        e.setReadOnly(True)
        self.e = e
        self.setWidget(e)

        self.setFeatures(QtGui.QDockWidget.DockWidgetMovable)

    def setData(self, text):
        self.e.setPlainText(text)

class TileWidget(QtGui.QWidget):

    SIZE = 25

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
        self.resetmins()
        self.update()

    def resetmins(self):
        self.setMinimumSize((self.w+1) * self.SIZE, self.h * self.SIZE + 10)

    def paintEvent(self, ev):
        p = QtGui.QPainter(self)
        p.setBrush(QtGui.QColor('white'))
        for i in range(self.h):
            dx = self.SIZE // 2 if i % 2 == 1 else 0
            for j in range(self.w):
                p.drawEllipse(dx + j * self.SIZE, i * self.SIZE * 42 // 50, self.SIZE, self.SIZE)

        p.setBrush(QtGui.QColor('blue'))
        for j, i in self.cells:
            dx = self.SIZE // 2 if i % 2 == 1 else 0
            p.drawEllipse(dx + j * self.SIZE, i * self.SIZE * 42 // 50, self.SIZE, self.SIZE)

        p.setBrush(QtGui.QColor('gray'))
        j, i = self.pivot
        dx = self.SIZE // 2 if i % 2 == 1 else 0
        p.drawEllipse(QtCore.QPoint(dx + j * self.SIZE + self.SIZE // 2, i * self.SIZE * 42 // 50 + self.SIZE // 2), 5, 5)


class TileWidget2(QtGui.QWidget):

    def __init__(self, owner):
        QtGui.QWidget.__init__(self)
        self.owner = owner
        self.h = None
        self.state = None
        self.sel = None
        self.positions = None
        self.sel_rot = 0

        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def setData(self, data, h, w):
        self.h = h
        self.w = w
        self.init_data = data
        self.resetmins()
        self.initPos()

    def calcPositions(self):
        self.positions = {}
        self.seen = {}
        #print('calcpositions: %s' % self.state.cur_unit)
        if not self.state.cur_unit:
            return

        def go(move, prev):
            t = self.xpos()
            self.seen[t] = (move, prev, self.state.cur_unit)
            for m in range(6):
                if self.canMove(m):
                    self.doMove(m)
                    if self.xpos() not in self.seen:
                        go(m, t)
                    self.undoMove(m)
                else:
                    # lock
                    self.positions[self.xpos()] = self.state.cur_unit, m

        go(None, None)
        #for x in self.seen.keys():
        #    print(x)

    def wheelEvent(self, ev):
        ev.accept()
        if ev.delta() > 0:
            self.sel_rot += 1
        else:
            self.sel_rot -= 1
        self.mouseMoveEvent(ev)

    def animating(self):
        return self.owner.act_play.isChecked() or self.owner.act_playb.isChecked()

    def mousePressEvent(self, ev):
        if self.sel == None or not self.sel_valid:
            return

        cur = self.sel_pos
        lets = 'palbdk'
        lock_cmd = self.positions[cur][1]
        cmds = [lets[lock_cmd]]
        while cur != None:
            move, cur, _ = self.seen[cur]
            if move != None:
                cmds.append(lets[move])
        cmds.reverse()
        for c in cmds:
            self.owner.doCommand(c)
        #print(''.join(cmds))


    def mouseMoveEvent(self, ev):

        if self.animating():
            return

        def getCell():
            x, y = ev.x(), ev.y()
            h = SIZE * 42 // 50
            yy = max(0, y - (SIZE - h)) // h
            if yy >= self.h:
                return None
            dx = SIZE // 2 if yy % 2 == 1 else 0
            x -= dx
            if x < 0:
                return None
            xx = x // SIZE
            if xx >= self.w:
                return None
            return xx, yy

        t = getCell()

        if self.positions == None:
            self.calcPositions()
            #print(len(self.positions))
        self.sel = None
        rs = []
        for r in range(6):
            if (t, r) in self.positions or (t, r) in self.seen:
                rs.append(r)

        if rs:
            self.sel_rot = self.sel_rot % len(rs)
            r = rs[self.sel_rot]
            self.sel = t
            if (t, r) in self.positions:
                self.sel_unit = self.positions[(t, r)][0]
                self.sel_valid = True
            else:
                self.sel_unit = self.seen[(t, r)][2]
                self.sel_valid = False
            self.sel_pos = (t, r)
        self.update()



    def xpos(self):
        return self.state.cur_unit.pivot, self.state.rot

    def resetmins(self):
        self.setMinimumSize((self.w+1) * SIZE, self.h * SIZE * 42 // 50 + 10)

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

        return allF(self.state.cur_unit.members, f)

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
        if move == 4:
            self.state.rot += 1
            if self.state.rot >= self.state.max_rot: self.state.rot = 0
        elif move == 5:
            self.state.rot -= 1
            if self.state.rot < 0: self.state.rot = self.state.max_rot - 1

    def undoMove(self, move):
        if move <= 3:
            m2 = move + 3
            if m2 >= 6:
                m2 -= 6
            self.state.cur_unit = Unit( self.move_pnt(self.state.cur_unit.pivot, m2, 1),
                                        [self.move_pnt(x, m2, 1) for x in self.state.cur_unit.members] )
        else:
            self.doMove(5 if move == 4 else 4)


    def calc_max_rot(self):
        t = sorted(self.state.cur_unit.members)
        for i in range(6):
            self.doMove(4)
            self.state.cur_unit.members.sort()
            if self.state.cur_unit.members == t:
                #print('Maxrot = %d' % (i+1))
                return i+1
        assert (False)


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
        self.state.rot = 0
        self.state.max_rot = self.calc_max_rot()
        self.state.rot = 0

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
        self.sel_pos = None
        self.sel = None

    def updatePower(self, letter, pwords):
        #print(history)
        self.state.pvisual = ''
        history = self.state.history + letter
        if len(history) > MAX_PLEN:
            history = history[1:]
        self.state.history = history
        for pw in pwords:
            if history.endswith(pw):
                if not pw in self.state.usedp:
                    self.state.usedp.add(pw)
                    self.state.pscore += 300
                self.state.pscore += 2 * len(pw)
                self.state.pvisual += pw

    def lockUnit(self):
        for x, y in self.state.cur_unit.members:
            self.cells[y][x] = 1

        # collapse here
        new_cells = [row for row in self.cells if not allF(row, lambda x: x == 1)]
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
        if self.animating():
            self.sel = None

        if not self.h:
            return
        p = QtGui.QPainter(self)

        def draw_cell(x, y, col):
            p.setBrush(QtGui.QColor(col))
            dx = SIZE // 2 if y % 2 == 1 else 0
            p.drawEllipse(dx + x * SIZE, y * SIZE * 42 // 50, SIZE, SIZE)

        def draw_pivot(x, y, col = 'gray'):
            p.setBrush(QtGui.QColor(col))
            dx = SIZE // 2 if y % 2 == 1 else 0
            p.drawEllipse(QtCore.QPoint(dx + x * SIZE + SIZE // 2, y * SIZE * 42 // 50 + SIZE // 2), 5, 5)

        def draw_text(x, y, s):
            font = p.font()
            font.setPixelSize(50)
            p.setFont(font)
            #p.setBrush(QtGui.QColor('lightgreen'))
            p.setPen(QtGui.QColor('green'))
            dx = SIZE // 2 if y % 2 == 1 else 0
            p.drawText(QtCore.QPoint(dx + x * SIZE + SIZE // 2, y * SIZE * 42 // 50 + SIZE // 2), s)
            p.setPen(QtGui.QColor('gray'))

        for i in range(self.h):
            for j in range(self.w):
                draw_cell(j, i, 'blue' if self.cells[i][j] else 'white')

        if self.state.cur_unit:
            for x, y in self.state.cur_unit.members:
                draw_cell(x, y, 'red')
            draw_pivot(self.state.cur_unit.pivot[0], self.state.cur_unit.pivot[1])

        if self.state.pvisual and self.state.cur_unit:
            draw_text(self.state.cur_unit.pivot[0], self.state.cur_unit.pivot[1], self.state.pvisual)

        if self.sel:
            for x, y in self.sel_unit.members:
                draw_cell(x, y, 'green' if self.sel_valid else 'yellow')
            draw_pivot(self.sel[0], self.sel[1], 'purple')


class UnitsPanel(QtGui.QDockWidget):

    def __init__(self, owner):

        QtGui.QDockWidget.__init__(self, ' Units')

        self.owner = owner
        self.setObjectName('object_creator') # for state saving

        self.setWidget(QtGui.QWidget())
        self.setFeatures(QtGui.QDockWidget.DockWidgetMovable)

    def setData(self, units):
        self.units = units
        def make(x):
            t = TileWidget(self)
            t.setData(x)
            return t

        layout = VBox([make(x) for x in units])
        wrap = QtGui.QScrollArea()
        wrap.setWidget(ensureWidget(layout))
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
        self.loadpowers()

        #self.img = QtGui.QImage(self.w * 50, self.h * 50,
        #                        QtGui.QImage.Format_ARGB32)
        #self.setCentralWidget(self.img)
        self.frames = []
        self.cur_frame = -1000
        self.resize(800, 600)

        self.units_list = UnitsPanel(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.units_list)
        self.info_box = InfoPanel(self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.info_box)


        s = QtCore.QSettings('PlatBox', 'Davar')
        t = s.value("mainwnd/geometry")
        if t:
            self.restoreGeometry(t)
        t = s.value("mainwnd/dockstate")
        if t:
            self.restoreState(t, 0)

        self.cbx = QtGui.QComboBox()
        self.sizesl = QtGui.QSlider()
        self.sizesl.setOrientation(QtCore.Qt.Horizontal)
        self.sizesl.setMaximumWidth(100)
        self.sizesl.setMinimum(10)
        self.sizesl.setMaximum(50)
        self.sizesl.setValue(25)
        self.sizesl.valueChanged.connect(self.changeSz)
        self.wi = TileWidget2(self)

        self.frame_lbl = QtGui.QLabel('None')
        self.act_next0 = Action(self, 'Last frame (F12)', 'icons/first.png', self.nextFrame0, 'F12')
        self.act_prev0 = Action(self, 'First frame (F11)', 'icons/last.png', self.prevFrame0, 'F11')
        self.act_next = Action(self, 'Next frame (F3)', 'icons/next.png', self.nextFrame, 'F3', enabled=False)
        self.act_prev = Action(self, 'Prev frame (F2)', 'icons/prev.png', self.prevFrame, 'F2', enabled=False)
        self.act_playb = Action(self, 'Play back (F4)', 'icons/control-180.png', self.startPlayback, 'F4', checkable=True)
        self.act_play = Action(self, 'Play (F5)', 'icons/play.png', self.startPlay, 'F5', checkable=True)
        self.act_gotomove = Action(self, 'Go to move... (F1)', 'icons/hand-point.png', self.gotoMove, 'F1')
        self.act_togglefast = Action(self, 'Toggle fast', '', self.toggleFast, 'F8')

        self.act_lastm = Action(self, 'Back to last spawn (Delete)', 'icons/undo.png', self.prevMove, 'Delete')
        self.addAction(self.act_togglefast)

        self.fastcb = QtGui.QCheckBox('Fast(F8)')
        self.fastcb.toggled.connect(self.onToggleFast)

        layout = HBox([self.cbx, self.sizesl, self.frame_lbl,
                       ToolBtn(self.act_lastm),
                       ToolBtn(self.act_gotomove),
                       ToolBtn(self.act_prev0),
                       ToolBtn(self.act_next0),
                       ToolBtn(self.act_prev),
                       ToolBtn(self.act_next),
                       ToolBtn(self.act_playb),
                       ToolBtn(self.act_play),
                       self.fastcb])

        #wrap = QtGui.QScrollArea()
        #wrap.setWidget(self.wi)
        wrap = self.wi

        layout = VBox([layout, wrap])
        self.setCentralWidget(ensureWidget(layout))

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Menu')
        self.act_showsol = Action(self, 'Show solution', '', self.showSol, 'F9')
        self.act_savesol = Action(self, 'Save solution', '', self.doSave, 'Ctrl+S')
        self.act_opensol = Action(self, 'Open solution file...', '', self.doOpen, 'Ctrl+O')
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
        self.cbx.addItems([str(i) for i in range(N_PROBLEMS)])

        if self.solname:
            self.show()
            if self.solname != '$$$':
                self.showSol()

    def changeSz(self, sz):
        global SIZE
        SIZE = sz
        self.wi.resetmins()
        self.wi.update()

    def loadpowers(self):
        with io.open('../../data/power-words.txt') as f:
            x = f.read().split('\n')
            self.powerwords = list(set([s for s in x if not s.startswith('#') and s.strip()]))
        for s in self.powerwords:
            assert(len(s) <= MAX_PLEN)
        #print(self.powerwords)

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
                    #history = self.cmds[max(0, i-MAX_PLEN) : i]
                    if not self.doCommandInternal(c, True):
                        print('Cannot spawn after %d' % i)
                        break
                except:
                    print('Move = %d' % i)
                    raise

            #print(len(self.frames))
            #self.setFrame(0)
            res.append((self.wi.state.score, self.wi.state.pscore))
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
        os.makedirs('saves', exist_ok=True)
        fname = getOpenFileName(self, 'sol_save', 'Save solution', 'JSON Files (*.json)', True)
        if not fname:
            fname = 'saves/task_%d_%s.json' % (self.data['id'], datetime.now().isoformat())
        else:
            if not fname.endswith('.json'):
                fname += '.json'
        with io.open(fname, 'w') as f:
            f.write(json.dumps(sol))
        print('Saved to %s' % fname)

    def doOpen(self):
        fname = getOpenFileName(self, 'sol', 'Open solution', 'JSON Files (*.json)')
        if fname:
            self.solname = fname
        self.showSol()

    def gotoMove(self):
        val, ok = QtGui.QInputDialog.getInt(self, 'Go to move', 'Go to move', self.cur_frame+1)
        if ok:
            self.setFrame(val-1)

    def toggleFast(self):
        self.fastcb.toggle()

    def onToggleFast(self):
        inter = 10 if self.fastcb.isChecked() else 50
        self.backup_timer.start(inter)
        self.backup_timer2.start(inter)

    def startGameInternal(self, seed):
        self.seed = seed
        self.cmds = ''
        self.seq = [x % len(self.units) for x in gen_rand(seed, self.data['sourceLength'])]

        self.wi.initPos()
        self.wi.placeUnit(self.seq, self.units)

        self.frames = []
        self.frames.append(Frame(self.wi.cells, self.wi.state))
        self.cur_frame = 0

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

        #history = self.cmds
        #if len(history) > MAX_PLEN:
        #    history = history[-MAX_PLEN:]
        self.doCommandInternal(letter)
        #print(self.cmds)
        self.cmds = self.cmds + letter
        self.cur_frame += 1
        self.updateStuff()

    def doCommandInternal(self, letter, no_frame=False):
        c = cmd_lets[letter]

        res = True
        if self.wi.canMove(c):
            self.wi.doMove(c)
        else:
            self.wi.lockUnit()
            if self.wi.state.unit_idx < len(self.seq):
                if not self.wi.placeUnit(self.seq, self.units):
                    res = False
                else:
                    self.wi.state.last_spawn = self.wi.state.move_num + 1
        self.wi.updatePower(letter, self.powerwords)
        self.wi.state.move_num += 1

        #print('???')
        if not no_frame:
            if self.wi.state.move_num % SKIP_FRAMES == 0:
                self.frames.append(Frame(self.wi.cells, self.wi.state))
            else:
                self.frames.append(42)
        return res

    def showSol(self):
        with io.open(self.solname, 'r') as f:
            sol = json.loads(f.read())

        if len(sol) > 1:
            val, ok = QtGui.QInputDialog.getInt(self, 'Seed index', 'seed (0-%d)' % (len(sol)-1), 0)
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
            #history = self.cmds[max(0, i-MAX_PLEN) : i]
            if not self.doCommandInternal(c):
                print('Cannot spawn after %d' % i)
                break

        #info = ''
        #score = self.frames[-1].state.score
        #pscore = self.frames[-1].state.pscore
        score = self.wi.state.score
        pscore = self.wi.state.pscore
        info = 'score = %d (%d + %d)' % (score + pscore, score, pscore)

        pscore2 = 0

        pwords = []
        for s in self.powerwords:
            pos = 0
            cnt = 0
            while True:
                pos = self.cmds.find(s, pos)
                if pos == -1:
                    break
                cnt += 1
                pos = pos + 1
            if cnt:
                pwords.append('%s (%d)' % (s, cnt))
                pscore2 += 300 + 2 * len(s) * cnt
        info += '\npowerwords: %s' % ', '.join(pwords)
        #used = self.frames[-1].state.unit_idx
        used = self.wi.state.unit_idx
        stock = self.data['sourceLength']
        info += '\nused %d of %d' % (used, stock)
        if used < stock:
            info += ' CONGESTION!!!'

        self.info_box.setData(info)
        assert(pscore == pscore2)
        self.setFrame(0)

    def nextFrame0(self):
        self.setFrame(len(self.frames)-1)

    def prevFrame0(self):
        self.setFrame(0)

    def nextFrame(self):
        self.setFrame(self.cur_frame + 1)

    def prevFrame(self):
        self.setFrame(self.cur_frame - 1)

    def prevMove(self):
        self.prevFrame()
        self.setFrame(self.wi.state.last_spawn)

    def setFrame(self, idx):
        n_frames = len(self.frames)
        if n_frames == 0:
            self.frame_lbl.setText('None')
            self.act_next.setEnabled(False)
            self.act_prev.setEnabled(False)
            self.wi.update()
            return
        if idx < 0:
            idx = 0
        if idx >= n_frames:
            idx = n_frames - 1

        if idx == self.cur_frame and idx > 0:
            return
        if idx == self.cur_frame + 1 and idx > 0:
            #print(self.wi.state.move_num)
            self.doCommandInternal(self.cmds[self.wi.state.move_num], True)
        else:
            t = idx
            while self.frames[t] == 42:
                t -= 1
            self.wi.state = copy.deepcopy(self.frames[t].state)
            self.wi.cells = copy.deepcopy(self.frames[t].cells)
            while t < idx:
                self.doCommandInternal(self.cmds[self.wi.state.move_num], True)
                t += 1

        self.cur_frame = idx
        self.wi.positions = None
        self.wi.seen = None
        self.wi.sel = None
        self.updateStuff()

    def updateStuff(self):
        n_frames = len(self.frames)
        idx = self.cur_frame
        unit_idx = self.wi.state.unit_idx
        unit_ty = -1 if unit_idx >= len(self.seq) else self.seq[unit_idx] % len(self.units)
        score = self.wi.state.score
        pscore = self.wi.state.pscore
        totscore = score + pscore
        self.frame_lbl.setText('%d/%d - %d(%d) | %d(%d+%d)' % (idx+1, n_frames, unit_idx, unit_ty, totscore, score, pscore))
        self.act_next.setEnabled(idx + 1 < n_frames)
        self.act_prev.setEnabled(idx > 0)
        self.wi.positions = None
        self.wi.update()


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
        #self.startGame()
        self.wi.positions = None
        self.wi.update()

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
    #print(getScore('../../data/solutions/solution_1_rip_2.json'))
    #print(getScore('../../data/solutions/solution_2_rip_2.json'))
    #return

    #return
    app = QtGui.QApplication(sys.argv)
    #fname = '$$$'
    fname = '../../data/solutions/solution_23_rip_2.json'
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    _ = TileEditor(fname)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
