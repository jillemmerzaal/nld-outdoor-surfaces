<h1> Non-linear dynamics of outdoor walking </h1>
Code to calculate the non-linear dynamics analysis of walking on various surfaces from a single IMU placed on the lower back

<h2> Pre-requisites </h2>
cd to the root folder containing the main.py in the terminal or command window, and run the following commands:

```
conda create -n nld_surfaces 
```

```
conda activate nld_surfaces
```

```
pip install -r requirements.txt
```

<h2>Run the provided python script </h2>
The run the python script, use the command ```python main.py``` where ```main.py```is the specific python file. 

```main.py``` will extract the data from the .zip file, create the file and folder structure required for the non-linear dynamics analysis. 
It will write the final output into a .csv file.




