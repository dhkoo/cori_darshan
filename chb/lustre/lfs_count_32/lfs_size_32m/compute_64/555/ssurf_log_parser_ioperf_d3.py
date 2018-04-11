'''
Version: Wed Jun  1 12:58:36 PDT 2016

python ./ssurf_log_parser_ioperf_d3.py -s -b -n 2 -i ./darshan_base.txt > ./io_perf.txt

python ./ssurf_log_parser_ioperf_d3.py -s -n 2 -i ./darshan_all.txt > ./io_perf.txt

'''

import sys, getopt, os, argparse
import time
import datetime
import random
import fileinput
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

from datetime import datetime, date, time
from multiprocessing import Process, Queue, current_process, freeze_support, Pool

#def search_item(mystype, mytype, mylist):
#    return [element for element in mylist if element[mystype] == mytype]
def search_item(mystype, mytype, mylist):
    return [element for element in mylist if (mytype in element[mystype])]

def search_item_flash(mystype, mytype, mylist):
    return [element for element in mylist if element[mystype] == mytype]

mpi_p_t=0.0
mpi_p_r=0.0
mpi_p_p=0.0
posix_p_t=0.0
posix_p_r=0.0
posix_p_p=0.0

#input_file = "/Users/asim/Desktop/amrex/runs/a04/darshan_all.txt"
#dirpath="/Users/asim/Desktop/amrex/runs/a04"
#f_input_file = "amrex.io.txt"
#input_file = "darsian_all.txt"
input_file = ""
f_input_file = ""
save_flag = False
filesize_flag = 1 

baseflag=False

parser = argparse.ArgumentParser(description='Subsurface/DARSHAN3 IO LOG parser')
parser.add_argument("-i", "--input", action="store", dest="input_file", required=True, help="input file path")
parser.add_argument("-s", "--save", action="store_true", dest="save_flag", required=False, help="saving plots")
parser.add_argument("-n", "--num", action="store", dest="filesize_flag", required=False, help="1:12173801392, 2:15659856800, 3:15666741176")
parser.add_argument("-b", "--base", action="store_true", dest="baseflag", required=False, help="darshan base output")

#args = parser.parse_args(['-s', 
#    '-i', '/Users/asim/Desktop/ssurf/runs/s07/darshan_all.txt')
args = parser.parse_args()     # uncomment this line for general use

input_file = args.input_file
if (args.save_flag): 
    save_flag = args.save_flag
if (args.baseflag): 
    baseflag = args.baseflag
if (args.filesize_flag): 
    filesize_flag = int(args.filesize_flag)

plot_sizes={}

if (filesize_flag == 1) :
    # for sample case
    plot_sizes['phi00.hdf5'] = 24782901464
elif (filesize_flag == 2) :
    plot_sizes['phi00.hdf5'] = 469959899089
elif (filesize_flag == 3) :  ## SNU run 11246966
    plot_sizes['sim_phi00.hdf5'] = 669137866376
elif (filesize_flag == 4) :  ## SNU run 11246777
    plot_sizes['sim_phi00.hdf5'] = 198263082992
else : 
    plot_sizes['phi00.hdf5'] = 24782901464

ax = plt.gca()
ax.ticklabel_format(useOffset=False)
ax.get_yaxis().get_major_formatter().set_useOffset(False)
      
fplot, (plotp) = plt.subplots(1, sharex=True, figsize=(11, 8))
plotp.set_title("time vs output files", fontsize=11)

###########################################################################
###########################################################################
posix_list=[]
posix_hash_list=[]
mpiio_list=[]
mpiio_hash_list=[]
rank=-100
hashname=" "
name=" "
rsize=0
write_time=0.0
meta_time=0.0

for line in fileinput.input([input_file], mode='r'):
    if (len(line) > 1):
        #print len(line), ":", line
        parsed = line.split()
    
        #for i in range(len(parsed)):
        #    print i, " = ", parsed[i]

        if (baseflag):
            if (parsed[1] == "-1"):        
                if (parsed[0] == "POSIX"):
                    if (parsed[3] == "POSIX_BYTES_WRITTEN") :
                        hashname=parsed[2]  # 3414876530736194290
                        name=(parsed[5].split('/'))[-1]   # sedov_hdf5_plt_cnt_0001
                        rsize = int(parsed[4])
                
                    if (parsed[3] == "POSIX_F_SLOWEST_RANK_TIME"):
                        start_time = float(parsed[4])
                
                        flash_dict = {
                            'hashname': hashname,  # 13919071261708348485
                            'name': name,   # sedov_hdf5_plt_cnt_0001
                            'time': start_time
                        }
                        posix_list.append(flash_dict)
                        if (hashname not in posix_hash_list):
                            posix_hash_list.append(hashname)

                elif (parsed[0] == "MPI-IO"):
                    if (parsed[3] == "MPIIO_BYTES_WRITTEN") :
                        hashname=parsed[2]  # 3414876530736194290
                        name=(parsed[5].split('/'))[-1]   # sedov_hdf5_plt_cnt_0001
                        rsize = int(parsed[4])
                
                    if (parsed[3] == "MPIIO_F_SLOWEST_RANK_TIME"):
                        start_time = float(parsed[4])
                                
                        flash_dict = {
                            'hashname': hashname,  # 13919071261708348485
                            'name': name,   # sedov_hdf5_plt_cnt_0001
                            'time': start_time
                        }
                        mpiio_list.append(flash_dict)
                        if (hashname not in mpiio_hash_list):
                            mpiio_hash_list.append(hashname)
        else:  
            if (parsed[0] == "POSIX"):
                if (parsed[3] == "POSIX_BYTES_WRITTEN") :
                    rank=int(parsed[1]) # rank
                    hashname=parsed[2]  # 3414876530736194290
                    name=(parsed[5].split('/'))[-1]   # sedov_hdf5_plt_cnt_0001
                    rsize = int(parsed[4])
                
                if (parsed[3] == "POSIX_F_WRITE_TIME"):
                    write_time = float(parsed[4])
                
                if (parsed[3] == "POSIX_F_META_TIME"):
                    meta_time = float(parsed[4])
                
                    flash_dict = {
                        'rank': rank, # rank
                        'hashname': hashname,  # 13919071261708348485
                        'name': name,   # sedov_hdf5_plt_cnt_0001
                        'time': (write_time + meta_time)
                    }
                    posix_list.append(flash_dict)
                    if (hashname not in posix_hash_list):
                        posix_hash_list.append(hashname)
                        #print "POSIX list len = ", len(posix_hash_list)

            elif (parsed[0] == "MPI-IO"):
                if (parsed[3] == "MPIIO_BYTES_WRITTEN") :
                    rank=int(parsed[1]) # rank
                    hashname=parsed[2]  # 3414876530736194290
                    name=(parsed[5].split('/'))[-1]   # sedov_hdf5_plt_cnt_0001
                    rsize = int(parsed[4])
                
                if (parsed[3] == "MPIIO_F_WRITE_TIME"):
                    write_time = float(parsed[4])
                
                if (parsed[3] == "MPIIO_F_META_TIME"):
                    meta_time = float(parsed[4])
                
                    flash_dict = {
                        'rank': rank, # rank
                        'hashname': hashname,  # 13919071261708348485
                        'name': name,   # sedov_hdf5_plt_cnt_0001
                        'time': (write_time + meta_time)
                    }
                    mpiio_list.append(flash_dict)
                    if (hashname not in mpiio_hash_list):
                        mpiio_hash_list.append(hashname)
                        #print "MPIIO list len = ", len(mpiio_hash_list)

#print "POSIX:", len(posix_list), posix_list[0]
#print "MPIIO:", len(mpiio_list), mpiio_list[0]


names=[]    # filenames
xaxis=[]    # start/end time
yaxis=[]    # duration 

#ax = plt.gca()
#ax.ticklabel_format(useOffset=False)
#ax.get_yaxis().get_major_formatter().set_useOffset(False)
#fplot, (plotp, plotc) = plt.subplots(2, sharex=True, figsize=(11, 8))
#fplot, (plotp) = plt.subplots(1, sharex=True, figsize=(11, 8))
#plotp.set_title("time vs output files", fontsize=11)
#results = [item for item in flash_list if item["type"] == "plotfile"]
# for plotfile
r_plots = search_item('name', 'phi', posix_list)

print "=============================================================================="
print "POSIX: plot_filename\ttime\tsize (B)\tsize (GB)\tB/sec\tGB/sec"
total_time = 0.0  # in seconds
total_size = 0  # bytes
pcount=0
maxrate=0.0
maxfile=''
minrate=80000000000.0
minfile=''
for fi in posix_hash_list:
    matching = search_item('hashname', fi, r_plots)
    if (len(matching)>0):
        pcount+=1
        time_list = []
        for j in range(0,len(matching)) :
            time_list.append(matching[j]['time'])
        t_diff = max(time_list)
        f_size = plot_sizes[matching[0]['name']]
        total_size += f_size
        o_rate = float(f_size)/float(t_diff) # B/sec
        if (pcount == 1):
            maxrate = o_rate
            maxfile = matching[0]['name']
            minrate = o_rate
            minfile = matching[0]['name']
        else:
            if (o_rate > maxrate):
                maxrate = o_rate
                maxfile = matching[0]['name']
            elif (o_rate < minrate):
                minrate = o_rate
                minfile = matching[0]['name']
        #print fi['name'], " " , t_diff, " ", fi['time'], " ", matching[0]['time'], " ", o_rate, " ", o_rate/1024/1024
        print matching[0]['name'], " " , t_diff, " ", f_size, " ", float(f_size)/1024/1024/1024, " ", o_rate, " ", o_rate/1024/1024/1024
        total_time += t_diff
        plt.scatter(pcount, o_rate, s=10, marker='s', color="blue")
        #plt.hold(True)
    #else :
    #    print fi, ": no plot matching"
#plt.legend(bbox_to_anchor=(0.95, 0.18), loc=1, fontsize=10)
#plt.legend(loc=4, fontsize=10)
#plt.gcf().autofmt_xdate()
#plt.xlabel('time')
#plt.ylabel('filename')
#plt.show()

print "Total_plotfile ", total_time, " seconds for ", total_size/1024/1024/1024, "GB =", total_size, "Bytes"
print "Rate_plotfile ", float(total_size)/float(total_time), "B/sec = ", float(total_size)/float(total_time)/1024/1024/1024, "GB/sec"
print "------------------------------------------------------------------------------"
print "POSIX: IO time Plotfile\tGB/s Plotfile\tmax GB/s Plot\tmax file Plot\tmin GB/s Plot\tmin file Plot"
print total_time, "\t", float(total_size)/float(total_time)/1024/1024/1024, "\t", maxrate, "\t", maxfile, "\t", minrate, "\t", minfile

posix_p_t=total_time
posix_p_r=float(total_size)/float(total_time)/1024/1024/1024
posix_p_p=maxrate
posix_a=float(total_size)/float(total_time)/1024/1024/1024

#########################
# MPIIO plot files
r_plots = search_item('name', 'phi', mpiio_list)

print "=============================================================================="
print "MPIIO: plot_filename\ttime\tsize (B)\tsize (GB)\tB/sec\tGB/sec"
total_time = 0.0  # in seconds
total_size = 0  # bytes
pcount=0
maxrate=0.0
maxfile=''
minrate=80000000000.0
minfile=''
for fi in mpiio_hash_list:
    matching = search_item('hashname', fi, r_plots)
    if (len(matching)>0):
        pcount+=1
        time_list = []
        for j in range(0,len(matching)) :
            time_list.append(matching[j]['time'])
        t_diff = max(time_list)
        f_size = plot_sizes[matching[0]['name']]
        total_size += f_size
        o_rate = float(f_size)/float(t_diff) # B/sec
        if (pcount == 1):
            maxrate = o_rate
            maxfile = matching[0]['name']
            minrate = o_rate
            minfile = matching[0]['name']
        else:
            if (o_rate > maxrate):
                maxrate = o_rate
                maxfile = matching[0]['name']
            elif (o_rate < minrate):
                minrate = o_rate
                minfile = matching[0]['name']
        #print fi['name'], " " , t_diff, " ", fi['time'], " ", matching[0]['time'], " ", o_rate, " ", o_rate/1024/1024
        print matching[0]['name'], " " , t_diff, " ", f_size, " ", float(f_size)/1024/1024/1024, " ", o_rate, " ", o_rate/1024/1024/1024
        total_time += t_diff
        plt.scatter(pcount, o_rate, s=10, marker='s', color="red")
        #plt.hold(True)
    #else :
    #    print fi, ": no plot matching"
#plt.legend(bbox_to_anchor=(0.95, 0.18), loc=1, fontsize=10)
#plt.legend(loc=4, fontsize=10)
#plt.gcf().autofmt_xdate()
#plt.xlabel('time')
#plt.ylabel('filename')
#plt.show()

print "Total_plotfile ", total_time, " seconds for ", total_size/1024/1024/1024, "GB =", total_size, "Bytes"
print "Rate_plotfile ", float(total_size)/float(total_time), "B/sec = ", float(total_size)/float(total_time)/1024/1024/1024, "GB/sec"
print "------------------------------------------------------------------------------"
print "MPIIO: IO time Plotfile\tGB/s Plotfile\tmax GB/s Plot\tmax file Plot\tmin GB/s Plot\tmin file Plot"
print total_time, "\t", float(total_size)/float(total_time)/1024/1024/1024, "\t", maxrate, "\t", maxfile, "\t", minrate, "\t", minfile

mpi_p_t=total_time
mpi_p_r=float(total_size)/float(total_time)/1024/1024/1024
mpi_p_p=maxrate
mpi_a=float(total_size)/float(total_time)/1024/1024/1024


print "=============================================================================="
print "#######################################################################"
print "M Time Plotfile\tM GB/s Plotfile\tM Peak Plotfile\tM ave GB/s\tP Time Plotfile\tP GB/s Plotfile\tP Peak Plotfile\tP ave GB/s"
print mpi_p_t, "\t", mpi_p_r, "\t", mpi_p_p, "\t",  mpi_a, "\t", posix_p_t, "\t", posix_p_r, "\t", posix_p_p, "\t", posix_a

ax = plt.gca()
ax.ticklabel_format(useOffset=False)
ax.get_yaxis().get_major_formatter().set_useOffset(False)

plt.xlim((0,pcount+1))
plt.grid()
plt.xlabel('file number')
plt.ylabel('rate (bytes per second)')
textstr="blue: POSIX plotfile\nred: MPIIO plotfile"
props = dict(boxstyle='round', facecolor="white", alpha=0.9)
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=7,
        verticalalignment='top', bbox=props)
if (args.save_flag):
    outplot_name = "io_perf_d3.png"
    print "output plot filename=", outplot_name
    plt.savefig(outplot_name, dpi=150)
else:
    plt.show()
    #plt.close('all')
