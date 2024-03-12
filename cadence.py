# -*- coding: utf-8 -*-
# CADENCE  supervised calcium events detection

from PySide6.QtGui import (QAction, QIcon)
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QMainWindow, 
    QApplication,
    QWidget,
    QDoubleSpinBox,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QCheckBox,
    QMenu,
    QMenuBar
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from numpy.polynomial.polynomial import polyfit
import sys, os, csv, scipy
from scipy import signal
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.plot_widget = PlotWidget(parent=self)
        self.setCentralWidget(self.plot_widget)
        self.setWindowTitle("CADENCE — supervised calcium events detection")
        #self._createMenuBar()    
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        open_action = QAction('Open dF/F', self)
        save_action = QAction('Save events', self)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        global fil, path, Fluorescence, NormalizedFluorescence, totaldatapoints, events
        fil=''
        path=''
        open_action.triggered.connect(lambda i: self.open_file())
        save_action.triggered.connect(lambda i: self.save_file())
        
    def open_file(self):
        self.file_name = QFileDialog.getOpenFileName(None, "Open", "", "Tab-separated files (*.txt)")
        global fil, path, Fluorescence, NormalizedFluorescence, totaldatapoints, events
        fil=os.path.basename(self.file_name[0])
        path=os.path.dirname(self.file_name[0])
        os.chdir(path)
        
        Fluorescence=pd.DataFrame() #read calcium events to Fluorescence array
        f = open(fil, 'r')
        st=f.read()
        Fluorescence = pd.read_csv(fil,sep='\t',header=None)
        f.close()
        
        NormalizedFluorescence=[]
        NormalizedFluorescence=(Fluorescence-Fluorescence.min())/(Fluorescence.max()-Fluorescence.min())#normalize events
        totaldatapoints=len(NormalizedFluorescence)
        self.plot_widget = PlotWidget(parent=self) #update plot
        self.setCentralWidget(self.plot_widget)
        events=[] #distinguished calcium events

    def save_file(self):    
        global fil, path, events
        file_name, _ = QFileDialog.getSaveFileName(self,"Save File",os.path.join(path,os.path.splitext(os.path.basename(fil))[0]+"_raster.txt"),"All Files(*);;Text Files(*.txt)")
        if file_name:
            df=pd.DataFrame(events)#saving raster events data
            df.to_csv(file_name, index=False, sep=' ') 
        
    
class PlotWidget(QWidget):              
    def __init__(self, parent=None):
        super().__init__(parent)
        #  create widgets
        self.view = FigureCanvas(Figure(figsize=(15, 9)))
        self.axes = self.view.figure.subplots()
        
        self.lowpass = QCheckBox()
        self.lowpass=QCheckBox("LP/HP Filtering", self)
        self.lowpass.setChecked(False)
        
        self.chn_input = QSpinBox()
        self.chn_input.setPrefix("Channel: ")
        self.chn_input.setValue(0)
        self.chn_input.setMaximum(9999)
        
        self.w_input = QSpinBox()
        self.w_input.setPrefix("Window: ")
        self.w_input.setValue(20)
        self.w_input.setSingleStep(5)
        
        self.thr_input = QDoubleSpinBox(decimals=4)
        self.thr_input.setPrefix("Threshold: ")
        self.thr_input.setValue(0.015)
        self.thr_input.setSingleStep(0.005)
        
        self.button = QPushButton("&Accept channel", self)
    
        # Â Create layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.lowpass)
        input_layout.addWidget(self.chn_input)
        input_layout.addWidget(self.w_input)
        input_layout.addWidget(self.thr_input)
        input_layout.addWidget(self.button)
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.view)
        vlayout.addLayout(input_layout)
        self.setLayout(vlayout)

        # connect inputs with on_change method
        self.chn_input.valueChanged.connect(self.on_change)
        self.thr_input.valueChanged.connect(self.on_change)
        self.w_input.valueChanged.connect(self.on_change)
        self.lowpass.toggled.connect(self.on_change)
        
        FilteredFluorescence, EventsAllCh, chn = self.on_change()
        self.button.clicked.connect(lambda i: self.save_chn(FilteredFluorescence, EventsAllCh))
     
    def save_chn(self,FilteredFluorescence, EventsAllCh):
        chn = self.chn_input.value()
        events.insert(len(events),EventsAllCh[chn])#save to events array
        print("channel ",chn, " saved")
        self.chn_input.setValue(chn+1)
        
    def on_change(self):
        #""" Update the plot with the current input values """
        w = self.w_input.value() #window width
        thr = self.thr_input.value() #threshold relative to median
        chn = self.chn_input.value() #current channel number

        filtr=self.lowpass.isChecked()        
        FilteredFluorescence, EventsAllCh = eventsdiscr(w, thr, filtr)
        
        self.axes.clear()
        self.axes.plot(FilteredFluorescence[chn])
        self.axes.scatter(EventsAllCh[chn],FilteredFluorescence[chn][EventsAllCh[chn]],linewidth=0.3, s=50, c='r')
        self.view.draw()
        return FilteredFluorescence, EventsAllCh, chn


#for highpass filter
def highpass(data: np.ndarray, cutoff: float, sample_rate: float, poles: int = 5):
    sos = scipy.signal.butter(poles, cutoff, 'highpass', fs=sample_rate, output='sos')
    filtered_data = scipy.signal.sosfiltfilt(sos, data)
    return filtered_data

#events discrimination
def eventsdiscr (w, thr, filtr): 
    global Fluorescence, NormalizedFluorescence, totaldatapoints
    EventsAllCh=[] #all channels events
    FilteredFluorescence=[] #all channels traces
    for ite in range(len(Fluorescence.columns)):
        if filtr:
            b, a = signal.butter(8, 0.125)
            CurrentChannel = signal.filtfilt(b, a, NormalizedFluorescence[ite], padlen=150) #filtering
            CurrentChannel = highpass(CurrentChannel, 4, totaldatapoints) #removing shift
        else : 
            CurrentChannel = NormalizedFluorescence[ite].values

        EventsCurrentCh=signal.argrelextrema(CurrentChannel, np.greater, order=w) #find spikes
        EventsCurrentChThr=list()#filtered events
        for i in list(EventsCurrentCh[0]): #filtering spikes
            if (i+w)<len(CurrentChannel) and i>w : #window width limits
                if ((CurrentChannel[i]-CurrentChannel[i+w])>thr)&((CurrentChannel[i]-CurrentChannel[i-w])>thr)  : EventsCurrentChThr.append(i)
        EventsAllCh.insert(len(EventsAllCh), EventsCurrentChThr)
        FilteredFluorescence.insert(len(FilteredFluorescence), CurrentChannel)
    return FilteredFluorescence, EventsAllCh
    

Fluorescence=[0,0,0,0,0,0,0,0,0,0,0] #dummy calcium events to Fluorescence array before file is open
Fluorescence=pd.DataFrame(Fluorescence) 
NormalizedFluorescence=[0,0,0,0,0,0,0,0,0,0,0]
NormalizedFluorescence=pd.DataFrame(NormalizedFluorescence) 
totaldatapoints=len(NormalizedFluorescence)
events=[] #distinguished calcium events

if __name__ == '__main__':
  
    app = QApplication(sys.argv)
    # creating main window
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())