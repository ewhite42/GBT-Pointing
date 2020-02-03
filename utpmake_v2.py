#!/opt/local/bin/python

# Most recent version: edited 11/14/17

# Original program written by Frank Ghigo, 
# additional functionality added later by Ellie White

# FDG: revised Dec 2017 to add "trackpath" to .pns file;
#	also fix bug in "clam" and allow 8 columns in track map file.

#----------------------------------------------------------
# tpmake - make the input file for tpoint
#          Use either the Focus or AzEl csv file.
# utpmake - universal version - uses the univ spec file.
#----------------------------------------------------------

# to run on an AzEL file:
#   h,c = rcsv('NewTrackAzElDec2007.csv')  [for example]
#   wazel('NewTrackAzElDec2007.csv', h,c, 'lambda_Model5e.out')   
#       [give it a track lambda file]
#       [output tpoint file will be: NewTrackAzElDec2007.tpz]
#
# to run on a Focus file:
#   h,c = rcsv('NewTrackFocusDec2007.csv') 
#   wfocus('NewTrackFocusDec2007.csv', h,c, 'lambda_Model5e.out')   
#       [output tpoint file will be: NewTrackFocusDec2007.tpf]
#   
#
import os
import sys
import math
from heuristicsCheck import HeuristicsCheck as hcheck

global headc

#---------------------------------------------------------------
# rcsv - read the csv file into a big array
def rcsv(csvname) :
  global headc
  nlines = 0
  ncols = 20
  headc = {}       # dictionary for header items
  csvdat = []

  csvf = open(csvname)
  for cc in csvf :
    c = cc.split(',')
    if len(c) < ncols  : continue      # skip blank lines
    c0 = c[0].strip()
    if c0[0] == '#' : continue         # skip comment lines

    c1 = []
    for a in c : c1.append(a.strip())  # remove blanks
      
    # detect the header line
    if c1[0].find('Project') >= 0 :
      ncols = len(c1)
      nlines=nlines+1
      # headc = c1
      # identify the columns 
      icol=0
      for a in c1 :
        headc[a] = icol
        # print "indices:", icol,iproj,itype,ipol,iscan,imjd,isrc,ipmod,ioff
        icol = icol+1

    else :     # non-header lines
      csvdat.append( c1 )
      nlines=nlines+1

  csvf.close()

  print "read ", nlines, " lines,", ncols, " cols"
  # print csvdat[-1]

  return (headc, csvdat)


#-----------------------------------------------------------
# read and parse the specification file
#   ufilename is the name of the spec file
#   output:  datapath and pdict
#            pdict is a dictionary: { projcode:(projdir,logpath,scanlist), ... }
#-----------------------------------------------------------
def parspec(ufilename=None) :
  if ufilename==None :
    print "You must specify a spec file"
    return None,None

  datapath = ''
  azelname = ''
  focusname = ''
  modelname = ''
  pdict = dict()    # a dictionary for the project information
  # make a list of projects in the order that they occur in the file
  plist = []

  uu = open(ufilename)
  icont=0
  oldvv = ''
  oldproj = ''
  oldpdir = ''
  oldlog = ''
  oldscans=''
  oldtrack=''
  oldprojoff = ''
  oldbeamoff = ''
  maxwind = ''
  elevspan = ''
  nproj = 0

  for u in uu :
    su = u.split('=')
    if su[0] == '#' : continue

    if len(su) > 1 or icont==1 :
      if icont==1 :
        vv = oldvv[0:-1] + su[0].strip()
      else :
        kw = su[0].strip()
        vv = su[1].strip()
        if kw == 'datapath' : datapath=vv
        if kw == 'model'    : modelname=vv
        if kw == 'azel'     : azelname =vv
        if kw == 'focus'    : focusname =vv
        if kw == 'elevspan' : elevspan = vv
        if kw == 'maxwind'  : maxwind  = vv

        if nproj > 0 and kw=='project' :
          pdict[oldproj] = (oldpdir,oldlog, oldscans, oldbeamoff, oldprojoff, oldtrack)
          plist.append(oldproj)
        if kw == 'project' : nproj=nproj+1

      if vv[-1] == '\\' : icont=1  # allow for continuation on next line
      else : icont=0

      oldvv = vv
      if kw == 'scans' : oldscans=oldvv
      if kw == 'project' : oldproj = vv
      if kw == 'projdir' : oldpdir = vv
      if kw == 'logpath' : oldlog = vv
      if kw == 'trackpath' : oldtrack = vv
      if kw == 'beamoff'  : oldbeamoff = vv
      if kw == 'projoff'  : oldprojoff = vv

  uu.close()

  # last project
  pdict[oldproj] = (oldpdir,oldlog, oldscans, oldbeamoff, oldprojoff, oldtrack)
  plist.append(oldproj)

  print nproj, " sessions found"
  for p in plist : print p
  # for p in pdict : print p

  return pdict, plist, (datapath,azelname,focusname,modelname), \
	(elevspan,maxwind)


#---------------------------------------------------------------
# mjdsortfunc - used to sort the csvdat array into MJD order
def mjdsortfunc ( a, b ) :
  global headc
  diff = float(a[headc['MJDate']]) - float(b[headc['MJDate']]) 
  if diff < 0.0 : iretval = -1
  elif diff == 0.0 : iretval = 0
  else             : iretval = 1
  return iretval


#---------------------------------------------------------------
# getst - get the combinations of the structural temps
def getst( cc, h) :
  # Temperature sensor readings.
  TF1 = float(cc[h['gbtts1_2001']])
  TSR = float(cc[h['gbtts1_2005']])
  TB1 = float(cc[h['gbtts2_2001']])
  TF2 = float(cc[h['gbtts2_2002']])
  TF3 = float(cc[h['gbtts2_2004']])
  TF4 = float(cc[h['gbtts3_2001']])
  TB2 = float(cc[h['gbtts3_2002']])
  TF5 = float(cc[h['gbtts3_2003']])
  TH1 = float(cc[h['gbtts4_2001']])    # error fixed Nov 2013(TH1,TH2 had been switched)
  TH2 = float(cc[h['gbtts3_2004']])
  TE1 = float(cc[h['gbtts4_2002']])
  TE2 = float(cc[h['gbtts4_2003']])
  TB3 = float(cc[h['gbtts4_2004']])
  TB4 = float(cc[h['gbtts4_2005']])
  TB5 = float(cc[h['gbtts4_2006']])
  TA1 = float(cc[h['gbtts5_2001']])
  TA2 = float(cc[h['gbtts5_2002']])
  TA3 = float(cc[h['gbtts5_2003']])
  TA4 = float(cc[h['gbtts5_2004']])

  # average structural temp
  i11 = h['gbtts1_2001']
  i54 = h['gbtts5_2004']
  tav = 0.0 ; itav=0
  for i in range(i11,i54+1) : 
    tav = tav + float(cc[i])
    itav=itav+1

  tav = tav/itav

  # T5E term to match matlab:
  T5E = ( TH1 + TH2 + TF2 + TF3 + TF4 + TF5)/6.0

  # Elevation and cross-azimuth temperature differences.
  T1E = (TB3+TB4+TB5)/3.0 - (TB1+TB2)/2.0
  T2E = (TH2-TE1)/2.0 + (TH1-TE2)/2.0
  T3E = (TF2+TF4)/2.0 - (TF3+TF5)/2.0
  T4E = (TA1+TA2)/2.0 - (TA3+TA4)/2.0
  T1V = (TA1+TA3)/2.0 - TE1 - (TA2+TA4)/2.0 + TE2
  T2A = (TH2-TE1)/2.0 - (TH1-TE2)/2.0
  T3A = (TB1+TB4)/2.0 - TE1 - (TB2+TB3)/2.0 + TE2
  T4A = (TF2+TF3)/2.0 - (TF4+TF5)/2.0
  # add minus sign to match how matlab calculates t5v
  # actually it should not have the minus - tpoint multiplies by -sinEl
  T5V = ( (TA2+TA3+TE2)/3.0 - (TA1+TA4+TE1)/3.0)
  # T5V = -( (TA2+TA3+TE2)/3.0 - (TA1+TA4+TE1)/3.0)
  T6A =  TA4-TA1-TA3+TA2

  avals = (T1V,T2A,T3A,T4A,T5V,T6A)
  evals = (T1E,T2E,T3E,T4E)
  # raw temperature readings
  rawtemps = (TF1, TSR, TB1, TF2, TF3, TF4, TB2, TF5, TH1, TH2, TE1, TE2, TB3, TB4, TB5, TA1, TA2, TA3, TA4)
  # return (avals,evals,tav)

  return (avals,evals,T5E, rawtemps)


#----------------------------------------------------------------
# read in the lambda table
# using new X,Y,lambda tables
# should work with the old format (Az,L1,L2,L3) as well as with 
# the new bigger tables (Az, L1, L2, L3, X1,X2,Y1,Y2)
def rlam(lamname) :
  lamf = open(lamname)
  dlam = []

  for ll in lamf :
    lm = ll.split()
    if len(lm) < 4 : continue
    l1 = lm[0]
    if l1[0] == '#' : continue

    if len(lm) > 7 :    # 8 columns
      dlam.append( [float(lm[0]), float(lm[1]), float(lm[2]), float(lm[3]), \
	float(lm[4]), float(lm[5]), float(lm[6]), float(lm[7]) ] )

    else :   # old version with 4 columns
      dlam.append( [float(lm[0]), float(lm[1]), float(lm[2]), float(lm[3]) ] )
 
  lamf.close()
  return dlam


#---------------------------------------------------------------
# find the lambda correction for given azimuth
def clam( az, dlam) :
  # put azimuth into 0-360 range
  if az > 360.0 : az = az-360.0
  if az < 0.0 : az = az+360.0
  lvals = []

  # how many colums in lam array?
  ncols = len(dlam[0]) -1
  
  # should work for 4-column and 8-column lambda tables.

  # find this azimuth in the dlam array - binary search
  j1 = 0
  j2 = len(dlam) 
  while (j2-j1)>1 :
    jc = int((j1+j2)/2)
    if ( az < dlam[jc][0]) : j2 = jc
    else :                   j1 = jc

  az1 = dlam[j1][0]
  if ncols < 5 :
    mm1 = [dlam[j1][1], dlam[j1][2], dlam[j1][3] ]
  else :
    mm1 = [dlam[j1][1], dlam[j1][2], dlam[j1][3], dlam[j1][4], dlam[j1][5], dlam[j1][6], dlam[j1][7] ]

  if j2 >= len(dlam) :  # fix problem with az between 359.9 and 360
    j2=0
    az2 = dlam[j2][0] + 360.0
  else :
    az2 = dlam[j2][0]

  if ncols < 5 :
    mm2 = [dlam[j2][1], dlam[j2][2], dlam[j2][3] ]
  else :
    mm2 = [dlam[j2][1], dlam[j2][2], dlam[j2][3], dlam[j2][4], dlam[j2][5], dlam[j2][6], dlam[j2][7] ]
  
  for i in range(ncols) :
    vinterp = mm1[i] + (mm2[i] - mm1[i]) * (az-az1)/(az2-az1)
    lvals.append(vinterp)
    
  # print " vals=",lvals
  return lvals

#---------------------------------------------------------------
# if its a FOCUS file, write the TPOINT data
def wfocus(csvname, h,c, lambdaname) :
  global maxwind, maxelev, minelev
  global pdict, plist

  # check that the obstype is "focus"
  if c[0][h['ObsType']] != 'FocusF' : 
    print "not a focus file "
    return

  alphaseq = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N', \
	'O','P','Q','R','S','T','U','V','W','X','Y','Z']

  # open the tpoint data file
  # use the name of the csv file and use a suffix of "tpf"
  idot = csvname.find('.')
  newname = csvname[0:idot]+'.tpf'

  # read the lambda file
  dlam = rlam(lambdaname)

  oldproj = ''
  iprj = 0
  njacks=0

  tpf = open(newname, 'w')
  # write the tpoint header
  tpf.write('GBT\n')
  tpf.write(': NODA\n')
  tpf.write(': ALLSKY\n')
  tpf.write(': ALTAZ\n')
  tpf.write('+38 25 59\n')

  for cs in c :
    # only print one pol - the coordinates are the same for both.
    poltype = cs[h['Pol']]
    if poltype != 'RCP' : continue  

    projid = cs[h['ProjectID']]   # get project identifier
    ip = projid.find('_')
    pdat = projid[ip+1:]     # last part of project ID
    if pdat != oldproj :
      # read the lambda file for this project
      ppdat = pdict[projid]
      lambdaname = ppdat[5]
      dlam = rlam(lambdaname)
      print 'Project:',projid, ' lambdafile=', lambdaname

      if iprj > 25 :
        # if more than 26 projects !
        tpf.write('D/JJ%s      ! %s\n' % (pdat, pdat))
      else :
        tpf.write('D/%s      ! %s\n' % (alphaseq[iprj], pdat))
      oldproj=pdat
      iprj=iprj+1

    obscaz = float(cs[h['Obsc_Az']])
    obscel = float(cs[h['Obsc_El']])
    if cs[h['SMNTC_AZ']] == '' :
      mntcaz = float(cs[h['Mnt_Az']])
      mntcel = float(cs[h['Mnt_El']])
    else :
      mntcaz = float(cs[h['SMNTC_AZ']])
      mntcel = float(cs[h['SMNTC_EL']])

    # get offsets if any
    ppdat = pdict[projid]
    bmoff = ppdat[3]
    if bmoff != '' :
      bbm = bmoff.split()   # beam corrections are in xel,el
      azbcorr = (float(bbm[0])/3600.0)/math.cos(obscel*math.pi/180.0) 
      elbcorr = float(bbm[1])/3600.0
      mntcaz = mntcaz - azbcorr
      mntcel = mntcel - elbcorr
    proff = ppdat[4]
    if proff != '' :
      pbm = proff.split()
      azpcorr = float(pbm[0])/3600.0 # subtract project-dependent corrections
      elpcorr = float(pbm[1])/3600.0  # in AZ and  EL
      mntcaz = mntcaz - azpcorr
      mntcel = mntcel + elpcorr

    # print 'applying correction', projid, zxelcorr, zelvcorr

    # is it KA-band?
    # obfreq = float(cs[h['ObsFreq']])
    # if obfreq > 26.0 :
    #   qkaband=True
    #   xelcorr = 39.0
    #   elvcorr = 67.0
    #   mntcaz = mntcaz - ( (xelcorr/3600.0)/math.cos(obscel*math.pi/180.0) )
    #   mntcel = mntcel - (elvcorr/3600.0)

    # select on elevation and wind speed.
    wvel = float(cs[h['WindVel']])
    if wvel > maxwind or obscel>maxelev or obscel<minelev : continue

    # add the refraction term if necessary
    rferr = float(cs[h['RefractError']]) * float(cs[h['NewRefModelVal']])
    obscel = obscel + rferr

    tpf.write( '%11.6f%11.6f%11.6f%11.6f & \\\n' \
	% (obscaz,obscel,mntcaz,mntcel) )

    # write the temperature terms
    avals,evals,tav = getst(cs,h)
    tpf.write('%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f \\\n' % \
	(avals[0],avals[1],avals[2],avals[3],evals[0],evals[1],evals[2],evals[3],tav))
    tpf.write('%+8.3f%+8.3f' % (avals[4],avals[5]))

    # write the lambda terms
    lamvals = clam(obscaz,dlam)
    tpf.write('%+8.3f%+8.3f%+8.3f\n' % (lamvals[0],lamvals[1],lamvals[2]))

    njacks=njacks+1

  tpf.write('END\n')
  tpf.close()

  print "Wrote ", newname, ",", iprj, " projects, ", njacks, "jacks"
#---------------------------------------------------------------



#---------------------------------------------------------------
# if its an AzEl file, write the TPOINT data
def wazel(csvname, h,c, lambdaname) :
  global maxwind, maxelev, minelev

  # check that the obstype is "AzEl"
  atypes = ['AzF','AzB','ElF','ElB']
  if c[0][h['ObsType']] not in atypes : 
    print "not an AzEl file "
    return

  alphaseq = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N', \
	'O','P','Q','R','S','T','U','V','W','X','Y','Z']

  # open the tpoint data file
  # use the name of the csv file and use a suffix of "tpz"
  idot = csvname.find('.')
  newname = csvname[0:idot]+'.tpz'

  # make sure the data are sorted in MJD order
  c.sort(mjdsortfunc)

  # read the lambda file
  dlam = rlam(lambdaname)

  oldproj = ''
  iprj = 0  # project counter
  kseq=0    # sequence counter
  zseq = -1
  nlines = 0
  njacks=0 
  okjacks =0 
  pscan = 0  # previous scan number
  dtr = math.pi/180.0   # degrees per radian

  tpf = open(newname, 'w')
  # write the tpoint header
  tpf.write('GBT\n')
  tpf.write(': NODA\n')
  tpf.write(': ALLSKY\n')
  tpf.write(': ALTAZ\n')
  tpf.write('+38 25 59\n')

  #make list of projects, then run prepoint to create heuristics for each project
  projlist = []
  for cs in c:
      projid = cs[h['ProjectID']]
      if projid not in projlist:
	  projlist.append(projid)
  for projid in projlist:
      hck = hcheck(projid)
      hck.run()

  for cs in c :
    # add project identifier
    projid = cs[h['ProjectID']]
    ip = projid.find('_')
    pdat = projid[ip+1:]     # last part of project ID
    if pdat != oldproj :
      # read the lambda file for this project
      ppdat = pdict[projid]
      lambdaname = ppdat[5]
      dlam = rlam(lambdaname)
      print 'Project:',projid, ' lambdafile=', lambdaname

      if iprj > 25 :
        # if more than 26 projects !
        tpf.write('! %s\n' % (pdat))
      else :
        tpf.write('! %s\n' % (pdat))

      oldproj=pdat
      iprj=iprj+1

    obstype = cs[h['ObsType']]
    scannum = int(cs[h['Scan']])
    offset  = float(cs[h['Value']])
    obsaz  = float(cs[h['Obsc_Az']])
    obsel  = float(cs[h['Obsc_El']])
    pol    = str(cs[h['Pol']])

    # print nlines, " ", obstype, " ", scannum, " ", pscan, " ", kseq, " ", zseq, " ", njacks
    nlines = nlines+1

    # compile the jack-scan sequences: 8 lines each
    if obstype == 'AzF':
      if kseq==0 or zseq == -1 :
        seqdat = []     # start new sequence
        pscan = scannum        # save scan num of 1st in sequence
        kseq=0
      if kseq >= 1 and (scannum-pscan) >= 1: continue   # skip if not in sequence
      seqdat.append( (scannum,obstype, offset, obsaz,obsel, pol) )
      zseq = 1
      kseq = kseq+1

    elif obstype == 'AzB':
      if (scannum-pscan) != 1 : continue             # skip if not in sequence
      seqdat.append( (scannum,obstype, offset, obsaz,obsel, pol) )
      kseq = kseq+1

    elif obstype == 'ElF':
      if (scannum-pscan) != 2 : continue             # skip if not in sequence
      seqdat.append( (scannum,obstype, offset, obsaz,obsel, pol) )
      # rememeber the temperature terms from the middle of the sequence
      avals,evals,tav, temps = getst(cs,h)
      kseq = kseq+1

    elif obstype == 'ElB':
      zseq = -1
      if (scannum-pscan) != 3 : continue             # skip if not in sequence
      seqdat.append( (scannum,obstype, offset, obsaz,obsel, pol) )
      kseq = kseq+1
 
    # here if sequence is complete
    if kseq == 8:

      #check that heuristics pass:
      hck = hcheck(projid)
      print "Checking jack {0}...".format(njacks +1)

      #Compare AzF, AzB, ElF, and ElB scans (both pol.'s)
      hpass1 = hck.checkScans(seqdat[0], seqdat[2], seqdat[4], seqdat[6])
      hpass2 = hck.checkScans(seqdat[1], seqdat[3], seqdat[5], seqdat[7])
      
      if hpass1 and hpass2:# and hpass3 and hpass4:
	  # average total corrections
          azave = 0.25*(seqdat[0][3] + seqdat[1][3] + seqdat[2][3] + seqdat[3][3])
          elave = 0.25*(seqdat[4][4] + seqdat[5][4] + seqdat[6][4] + seqdat[7][4])
          azoff = 0.25*(seqdat[0][2] + seqdat[1][2] + seqdat[2][2] + seqdat[3][2])
          eloff = 0.25*(seqdat[4][2] + seqdat[5][2] + seqdat[6][2] + seqdat[7][2])
          
	  el_mnt = elave + eloff/3600.0
          az_mnt = azave + azoff/(3600.0 * math.cos(dtr*el_mnt))

          kseq = 0
          # select on elevation and wind speed.
          wvel = float(cs[h['WindVel']])
          if wvel > maxwind or el_mnt>maxelev or el_mnt<minelev : continue

          # add the refraction term if necessary
          rferr = float(cs[h['RefractError']]) * float(cs[h['NewRefModelVal']])
          elave = elave + rferr

          tpf.write( '%11.6f%11.6f%11.6f%11.6f & \\\n' \
	    % (azave, elave, az_mnt, el_mnt ) )
          # write the temperature terms
          tpf.write('%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f \\\n' % \
	    (avals[0],avals[1],avals[2],avals[3],evals[0],evals[1],evals[2],evals[3],tav))
          tpf.write('%+8.3f%+8.3f' % (avals[4],avals[5]))
          # write the lambda terms
          lamvals = clam(azave,dlam)
          tpf.write('%+8.3f%+8.3f%+8.3f \\\n' % (lamvals[0],lamvals[1],lamvals[2]))

	  #write the raw temperature terms
	  tpf.write(' %+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f \\\n' % \
	 (temps[0],temps[1],temps[2],temps[3],temps[4],temps[5],temps[6], temps[7], temps[8]))
	  tpf.write(' %+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f%+8.3f \\\n' % \
	  (temps[9], temps[10], temps[11], temps[12], temps[13], temps[14], temps[15], temps[16], temps[17], temps[18]))

	  # write the extra raw track terms
          tpf.write('%+8.3f%+8.3f%+8.3f%+8.3f \n' % (lamvals[3],lamvals[4],lamvals[5], lamvals[6]))
           
          njacks = njacks+1
	  okjacks += 1

      else: 
	  njacks += 1

  tpf.write('END\n')
  tpf.close()

  print "Wrote ", newname, ",", iprj, " projects, ", okjacks, "jacks"


#---------------------------------------------------------------
# for test mode, write just az and el
def wtestmode(csvname, h,c, lambdaname) :

  # check that the obstype is "focus"
  if c[0][h['ObsType']] != 'FocusF' : 
    print "not a focus file "
    return

  # open the test data file
  # use the name of the csv file and use a suffix of "tpf"
  idot = csvname.find('.')
  newname = csvname[0:idot]+'.tst'
  tsf = open(newname, 'w')

  # read the lambda file
  # dlam = rlam(lambdaname)

  for cs in c :
    # only print one pol - the coordinates are the same for both.
    poltype = cs[h['Pol']]
    if poltype != 'RCP' : continue  

    projid = cs[h['ProjectID']]   # get project identifier

    obscaz = float(cs[h['Obsc_Az']])
    obscel = float(cs[h['Obsc_El']])
    tsf.write('%8.3f %8.3f\n' % (obscaz,obscel))

  tsf.close()


#---------------------------------------------------------------
# universal processing - focus only
#   h,c = rcsv('NewTrackFocusDec2007.csv') 
#   wfocus('NewTrackFocusDec2007.csv', h,c, 'lambda_Model5e.out')   
#   jwhich = 'focus' or 'azel'
#---------------------------------------------------------------
def uproc(specfile, jwhich, tmode=False) :
  global maxwind, maxelev, minelev
  global pdict, plist

  pdict, plist, (datapath,azelname,focusname,modelname), plimits \
	 = parspec(specfile)

  if plimits[0] != '' :        # elevspan
    pp = (plimits[0]).split()
    minelev = float(pp[0])
    maxelev = float(pp[1])
  if plimits[1] != '' :        # max wind
    maxwind = float(plimits[1])

  print "Limits=", maxwind, minelev, maxelev

  # default lambda file is first one in the list
  lambdafile = pdict[plist[0]][5]
  print 'lambdafile0=',lambdafile
  if lambdafile == '' :
    print 'Warning: need to specify trackpath ! \n'
    exit()

  focusfile = os.path.join(datapath,focusname)
  azelfile  = os.path.join(datapath,azelname)
  
  if jwhich == 'focus' :
    h,c = rcsv(focusfile)
    if tmode == True : wtestmode( focusfile, h,c, lambdafile)
    else             : wfocus( focusfile, h,c, lambdafile)
  else :
    h,c = rcsv(azelfile)
    wazel( azelfile, h,c, lambdafile)

  
#-------------------------------------------------
# to run as a script to produce the tpoint file
#   Usage: utpmake modelspecfile [focus|azel]  [-test]
#    (-test --> produce file for pointing test utility)
#-------------------------------------------------
"""nargs = len(sys.argv)
if nargs < 2 :
  print "Usage: utpmake modelspecfile"
else :
  sfile = sys.argv[1]
  tmode = False
  print "Pointing spec file=", sfile
  jwhich = 'azel'
  if nargs > 2 :
    for nn in range(2,nargs) :
      if sys.argv[nn] == "-test" : tmode=True
      else                       : jwhich = sys.argv[2]

  uproc(sfile,jwhich, tmode)"""

inp = str(input('What project? >>> '))
#nargs = len(inp.split(''))
#if nargs < 2 :
#  print "Usage: utpmake modelspecfile"
#else :
sfile = inp
tmode = False
print "Pointing spec file=", sfile
jwhich = 'azel'
#  if nargs > 2 :
#    for nn in range(2,nargs) :
#      if sys.argv[nn] == "-test" : tmode=True
#      else                       : jwhich = sys.argv[2]

uproc(sfile,jwhich, tmode)
