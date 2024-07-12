import pandas as pd
from support_functions.engine import engine
from support_functions.grab import grab
from support_functions.fileparts import fileparts


def zoo2excel(fld, fld_stats):
    """
    zoo2excel is a specified function to extract the calculated non-linear dynamics from the individual dictionaries
    and write them to a csv file.

    :param fld: full path to data folder
    :param fld_stats: full path to stats folder
    :return: Nothing
    """
    fl = engine(path=fld, extension=".zoo")
    fl.sort()

    # pre-allocate empty lists
    surface = []
    subject_id = []
    last_step = []
    samp_ent = []
    ldlj = []
    step_sym = []
    stride_sym = []
    lye_s = []
    lye_l = []

    for f in fl:
        # extract data
        data = grab(f)
        file_path, file_name, ext = fileparts(f)
        print(f'extracting nld on {file_name}{ext} and writing to ')

        # extract subject/condition from file name
        indx = [i for i, char in enumerate(file_name) if char == '_']
        subject_id.append(file_name[:indx[0]])
        surface.append(file_name[indx[0] + 1:])
        last_step.append(data["Acc_x"]["event"]["FS1"][0])

        # extract non-linear dynamics
        samp_ent.append(data["Acc_euclidean"]["event"]["sampen"][0])
        ldlj.append(data["Acc_euclidean"]["event"]["ldlj"][0])
        step_sym.append(data["Autocorrelation"]["event"]["ad1"][0])
        stride_sym.append(data["Autocorrelation"]["event"]["ad2"][0])
        lye_s.append(data["Divergence"]["event"]["LyEs"][0])
        lye_l.append(data["Divergence"]["event"]["LyEl"][0])

    # create dictionalry from the appended listst
    data_dict = {
        "Subject_ID": subject_id,
        "Surface": surface,
        "LeastStepIndex": last_step,
        "SampleEntropy": samp_ent,
        "LDLJ": ldlj,
        "StepSymmetry": step_sym,
        "StrideSymmetry": stride_sym,
        "LyE_s": lye_s,
        "LyE_l": lye_l}

    # write to csv
    df = pd.DataFrame.from_dict(data_dict)
    csv_name = fld_stats + "/results.csv"
    df.to_csv(csv_name)
