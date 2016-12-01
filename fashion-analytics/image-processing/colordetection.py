from __future__ import division
from PIL import Image
import os
from operator import itemgetter
import shutil
import numpy as np

from collections import Counter
from joblib import Parallel, delayed

num_parallel_loop = 1
spacing = 8
unifColDict = {}
for r in range(0, 257, spacing):
    for g in range(0, 257, spacing):
        for b in range(0, 257, spacing):
            unifColDict[(r, g, b)] = [r, g, b]

colNeighbors = {}
for value in unifColDict.keys():
    neighbors = []
    for rsteps in [value[0] - spacing, value[0], value[0] + spacing]:
        for gsteps in [value[1] - spacing, value[1], value[1] + spacing]:
            for bsteps in [value[2] - spacing, value[2], value[2] + spacing]:
                if (
                                                rsteps > -1 and rsteps < 257 and gsteps > -1 and gsteps < 257 and bsteps > -1 and bsteps < 257):
                    if not (value == (rsteps, gsteps, bsteps)):
                        neighbors.append([rsteps, gsteps, bsteps])
    colNeighbors[value] = neighbors


def findPeaks(c, colNeighbors):
    peaks = {}
    for presentCols in c.keys():
        presentNeighbors = {tuple(colors): c[tuple(colors)] for colors in
                            colNeighbors[presentCols] if
                            tuple(colors) in c.keys()}
        if len(presentNeighbors) > 0:
            if c[presentCols] >= max(presentNeighbors.values()):
                if c[presentCols] > 15:
                    peaks[presentCols] = c[presentCols]
        else:
            if c[presentCols] > 15:
                peaks[presentCols] = c[presentCols]
    return peaks


def distWhite(a, b):
    maxDist = 0
    for a_i, a_values in enumerate(a):
        maxDist = max(maxDist, abs(b[a_i] - a_values))
    return maxDist


def topColors(my_item_id):
    '''Create a collage of the dominant colors.

    Take an item id, and with all its pictures make a
    collage of the dominant colors. The first one is the
    background. The collage is saved as 'colors.png'.
    Also return them as a list.

    :param my_item_id: the id of the item
    :return: list of dominant colors
    '''
    src_folder = './sample_img'

    count = 0
    dest = './'
    file_name = str(my_item_id) + '_' + str(count) + '.jpeg'
    full_file_name = os.path.join(src_folder, file_name)
    peaks_combined = {}
    print(full_file_name)
    global_assignment = []

    while os.path.isfile(full_file_name):
        print(count)
        img = Image.open(full_file_name)
        img.thumbnail((200, 200))
        color_list = list(img.getdata())

        W, H = img.size
        data = np.zeros((len(color_list), 3))
        for i in range(len(color_list)):
            color = color_list[i]
            data[i, :] = color

        # Assign points given centers
        assignment = list(np.zeros((data.shape[0],)))

        range_list = []
        for i in range(num_parallel_loop):
            range_list.append(
                np.arange(int(i * data.shape[0] / num_parallel_loop),
                          int((i + 1) * data.shape[0] / num_parallel_loop)))
        data_list = []
        for i in range(num_parallel_loop):
            data_list.append(data[range_list[i], :])

        findCloseResult = Parallel(n_jobs=num_parallel_loop)(
            delayed(findCloseCorner)(data_list[i], spacing, unifColDict) for i
            in range(num_parallel_loop))
        count_i = 0
        for i in range(num_parallel_loop):
            temp = findCloseResult[i]
            for values in temp:
                assignment[count_i] = values
                count_i = count_i + 1
        global_assignment.extend(assignment)

        count += 1
        file_name = str(my_item_id) + '_' + str(count) + '.jpeg'
        full_file_name = os.path.join(src_folder, file_name)

        #try:
        #    shutil.copy(full_file_name, dest)
        #except:
        #    print("File not found")
        #print(full_file_name)


    c = Counter(global_assignment)

    peaks = findPeaks(c, colNeighbors)

    sorted_peaks = sorted(peaks, key=peaks.__getitem__, reverse=True)
    total_peaks = len(peaks)
    numcol = min(total_peaks, 4)
    numrow = (total_peaks - 1) // 4 + 1
    imgSize = 80
    collager = np.zeros((numrow * imgSize, numcol * imgSize))
    collageg = np.zeros((numrow * imgSize, numcol * imgSize))
    collageb = np.zeros((numrow * imgSize, numcol * imgSize))

    img = np.ones((imgSize, imgSize))
    for iii, peak in enumerate(sorted_peaks):
        peak = list(peak)
        for hh in range(len(peak)):
            if peak[hh] == 256:
                peak[hh] = 255
        arrr = (np.ones((imgSize, imgSize)) * peak[0]).astype('uint8')
        arrg = (np.ones((imgSize, imgSize)) * peak[1]).astype('uint8')
        arrb = (np.ones((imgSize, imgSize)) * peak[2]).astype('uint8')
        print(arrr.shape)
        rowIndex = iii // 4
        colIndex = iii % 4
        collager[(rowIndex * imgSize):((rowIndex + 1) * imgSize),
        (colIndex * imgSize):((colIndex + 1) * imgSize)] = arrr
        collageg[(rowIndex * imgSize):((rowIndex + 1) * imgSize),
        (colIndex * imgSize):((colIndex + 1) * imgSize)] = arrg
        collageb[(rowIndex * imgSize):((rowIndex + 1) * imgSize),
        (colIndex * imgSize):((colIndex + 1) * imgSize)] = arrb
    imr = Image.fromarray(collager.astype('uint8'))
    img = Image.fromarray(collageg.astype('uint8'))
    imb = Image.fromarray(collageb.astype('uint8'))
    collagergb = Image.merge('RGB', (imr, img, imb))  # color image
    collagergb.save("colors.png", "PNG")
    return sorted(peaks.items(), key=itemgetter(1), reverse=True)


def findCloseCorner(colors, spacing, unifColDict):
    result = []
    for ff in range(colors.shape[0]):
        color = colors[ff, :]
        dist = {}
        cornerElements = []
        rcoord = [int((color[0] // spacing) * spacing),
                  int((color[0] // spacing + 1) * spacing)]
        gcoord = [int((color[1] // spacing) * spacing),
                  int((color[1] // spacing + 1) * spacing)]
        bcoord = [int((color[2] // spacing) * spacing),
                  int((color[2] // spacing + 1) * spacing)]
        for ii in rcoord:
            for jj in gcoord:
                for kk in bcoord:
                    cornerElements.append((ii, jj, kk))
        for corner in cornerElements:
            dist[corner] = np.sqrt(np.sum((unifColDict[
                                               corner] - color) ** 2))  # delta94(rgb2Lab(unifColDict[corner]), rgb2Lab(data[i,:]))#
        result.append(min(dist, key=dist.get))
    return result
