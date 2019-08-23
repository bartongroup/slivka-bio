#!/usr/bin/env python
# Copyright (C) 2004 Rune Linding & Lars Juhl Jensen - EMBL
# The DisEMBL is licensed under the GPL license
# (http://www.opensource.org/licenses/gpl-license.php)
# DisEMBL pipeline
#
# Modified to work with current versions of Biopython (1.7+)
# by Shyam Saladi (saladi1@illinois.edu), Janauary 2013 
# Bio:SeqIO completely replaces Bio:Fasta
#
# Modified to work with Python 3 and to be jabaws-compatible
# by Mateusz Warowny (mmwarowny@dundee.ac.uk), August 2018

import os
import sys
from subprocess import Popen, PIPE

from Bio import SeqIO

relpath = os.path.dirname(__file__) or os.curdir
NN_bin = os.path.join(relpath, 'disembl')
SG_bin = os.path.join(relpath, 'sav_gol')


def JensenNet(sequence):
    p = Popen(NN_bin, shell=True, stdin=PIPE, stdout=PIPE,
              stderr=sys.stderr, close_fds=True, universal_newlines=True)
    p.stdin.write('%s\n' % sequence)
    p.stdin.close()
    REM465 = []
    COILS = []
    HOTLOOPS = []
    for line in p.stdout:
        it = map(float, line.split())
        COILS.append(next(it))
        HOTLOOPS.append(next(it))
        REM465.append(next(it))
    return COILS, HOTLOOPS, REM465


def SavitzkyGolay(window, derivative, datalist):
    if len(datalist) < 2 * window:
        window = len(datalist) / 2
    elif window == 0:
        window = 1
    cmd = '{0} -V0 -D{1} -n{2},{2}'.format(SG_bin, derivative, window)
    p = Popen(cmd, shell=True,
              stdin=PIPE, stdout=PIPE, stderr=sys.stderr, close_fds=True)
    for data in datalist:
        p.stdin.write(b'%f\n' % data)
    p.stdin.close()
    p.wait()
    results = p.stdout.readlines()
    SG_results = [max(f, 0.0) for f in map(float, results)]
    return SG_results


def getSlices(NNdata, fold, join_frame, peak_frame, expect_val):
    slices = []
    inSlice = beginSlice = endSlice = maxSlice = 0
    for i in range(len(NNdata)):
        if inSlice:
            if NNdata[i] < expect_val:
                if maxSlice >= fold * expect_val:
                    slices.append([beginSlice, endSlice])
                inSlice = 0
            else:
                endSlice += 1
                if NNdata[i] > maxSlice:
                    maxSlice = NNdata[i]
        elif NNdata[i] >= expect_val:
            beginSlice = i
            endSlice = i
            inSlice = 1
            maxSlice = NNdata[i]
    if inSlice and maxSlice >= fold * expect_val:
        slices.append([beginSlice, endSlice])

    i = 0
    while i < len(slices):
        if (i + 1 < len(slices) and
                slices[i + 1][0] - slices[i][1] <= join_frame):
            slices[i] = [slices[i][0], slices[i + 1][1]]
            del slices[i + 1]
        elif slices[i][1] - slices[i][0] + 1 < peak_frame:
            del slices[i]
        else:
            i += 1
    return slices


def reportSlicesTXT(slices, sequence):
    if not slices:
        s = sequence.lower()
    else:
        if slices[0][0] > 0:
            s = sequence[0:slices[0][0]].lower()
        else:
            s = ''
        for i in range(len(slices)):
            if i > 0:
                sys.stdout.write(', ')
            sys.stdout.write('{}-{}'.format(slices[i][0] + 1, slices[i][1] + 1))
    print('')


def runDisEMBLpipeline():
    if len(sys.argv) == 2:
        smooth_frame = 8
        peak_frame = 8
        join_frame = 4
        fold_coils = 1.2
        fold_hotloops = 1.4
        fold_rem465 = 1.2
        file = str(sys.argv[1])
    else:
        print('Usage:')
        print('\tDisEMBL.py sequence_file \n')
        sys.exit(1)
    for record in SeqIO.parse(file, "fasta"):
        sequence = str(record.seq).upper()
        # Run NN
        COILS_raw, HOTLOOPS_raw, REM465_raw = JensenNet(sequence)
        # Run Savitzky-Golay
        REM465_smooth = SavitzkyGolay(smooth_frame, 0, REM465_raw)
        COILS_smooth = SavitzkyGolay(smooth_frame, 0, COILS_raw)
        HOTLOOPS_smooth = SavitzkyGolay(smooth_frame, 0, HOTLOOPS_raw)
        sys.stdout.write('> ' + record.id + '\n')
        sys.stdout.write('# COILS ')
        reportSlicesTXT(
            getSlices(COILS_smooth, fold_coils, join_frame, peak_frame, 0.43),
            sequence
        )
        sys.stdout.write('# REM465 ')
        reportSlicesTXT(
            getSlices(REM465_smooth, fold_rem465, join_frame, peak_frame, 0.50),
            sequence
        )
        sys.stdout.write('# HOTLOOPS ')
        reportSlicesTXT(
            getSlices(HOTLOOPS_smooth, fold_hotloops,
                      join_frame, peak_frame, 0.086),
            sequence
        )
        print('# RESIDUE\tCOILS\tREM465\tHOTLOOPS')
        for i in range(len(REM465_smooth)):
            print('{}\t{:.5f}\t{:.5f}\t{:.5f}'.format(
                sequence[i], COILS_smooth[i], REM465_smooth[i],
                HOTLOOPS_smooth[i]
            ))


runDisEMBLpipeline()
