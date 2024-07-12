import tkinter as tk
import time
import os
import json
from tkinter import filedialog
from support_functions.setZoosystem import setZoosystem
from support_functions.add_channel import addchannel_data
from support_functions.zsave import zsave
from support_functions.engine import engine

# Some hardcoded values
CHNS = ['Acc_x', 'Acc_y', "Acc_z"]
SAMPLE_RATE = 100


def outdoor2zoo(fld):
    """
    OUTDOOR2ZOO is a custom function to convert data from outdoor data set to zoo format. The zoo format in Python is
    modeled after the biomechZoo toolbox, which is an open-source toolbox for the processing, analysis,
    and visualization of biomechanical movement data implemented in Matlab.
    Each data file has n-number of channels containing the time-series data [m x 1] or [m x 3] and
    any corresponding events [1 x 3]. The file also contains a zoosystem that contains all system information
    e.g. sample frequency, number of channels, number of events.

    For detailed information about the biomechZoo toolbox, please see:
    Dixon, P. C., Loh, J. J., Michaud-Paquette, Y., & Pearsall, D. J. (2017). biomechZoo: An open-source toolbox for the
    processing, analysis, and visualization of biomechanical movement data.
    Computer Methods and Programs in Biomedicine, 140, 1-10.

    :param fld: str. Full path to data folder
    :return: None
    """


    if fld is None:
        root = tk.Tk()
        root.withdraw()
        fld = filedialog.askdirectory()

    start_time = time.time()
    os.chdir(fld)

    fl = engine(path=fld, extension='.json')
    with open(fl[0], 'r') as f:
        r = json.load(f)

    cons = r.keys()

    for c in cons:
        if not r[c]:
            print('no data for condition {0}'.format(c))
            continue

        subs = r[c].keys()
        for s in subs:
            r[c][s].keys()
            fname = "{0}_{1}.zoo".format(s, c)
            print("creating zoo file for {0}".format(fname))
            evts = r[c][s]['last_step_index']
            print(evts)
            data = {}
            data['zoosystem'] = setZoosystem(fname)
            data['zoosystem']['Units'] = {}
            data['zoosystem']['Video']["Freq"] = SAMPLE_RATE
            data['zoosystem']['AVR'] = 0

            for ch in CHNS:
                ndata = r[c][s][ch]
                if isinstance(ndata, int):
                    ndata = [ndata]
                data = addchannel_data(data, f'{ch}', ndata, 'video')
                if ch == 'Acc_x':
                    data['{0}'.format(ch)]['event'] = {
                        f'FS1': [evts, 0, 0],
                    }

                # Save all into to file
            zsave(fname, data)

        time_to_finish = time.time() - start_time
        print(' ')
        print('**********************************')
        print('Finished converting data in: {:.2f} seconds'.format(time_to_finish))
        # print(f"{time.time() - start_time:.2f} seconds")
        print('**********************************')
