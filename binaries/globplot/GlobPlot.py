#!/usr/bin/env python
# Copyright (C) 2003 Rune Linding - EMBL
# GlobPlot TM
# GlobPlot is licensed under the Academic Free license
#
# Modified to work with Python 3 and biopython 1.72 and to be jabaws-compatible
# by Mateusz Warowny (mmwarowny@dundee.ac.uk), August 2018

import os
import sys
from subprocess import Popen, PIPE

import Bio.SeqIO

relpath = os.path.dirname(__file__) or os.curdir


# Russell/Linding
RL = {
    'N': 0.229885057471264,
    'P': 0.552316012226663,
    'Q': -0.187676577424997,
    'A': -0.261538461538462,
    'R': -0.176592654077609,
    'S': 0.142883029808825,
    'C': -0.0151515151515152,
    'T': 0.00887797506611258,
    'D': 0.227629796839729,
    'E': -0.204684629516228,
    'V': -0.386174834235195,
    'F': -0.225572305974316,
    'W': -0.243375458622095,
    'G': 0.433225711769886,
    'H': -0.00121743364986608,
    'Y': -0.20750516775322,
    'I': -0.422234699606962,
    'K': -0.100092289621613,
    'L': -0.337933495925287,
    'M': -0.225903614457831
}


def Sum(seq, par_dict):
    sum = 0
    sums = []
    p = 1
    for residue in seq:
        parameter = par_dict.get(residue, 0)
        if p == 1:
            sum = parameter
        else:
            sum = sum + parameter  # *math.log10(p)
        sums.append(round(sum, 10))
        p += 1
    return sums


def getSlices(dydx_data, DOM_join_frame, DOM_peak_frame,
              DIS_join_frame, DIS_peak_frame):
    DOMslices = []
    DISslices = []
    in_DOMslice = 0
    in_DISslice = 0
    beginDOMslice = 0
    endDOMslice = 0
    beginDISslice = 0
    endDISslice = 0
    for i in range(len(dydx_data)):
        # close dom slice
        if in_DOMslice and dydx_data[i] > 0:
            DOMslices.append([beginDOMslice, endDOMslice])
            in_DOMslice = 0
        # close dis slice
        elif in_DISslice and dydx_data[i] < 0:
            DISslices.append([beginDISslice, endDISslice])
            in_DISslice = 0
        # elseif inSlice expandslice
        elif in_DOMslice:
            endDOMslice += 1
        elif in_DISslice:
            endDISslice += 1
        # if not in slice and dydx !== 0 start slice
        if dydx_data[i] > 0 and not in_DISslice:
            beginDISslice = i
            endDISslice = i
            in_DISslice = 1
        elif dydx_data[i] < 0 and not in_DOMslice:
            beginDOMslice = i
            endDOMslice = i
            in_DOMslice = 1
    # last slice
    if in_DOMslice:
        DOMslices.append([beginDOMslice, endDOMslice])
    if in_DISslice:
        DISslices.append([beginDISslice, endDISslice])
    i = 0
    while i < len(DOMslices):
        if (i + 1 < len(DOMslices) and
                DOMslices[i + 1][0] - DOMslices[i][1] < DOM_join_frame):
            DOMslices[i] = [DOMslices[i][0], DOMslices[i + 1][1]]
            del DOMslices[i + 1]
        elif DOMslices[i][1] - DOMslices[i][0] + 1 < DOM_peak_frame:
            del DOMslices[i]
        else:
            i += 1
    j = 0
    while j < len(DISslices):
        if (j + 1 < len(DISslices) and
                DISslices[j + 1][0] - DISslices[j][1] < DIS_join_frame):
            DISslices[j] = [DISslices[j][0], DISslices[j + 1][1]]
            del DISslices[j + 1]
        elif DISslices[j][1] - DISslices[j][0] + 1 < DIS_peak_frame:
            del DISslices[j]
        else:
            j += 1
    return DOMslices, DISslices


def SavitzkyGolay(window, derivative, datalist):
    SG_bin = os.path.join(relpath, 'sav_gol')
    cmd = '{0} -V0 -D{1} -n{2},{2}'.format(SG_bin, derivative, window)
    p = Popen(cmd, shell=True,
              stdin=PIPE, stdout=PIPE, stderr=sys.stderr, close_fds=True)
    for data in datalist:
        p.stdin.write(b'%f\n' % data)
    p.stdin.close()
    p.wait()
    results = p.stdout.readlines()
    p.stdout.close()
    SG_results = [float(result) for result in results]
    return SG_results


def reportSlicesTXT(slices, sequence, maskFlag):
    if maskFlag == 'DOM':
        coordstr = 'GlobDoms '
    elif maskFlag == 'DIS':
        coordstr = 'Disorder '
    else:
        raise SystemExit
    if slices == []:
        # by default the sequence is in uppercase which is our search space
        s = sequence
    else:
        # insert seq before first slide
        if slices[0][0] > 0:
            s = sequence[0:slices[0][0]]
        else:
            s = ''
        for i in range(len(slices)):
            # skip first slice
            if i > 0:
                coordstr = coordstr + ', '
            coordstr = coordstr + str(slices[i][0] + 1) + '-' + str(
                slices[i][1] + 1)
            # insert the actual slice
            if maskFlag == 'DOM':
                s = s + str.lower(sequence[slices[i][0]:(slices[i][1] + 1)])
                if i < len(slices) - 1:
                    s = s + str.upper(
                        sequence[(slices[i][1] + 1):(slices[i + 1][0])])
                # last slice
                elif slices[i][1] < len(sequence) - 1:
                    s = s + str.lower(
                        sequence[(slices[i][1] + 1):(len(sequence))])
            elif maskFlag == 'DIS':
                s = s + str.upper(sequence[slices[i][0]:(slices[i][1] + 1)])
                # insert untouched seq between disorder segments, 2-run labelling
                if i < len(slices) - 1:
                    s = s + sequence[(slices[i][1] + 1):(slices[i + 1][0])]
                # last slice
                elif slices[i][1] < len(sequence) - 1:
                    s = s + sequence[(slices[i][1] + 1):(len(sequence))]
    return s, coordstr


def run_glob_plot():
    if len(sys.argv) == 2:
        smoothFrame = 10
        DOM_joinFrame = 15
        DOM_peakFrame = 74
        DIS_joinFrame = 4
        DIS_peakFrame = 5
        file = str(sys.argv[1])
    else:
        print('Usage:')
        print('         ./GlobPipe.py FASTAfile')
        sys.exit(1)
    for record in Bio.SeqIO.parse(file, 'fasta'):
        # uppercase is searchspace
        seq = str(record.seq).upper()
        # sum function
        sum_vector = Sum(seq, RL)
        # Run Savitzky-Golay
        smooth = SavitzkyGolay(smoothFrame, 0, sum_vector)
        dydx_vector = SavitzkyGolay(smoothFrame, 1, sum_vector)
        # test
        sumHEAD = sum_vector[:smoothFrame]
        sumTAIL = sum_vector[-smoothFrame:]
        newHEAD = []
        newTAIL = []
        for i in range(len(sumHEAD)):
            try:
                dHEAD = (sumHEAD[i + 1] - sumHEAD[i]) / 2
            except:
                dHEAD = (sumHEAD[i] - sumHEAD[i - 1]) / 2
            try:
                dTAIL = (sumTAIL[i + 1] - sumTAIL[i]) / 2
            except:
                dTAIL = (sumTAIL[i] - sumTAIL[i - 1]) / 2
            newHEAD.append(dHEAD)
            newTAIL.append(dTAIL)
        dydx_vector[:smoothFrame] = newHEAD
        dydx_vector[-smoothFrame:] = newTAIL
        globdoms, globdis = getSlices(
            dydx_vector, DOM_joinFrame,
            DOM_peakFrame, DIS_joinFrame, DIS_peakFrame
        )
        s_domMask, coordstrDOM = reportSlicesTXT(globdoms, seq, 'DOM')
        s_final, coordstrDIS = reportSlicesTXT(globdis, s_domMask, 'DIS')
        print('>%s' % record.id)
        print('# %s' % coordstrDOM)
        print('# %s' % coordstrDIS)

        # UNCOMMENT THIS IF NEED TO PRODUCE PER RESEDUE VALUES
        sys.stdout.write('# RESIDUE\tDYDX\tRAW\tSMOOTHED\n')
        for i in range(len(dydx_vector)):
            # dydx (positive values seems to indicate disorder in rows more than ~6 chars)  raw    smoothed
            print('{}\t{:.4f}\t{:.4f}\t{:.4f}'.format(
                seq[i], dydx_vector[i], smooth[i], sum_vector[i]
            ))

        #            print s_final
        print('\n')


run_glob_plot()
