#recType

import os

def recType(fpath):
    subdirs = os.listdir(fpath)
    if "Rcvr8_10" in subdirs:
	return "X/DCR"
    elif "Rcvr68_92" in subdirs:
	return "W/DCR"
    elif "RcvrArray18_26" in subdirs:
	return "KFPA/DCR"
    elif "RcvrArray75_115" in subdirs:
	return "Argus/DCR"
