# GBT-Pointing

The goal of this repository is to compile and document programs which are currently used to reduce GBT pointing runs and convert them into useable TPOINT file formats. Here are some initial notes...

The program which will create the .pns files is the version called makepns.py located in /users/ewhite/pointing/preprocessing/makepns.py. It makes both the .pns files and the necessary lambdas files. 

The lambdas files and pns files will be saved in the directory /users/ewhite/tpoint-inputs/xband/. Lines in the code can be modified such that these files are saved to the directory of your choice. 

You will now need to go through and change the scans range in each of the sessions' pns files as they will be set to incorrect defaults. Find the total number of scans using psum, and enter it into the "scans" field in each pns file. 

Run univPoint on each pns file. 

Run utpmake (version TBA...)

-- Ellie White, 18 Sept. 2019
