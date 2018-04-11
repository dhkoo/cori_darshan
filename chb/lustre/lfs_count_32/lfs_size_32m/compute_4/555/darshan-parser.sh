#!/bin/sh

MYDS=$1
JID=$2

if [ -f "$MYDS" ]; then
	darshan-job-summary.pl $MYDS --output darshan_sum-$JID.pdf
	darshan-parser --perf --all $MYDS  > darshan_all-$JID.txt
	darshan-dxt-parser $MYDS > darshan_dxt-$JID.txt
else
    echo "./$MYDS does not exist"
    echo "command job_id target_dir option [all sum allsum basesum]"
    echo "  e.g. ./3-darshan.sh s10 basesum 826043"
    exit 123;
fi
