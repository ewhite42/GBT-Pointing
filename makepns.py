#! /opt/local/bin/python
#makepns.py

""" This program accepts a list of filepaths to GBT observations and creates a .pns file which contains information about multiple observing sessions rather than just one.

    Ellie White 28 Apr. 2017 -- last modified 19 Sept. 2019

"""
from recType import recType
from shutil import copyfile

def makepns(obslist, trackfile):

    contents = """model = pm
azel  = pm_AzEl.csv
focus = pm_Focus.csv
datapath = /users/ewhite/univPoint

elevspan = 5 87
maxwind = 20
logpath = /home/gbtlogs

trackpath = {0}""".format(trackfile)

    for n in obslist:
        spath = n.split("/")
	obsid = spath[-1]
	fpath = "/".join(spath[:-1])
	rx = recType(n)

        # pns files are separated out by receiver in case you want
        # to store pns files from different receivers in different 
        # directories
	if rx == "KFPA/DCR":
	    beamoff = "-82.16 47.44"
	    fname = "{0}.pns".format(obsid)
	elif rx == "X/DCR":
	    beamoff = "0.0 0.0"
	    fname = "{0}.pns".format(obsid)
	elif rx == "W/DCR":
	    beamoff = "-143.0 0.0"
	    fname = "{0}.pns".format(obsid)
	elif rx == "Argus/DCR":
	    beamoff = "-15.2 -15.2"
	    fname = "{0}.pns".format(obsid)
	#scans =  countScans(obsid)

	contents += """\n\nproject = {0}
projdir = {1}
receiver = {2}
beamoff = {3}
scans = 1:{4} """.format(obsid, fpath, rx, beamoff, 59)

    #name = str(input("What do you want to call the .pns file? "))

    outfile = open(fname, 'w')
    outfile.write(contents)
    print "The .pns file: {0} has been created.".format(fname)
    return obsid, rx


def main():
    trackfname = '/home/groups/ptcs/trackmaps/tmapJul17-2017.track.txt'

    n = input("Enter the filepath of a list of projects you want to make pns files for >>> ")

    infile = open(n, 'r')
    for line in infile:
	fpaths = [line.strip("\n")]
    	name, rec = makepns(fpaths, trackfname)
    	#makeLambdas(name, rec)
    


if __name__ == "__main__":
    main()
