# cadence
CADENCE — neuroinformatic tool for supervised calcium events detection.
CADENCE is an open-source Python3-written neuroinformatic tool with Qt6 GUI for supervised calcium events detection. In calcium imaging experiments, the  instruments' (Celena X, Miniscope) output is a movie with flashing cells. There are few pipelines to convert video to relative fluorescence dF/F, from simplest ImageJ/Fiji plugins to sophisticated tools like MiniAn. dF/F may be per se desired result, but usually researcher interested in more detailed analysis of calcium events. Here is the niche for our tool, as one need to distinguish calcium events from dF/F curve and rasterize it for later use in analysis software, like Elephant.

![cadence_gui](https://github.com/asenicos/cadence/assets/31521207/b5b56525-f0ad-478f-8ed1-852bdd931a1e)

Installation

To run the tool, you need Python 3 installed in your system (we wrote and tested tool in Python 3.8). If you do not have Python on your PC, we recommend downloading and installing the Miniconda package:

 install miniconda

Additional installation of PySide6/Qt package is needed for GUI, type in prompt shell:

 pip3 install pyside6
 
CADENCE have dependencies on the SciPy, Pandas, and Matplotlib libraries for correct functioning, so you will need to install them:

 conda install matplotlib
 
 conda install scipy
 
 conda install pandas

To run examples for later analysis you will need Elephant and viziphant packages installation, see instructions by the link:

 pip3 install elephant
 
 pip3 install viziphant

Usage

Work with CADENCE is straightforward: first you need to open tab-separated file with dF/F data (File/Open dF/F). We provide example dF/F file from Celena X calcium imaging experiment and example data from Miniscope. Tab-separated data file can be prepared in spreadsheet like Excel, decimal separator is dot. When file is opened, the relative fluorescence for the first channel with distinguished events is appeared in main window. We recommend to use low pass and high pass filtering of data from Celena X (LP/HP Filtering checkbox). Relative fluorescence data from Miniscope were processed by MiniAn and don't need to be filtered after CNMF-e algorithm. The speed of processing such data in CADENCE may be as high, as 20 channels per minute. Threshold and window of peaks detection can be tuned by respective spin boxes. When you are satisfied with detected calcium events for the channel, you can save the results by pressing button "Accept channel". The next channel will be displayed automatically. If you decide to skip a channel because of bad quality of dF/F data and detection, just increase channel number in Channel spin box. Channels where "Accept channel" button were not pressed will not appeared in final output data. When you process all of channels use File/Save events to save output to text file. This output file contains all events for all accepted channels and can be loaded to Python for later analysis.
![example_traces](https://github.com/asenicos/cadence/assets/31521207/81a5c642-e70a-4587-bbb0-fdf79866121f)
![example_raster](https://github.com/asenicos/cadence/assets/31521207/b53971b7-c643-41ce-a322-d16a3a01057d)

Analysis

We provide a code for loading output data to Elephant for later analysis in a separate file. After loading data the code shows raster plot of calcium events, calculate mean firing rate, Spike-contrast synchrony, CuBIC xi, and plot results of SPADE analysis for synchronous events.
![example_spade](https://github.com/asenicos/cadence/assets/31521207/edabbf28-d5f8-4279-ba20-c9922ef78fca)

Comparison

We made a comparison with sophisticated ML tool for automated calcium events detection, Cascade. Without "ground truth" data (eg. patch clamp recording simultaneous to imaging), out of the box, Cascade shows worse detection of calcium events small in magnitude. Nevertheless, Cascade analyze magnitude of events and trying to inferring spike bursts from high-magnitude events.
![example_cascade](https://github.com/asenicos/cadence/assets/31521207/05143196-e57c-47d6-9aa2-5a1bb56de2c1)
_Upper trace is dF/F, middle trace is the result of CADENCE detection, lower one is for Cascade detection with optimal parameters._
