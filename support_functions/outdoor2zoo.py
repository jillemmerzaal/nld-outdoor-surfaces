from support_functions.setZoosystem import setZoosystem
from support_functions.add_channel import addchannel_data
from support_functions.zsave import zsave
from support_functions.engine import engine
from tkinter import filedialog
import tkinter as tk
import time
import os
import json

# Some hardcoded values
CHNS = ['Acc_x', 'Acc_y', "Acc_z"]
SAMPLE_RATE = 100


def outdoor2zoo(fld):
    """
    OUTDOOR2ZOO is a custom function to convert data from outdoor data set to zoo format
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
            print(f'no data for condition {c}')
            continue

        subs = r[c].keys()
        for s in subs:
            r[c][s].keys()
            fname = f"{s}_{c}.zoo"
            print(f"creating zoo file for {fname}")
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
                    data[f'{ch}']['event'] = {
                        f'FS1': [evts, 0, 0],
                    }

                # Save all into to file
            zsave(fname, data)

        print(' ')
        print('**********************************')
        print('Finished converting data in: ')
        print(f"{time.time() - start_time:.2f} seconds")
        print('**********************************')
