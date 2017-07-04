import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

""" at the end we should get the mean square displacement of the particle trajectories
if one particle then a single MSD and if multiple particles then the mean of all MSDS
"""
class MSDtraj:

    def __init__(self,dirname,filenum,coords,timestep,timeCMSD=1000):
        self.dirname = dirname
        self.filenum = filenum
        self.timeCMSD = timeCMSD
        self.coords = coords
        self.timestep = timestep

    # importing trajectory
    def importtraj(self,num,delimiter =' '):
            lencoords = len(self.coords)
            d = [] # stores data from the text file
            filename = self.dirname + str(num)+".txt";
            with open(filename,'rb') as source:
                for line in source:
                    if delimiter in line:
                        f = line.split(' ')
                        if lencoords == 4: # for 3D case
                            d.append(map(lambda i: float(f[i]),[0,3,4,5]))
                        elif lencoords == 3: # for 2D case
                            d.append(map(lambda i: float(f[i]),[0,3,4]))
                        else: ## for 1-D
                            d.append(map(lambda i: float(f[i]),[0,3]))

            return pd.DataFrame(d, columns=self.coords)

    # function to compute MSD for one trajectory
    def compute_msd(self,trajectory):

        tau = trajectory['t'].copy()
        tau = tau[0:self.timeCMSD]
        shifts = np.floor(tau / self.timestep).astype(np.int)
        msds = np.zeros(shifts.size)
        msds_std = np.zeros(shifts.size)

        for i, shiftpos in enumerate(shifts):
            diffs = trajectory[self.coords].shift(-shiftpos) - trajectory[self.coords]
            diffs = diffs.dropna(thresh=3)
            sqdist = np.square(diffs).sum(axis=1)
            msds[i] = sqdist.mean()
            msds_std[i] = sqdist.std()

        msds = pd.DataFrame({'msds': msds, 'tau': tau, 'msds_std': msds_std})
        return msds

    ## main import trajectories, calculate composed MSD and STD
    def main(self):
        MSDlist = []
        STDlist = []
        for num in range(1, self.filenum + 1):
            traj = self.importtraj(num)
            msd = self.compute_msd(traj)
            MSDlist.append(msd['msds'])
            STDlist.append(msd['msds_std'])
        msdcomposelist = np.mean(map(list,zip(*MSDlist)),axis=1)
        stdcomposelist = np.mean(map(list,zip(*STDlist)),axis=1)
        return msdcomposelist, stdcomposelist
