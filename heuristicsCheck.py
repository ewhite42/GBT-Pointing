#heuristicsCheck.py

# Last modified 25 Nov. 2017

""" This program accepts a prepoint file as input, writes the heuristics from the
    prepoint file into a new file, then reads that file to determine which scans to
    reject based on heuristic parameters.

    Ellie White 15 May 2017

"""

import os

class HeuristicsCheck:
    def __init__(self, projectid, fwidth=0.5, foffset=3.0, bothpass=False, rheight=0.5, rwidth=0.5, roffset=0.5):
	self.projid = projectid
	self.fwidth = fwidth
	self.foffset = foffset
	self.bothpass = bothpass
	self.rheight = rheight
	self.rwidth = rwidth
	self.roffset = roffset

    def setHeuristics(self, fitwid, fitoff, bothpass, relht, relwid, reloff):
	"""Use this method to change the heuristic cutoff values."""
	self.fwidth = fitwid
	self.foffset = fitoff
	self.bothpass = bothpass
	self.rheight = relht
	self.rwidth = relwid
	self.roffset = reloff

    def runPrepoint(self):
	#run prepoint
	cd = os.getcwd()
	contents = os.listdir(cd)
	if "{0}.out".format(self.projid) not in contents:
	    print "Need to run prepoint..."
	    dir1 = '/home/gbtdata'
	    if self.projid not in dir1:
		a = '/home/archive/test-data'
		subdirs = os.listdir(a)
		for d in subdirs:
		    d = "{0}/{1}".format(a, d)
		    #print d
		    subdirs2 = os.listdir(d)
		    
		    if self.projid in subdirs2:
			self.filename = '{0}/'.format(d)
			print self.filename
			os.system('prepoint {0} -h {1}'.format(self.projid, self.filename))
			print "Ran prepoint"
			return
		    else: continue
	    else:
	        os.system('prepoint {0}'.format(self.projid))
	        print "Ran prepoint"
		return
	else: print "Did not run prepoint"

    def readPrepoint(self):
	#read prepoint file
	pfile = '{0}.out'.format(self.projid)
	infile = open(pfile, 'r')
	lines = infile.readlines()[1:]
	scansdata = []
	scansinfo = []
	for line in lines:
	    fields = [x.strip() for x in line.split(',')]
	    stype = fields[1]
	    scan = fields[3]
	    height = fields[14]
	    width = fields[16]
	    offset = fields[18]
	    obsfreq = fields[9]
	    polarization = fields[2]
	    scandata = [stype, scan, height, width, offset, obsfreq, polarization]
	    scansdata.append(scandata)	

	self.scansdata = scansdata
	return self.scansdata 

    def matchScans(self):
	pairs = []
	for scan in self.scansdata:
	    if scan[0] == 'AzF':
		#find scan with same polarization and scan number, of type AzB
		for i in self.scansdata:
		    #print i[-1], scan[-1], i[1], scan[1], i[0], scan[0]
		    stype1 = float(scan[1])
		    stype2 = float(i[1])
		    if i[-1] == scan[-1] and (stype2 == stype1-1 or stype2 == stype1+1) and i[0] == 'AzB':
			#create scan pair as list
			#print i[-1], scan[-1], i[1], scan[1], i[0], scan[0]
			pair = [scan, i]
			pairs.append(pair)
		    #else:
			#break

	    elif scan[0] == 'AzB':
		#find scan with same polarization and scan number, of type AzF
		for i in self.scansdata:
		    #print i[0], scan[0]
		    stype1 = float(scan[1])
		    stype2 = float(i[1])
		    if i[-1] == scan[-1] and (stype2 == stype1-1 or stype2 == stype1+1) and i[0] == 'AzF':
			#create scan pair as list
			#print i[-1], scan[-1], i[1], scan[1], i[0], scan[0]
			pair = [scan, i]
			pairs.append(pair)
		    #else:
			#break

	    elif scan [0] == 'ElF':
		#find scan with same polarization and scan number, of type ElB
		for i in self.scansdata:
		    #print i[0], scan[0]
		    stype1 = float(scan[1])
		    stype2 = float(i[1])
		    if i[-1] == scan[-1] and (stype2 == stype1-1 or stype2 == stype1+1) and i[0] == 'ElB':
			#create scan pair as list
			#print i[-1], scan[-1], i[1], scan[1], i[0], scan[0]
			pair = [scan, i]
			pairs.append(pair)
		    #else:
			#break


	    elif scan[0] == 'ElB':
		#find scan with same polarization and scan number, of type ElF
		for i in self.scansdata:
		    #print i[0], scan[0]
		    stype1 = float(scan[1])
		    stype2 = float(i[1])
		    if i[-1] == scan[-1] and (stype2 == stype1-1 or stype2 == stype1+1) and i[0] == 'ElF':
			#create scan pair as list
			#print i[-1], scan[-1], i[1], scan[1], i[0], scan[0]
			pair = [scan, i]
			pairs.append(pair)
		    #else:
			#break
	    else:
		continue

	for pair in pairs:
	    #remove duplicates
	    newpair = [pair[1], pair[0]]
	    if newpair in pairs:
		pairs.remove(newpair)

	return pairs

    def writeHeuristics(self):
	outfile = "{0}.hc".format(self.projid)
	ofile = open(outfile, 'w')
	ofile.write("{0}\n\nScan | ScanType | Pol | Individual width | Fitted offset | Relative width | Relative height | Relative offset\n".format(self.projid))

	pairs = self.matchScans()
	#print pairs

	for pair in pairs:
	    pair1 = pair[0]
	    pair2 = pair[1]
	    #find relative width (convert to arcminutes)
	    relwidth = (float(pair1[3])/60)/(float(pair2[3])/60)
	    #find relative height	   
	    relheight = float(pair1[2])/float(pair2[2])
	    #find relative offset (convert to arcminutes)
	    reloffset = ((float(pair1[4])/60)-(float(pair2[4])/60))/(0.5*(float(pair1[3])+float(pair2[3])))
	    
	    for item in pair:
		#find individual width (convert to arcmin)
		exwidth = (740/float(item[5]))/60
	        widthcheck = (float(item[3])/60)/exwidth
		#convert offset to arcmin
	        fitoffset = float(item[4])/60
		ofile.write("{0} | {1} | {2} | {3} | {4} | {5} | {6} | {7}\n".format(item[1], item[0], item[-1], widthcheck, fitoffset, relwidth, relheight, reloffset))
	    
	#print "Heuristics written to {0}\n".format(self.outfile)
	    
    def checkScans(self, azf, azb, elf, elb):
	"""check through self.outfile to see if any of the scans' heuristics exceed the values defined in __init__"""

	ok = True

	#read self.outfile
	hfile = open("{0}.hc".format(self.projid), "r")
	#save each line in self.outfile as a list, within a list called scans
	scans = []
	lines = hfile.readlines()[3:]
	for line in lines:
	    scan = [x.strip() for x in line.split('|')]
	    scans.append(scan)

	if azf[5] == azb[5] == elf[5] == elb[5]:
	    for scan in scans:
	        if int(scan[0]) == int(azf[0]):
		    AzF = scan
	        elif int(scan[0]) == int(azb[0]):
		    AzB = scan
	        elif int(scan[0]) == int(elf[0]):
		    ElF = scan
	        elif int(scan[0]) == int(elb[0]):
		    ElB = scan

	        else:
		    continue

	else:
	    print "Scans were of mixed polarization"
	    # return False
	    for scan in scans:
	        if int(scan[0]) == int(azf[0]) and azf[5] == scan[2]:
		    AzF = scan
	        elif int(scan[0]) == int(azb[0]) and azb[5] == scan[2]:
		    AzB = scan
	        elif int(scan[0]) == int(elf[0]) and elf[5] == scan[2]:
		    ElF = scan
	        elif int(scan[0]) == int(elb[0]) and elb[5] == scan[2]:
		    ElB = scan

	        else:
		    continue
	    
	jack = [AzF, AzB, ElF, ElB]
	#print AzF[0], AzF[1], AzF[2], AzB[0], AzB[1], AzB[2]

	#check each field in scan against heuristics value
	#individual scans:
	for s in jack:
	    #individual fitted width check
	    if abs(float(s[3]))>self.fwidth+1 or abs(float(s[3]))<1-self.fwidth:
		ok = False
		print "Ind. Width failed"
		return ok
	    #individual fitted offset check
	    elif abs(float(s[4]))>self.foffset:
		ok = False
		print "Ind. offset failed"
		return ok

        #if other scan in pair doesn't pass and self.bothpass:
	#badscans.append(scan)

	#relative height check
	"""if abs(float(AzF[6]))>self.rheight+1 or abs(float(AzF[6]))<1-self.rheight:
	    ok = False
	    print "Rel. height (az) failed"
	    return ok
	elif abs(float(ElF[6]))>self.rheight+1 or abs(float(ElF[6]))<1-self.rheight:
	    ok = False
	    print "Rel. height (el) failed"
	    return ok"""

	#relative width check
	if abs(float(AzF[5]))>self.rwidth+1 or abs(float(AzF[5]))<1-self.rwidth:
	    ok = False
	    print "Rel. width (az) failed"
	    return ok
	elif abs(float(ElF[5]))>self.rwidth+1 or abs(float(ElF[5]))<1-self.rwidth:
	    ok = False
	    print "Rel. width (el) failed"
	    return ok

	#relative offset check
	elif abs(float(AzF[7]))>self.roffset+1 or abs(float(AzF[7]))>1-self.roffset:
	    ok = False
	    print "Rel. offset (az) failed"
	    return ok
	elif abs(float(ElF[7]))>self.roffset+1 or abs(float(ElF[7]))>1-self.roffset:
	    ok = False
	    print "Rel. offset (el) failed"
	    return ok

	print ok
        return ok


    def printInfo(self):
	for i in self.badscans:
	    print """Scan {0} was rejected.
Fitted Width:{1}
Fitted Offset:{2}
Both pass? {3}
Relative Height: {4}
Relative Width: {5}
Relative Offset: {6}\n""".format(i[0], i[3], i[4], self.bothpass, i[6], i[5], i[7])
	    continue

    def run(self):
	self.runPrepoint()
        self.readPrepoint()
        self.writeHeuristics()
        #self.checkScans()

def main():
    prepointfile = str(input("Enter the filepath to the prepoint file you want to check>> "))
    hcheck = HeuristicsCheck(prepointfile)
    hcheck.run()

if __name__ == "__main__":
    main()



    """def checkScans(self, azf, azb, elf, elb):
	#check through self.outfile to see if any of the scans' heuristics exceed the values defined in __init__
	#read self.outfile
	hfile = open(self.outfile, "r")
	#save each line in self.outfile as a list, within a list called scans
	scans = []
	lines = hfile.readlines()[3:]
	for line in lines:
	    scan = [x.strip() for x in line.split('|')]
	    scans.append(scan)
	
	badscans = []
	for scan in scans:
	    if 'nan' in scan:
		badscans.append(scan)
		continue
	    
	    #check each field in scan against heuristics value
	    #individual fitted width check
	    if abs(float(scan[3]))>self.fwidth+1 or abs(float(scan[3]))<1-self.fwidth:
		badscans.append(scan)
		print "appended {0}".format(scan)
		continue

	    #individual fitted offset check
	    if abs(float(scan[4]))>self.foffset:
		badscans.append(scan)
		print "appended {0}".format(scan)
		continue

	    #if other scan in pair doesn't pass and self.bothpass:
		#badscans.append(scan)

	    #relative height check
	    if abs(float(scan[6]))>self.rheight+1 or abs(float(scan[6]))<1-self.rheight:
		badscans.append(scan)
		print "appended {0}".format(scan)
		continue

	    #relative width check
	    if abs(float(scan[5]))>self.rwidth+1 or abs(float(scan[5]))<1-self.rwidth:
		badscans.append(scan)
		print "appended {0}".format(scan)
		continue

	    #relative offset check
	    if abs(float(scan[7]))>self.roffset+1 or abs(float(scan[7]))>1-self.roffset:
		badscans.append(scan)
		print "appended {0}".format(scan)
		continue

	self.badscans = badscans"""
    
