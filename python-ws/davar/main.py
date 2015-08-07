'''
Created on Aug 7, 2015

@author: linesprower
'''

from PyQt4 import QtGui, QtCore
import json, sys
import io
import common as cmn

fname = '../../qualifier-problems/problem_%d.json'

SIZE = 30

def unp_cell(cell):
    return cell['x'], cell['y']

class TileWidget(QtGui.QDockWidget):
    
    def __init__(self, owner):
        self.pivot = (0, 0)
        self.cells = []
        self.w = 0
        self.h = 0
        QtGui.QDockWidget.__init__(self, owner)
        
    def setData(self, data):
        self.pivot = unp_cell(data['pivot'])
        self.cells = [unp_cell(x) for x in data['members']]
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
    
    def setData(self, data, h, w):
        self.h = h
        self.w = w 
        self.cells = [[0] * self.w for _ in range(self.h)]
        for ce in data:
            self.cells[ ce['y'] ][ ce['x'] ] = 1        
    
    def paintEvent(self, ev):
        if not self.h:
            return        
        p = QtGui.QPainter(self)        
        for i in range(self.h):
            dx = SIZE // 2 if i % 2 == 1 else 0
            for j in range(self.w):
                if self.cells[i][j]:
                    p.setBrush(QtGui.QColor('blue'))
                else:
                    p.setBrush(QtGui.QColor('white'))
                p.drawEllipse(dx + j * SIZE, i * SIZE * 42 // 50, SIZE, SIZE)


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
        

class TileEditor(QtGui.QMainWindow):
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        
        #self.img = QtGui.QImage(self.w * 50, self.h * 50,
        #                        QtGui.QImage.Format_ARGB32)
        #self.setCentralWidget(self.img)        
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
        
        self.cbx.currentIndexChanged.connect(self.onChanged)
        self.cbx.addItems([str(i) for i in range(24)])
        
        layout = cmn.VBox([self.cbx, self.wi])
        self.setCentralWidget(cmn.ensureWidget(layout))
        self.show()
        #img = 
        
    def onChanged(self, idx):
        with io.open(fname % idx, 'r') as f:
            data = json.loads(f.read())
            self.h = data['height']
            self.w = data['width']
            
        self.units_list.setData(data['units'])
        descr = 'id = %s, count = %s, games = %s' % (data['id'], data['sourceLength'], len(data['sourceSeeds']))                                                     
        self.statusBar().showMessage(descr)
        self.wi.setData(data['filled'], self.h, self.w)
        self.update()
    
    def closeEvent(self, event):
        s = QtCore.QSettings('PlatBox', 'Davar')
        s.setValue("mainwnd/geometry", self.saveGeometry())
        s.setValue('mainwnd/dockstate', self.saveState(0))        
    
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    _ = TileEditor()
    sys.exit(app.exec_())