import os
import shutil
import zipfile
from support_functions.outdoor2zoo import outdoor2zoo
from support_functions.fileparts import fileparts
from support_functions.engine import engine
from support_functions.grab import grab
from support_functions.add_channel import addchannel_data
from support_functions.zoo2excel import zoo2excel

# support functions for the non-linear analysis
from support_functions.sample_entropy import sample_entropy
from support_functions.symmetry import symmetry
from support_functions.ldlj import log_dimensionless_jerk_imu
from support_functions.LyE import LyE_R
from support_functions.zsave import zsave

# %% Step 1 prepare data
# Ensure the current working directory is the root of the repository
fld_root = os.getcwd()
data_file = os.path.join(fld_root, 'data.json.zip')
fld = os.path.join(fld_root, 'data')  # Setting path for processed data
fld_stats = os.path.join(fld_root, 'Results')

# Remove old processed data folder if it exists
if os.path.exists(fld):
    print('Removing old processed data folder...')
    shutil.rmtree(fld)

os.makedirs(fld)
print(f'Unzipping data file {data_file}')
with zipfile.ZipFile(data_file, 'r') as zip_ref:
    zip_ref.extractall(fld_root)
# move data file to data folder
shutil.move("data.json", "data/data.json")

# Remove old stats folder if it exists
if os.path.exists(fld_stats):
    print('Removing old stats folder...')
    shutil.rmtree(fld_stats)

print('Creating folder for Excel sheet output...')
os.makedirs(fld_stats)

# restructure the data from the json dictionary into seperate files.
outdoor2zoo(fld)

# %% Step 2: re-organize data in folders
fl = engine(path=fld, extension=".zoo")
for f in fl:
    file_path, file_name, ext = fileparts(f)

    # extract subject/condition from file name
    indx = [i for i, char in enumerate(file_name) if char == '_']
    subject = file_name[:indx[0]]
    condition = file_name[indx[0] + 1:]
    nfld = os.path.join(fld, subject, condition)

    if not os.path.exists(nfld):
        os.makedirs(nfld)

    # move file to new directory
    new_file_path = os.path.join(nfld, file_name + ext)
    print(f'moving {file_name}{ext} to {nfld}')
    shutil.move(f"{file_name}{ext}", nfld)
# %% Step 3: Non-linear dynamics analysis

# prepare files
fl = engine(path=fld, extension=".zoo")
fl.sort()

for f in fl:
    file_path, file_name, ext = fileparts(f)
    print(f'running analysis on {file_name}{ext}')

    # extract subject/condition from file name
    indx = [i for i, char in enumerate(file_name) if char == '_']
    subject = file_name[:indx[0]]
    condition = file_name[indx[0] + 1:]

    # extract the data from file
    data = grab(f)
    channels = ["Acc_x", "Acc_y", "Acc_z"]
    last_step_index = data["Acc_x"]["event"]["FS1"][0]

    # perform non-linear dynamics analysis on all gait trails
    sampen, norm = sample_entropy(data, channels, event=last_step_index)
    d_1, ad_1, d_2, ad_2, autocorr = symmetry(data, channels, event=last_step_index)
    ldlj = log_dimensionless_jerk_imu(data, channels, event=last_step_index)
    lds, AveLnDiv = LyE_R(data, channels, event=last_step_index)

    # add channels
    addchannel_data(data, "Acc_euclidean", norm, "video")
    addchannel_data(data, "Autocorrelation", autocorr, "Video")
    addchannel_data(data, "Divergence", AveLnDiv, "Video")

    # add the event to the respective channels
    data["Acc_euclidean"]['event'] = {
        'sampen': [sampen, 0, 0],
        "ldlj": [ldlj, 0, 0]
    }

    data["Autocorrelation"]["event"] = {
        "d1": [int(d_1), 0, 0],
        "d2": [int(d_2), 0, 0],
        "ad1": [float(ad_1), 0, 0],
        "ad2": [float(ad_2), 0, 0]
    }

    data["Divergence"]["event"] = {
        "LyEs": [float(lds[0]), 0, 0],
        "LyEl": [float(lds[1]), 0, 0]
    }

    zsave(f, data)

# %% Extract events to spreadsheet
zoo2excel(fld, fld_stats)
# %%
