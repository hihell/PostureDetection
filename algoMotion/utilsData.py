from __future__ import division
from algoMotion import featureGenerator as fg

__author__ = 'jiusi'

import json
import parameters as param
import numpy as np


def getStatusByCode(code):
    for status, c in param.STAT_DICT.iteritems():
        if c == code:
            return status
    print 'did not find status by code:', code
    return None

def getL1ByL2(l2List):
    l1List = []
    for l2 in l2List:
        l1List.append(param.STAT_CLASS_MAP[l2])
    return l1List

def getDataBySensorType(datatype, list):
    if 'sensorName' in list[0]:
        key = 'sensorName'
        aList = [ele for ele in list if ele[key] == 'acc']
        linList = [ele for ele in list if ele[key] == 'linacc']
        gList = [ele for ele in list if ele[key] == 'gyro']
    elif 'source' in list[0]:
        key = 'source'
        aList = [ele for ele in list if ele[key] == 'accelerometer']
        # old log does not have fused linear acceleration
        gList = [ele for ele in list if ele[key] == 'Gyroscope']
    else:
        print 'wrong data src format, no sensorName or source in it'
        return None

    if(datatype == 'accelerometer'):
        return aList
    elif(datatype == 'linacc'):
        return linList
    elif(datatype == 'gyro'):
        return gList
    else:
        print 'wrong data type:', datatype, ' must be either accelerometer, linacc or gyro'
        return None

def readFile(filePath, isOld=False):
    with open(filePath) as f:
        jlist = [line.rstrip() for line in f]
        dataList = [json.loads(j) for j in jlist]
        if isOld:
            return dataList[0]
        else:
            return dataList

def readFiles(filePaths):
    dataList = []

    for path in filePaths:
        print path
        dataList.append(readFile(path))

    return dataList

def splitDataListBySampleGranularity(granularity, dataList):
    return [dataList[i:i+granularity] for i in range(0, len(dataList), granularity)]

def splitDataListByStatus(dataList):
    buckets = {}
    for data in dataList:
        status = data['status']
        if status in buckets:
            buckets[status].append(data)
        else:
            buckets[status] = [data]

    return [buckets[key] for key in buckets]


def assignL2ClassToBucket(buckets):
    y = []
    for bucket in buckets:
        data = bucket[0]
        if 'status' in data:
            status = data['status']
            y.append(param.STAT_DICT[status])
        else:
            return None
    return y

def assignL1ClassToBucket(buckets):
    y = []
    for buckets in buckets:
        data = buckets[0]
        if 'status' in data:
            status = data['status']
            l1 = param.STAT_DICT[status]
            l2 = param.STAT_CLASS_MAP[l1]
            y.append(l2)
        else:
            return None
    return y

def processFile(filePath, granularity):
    dataList = readFile(filePath)

    accList = getDataBySensorType('accelerometer', dataList)

    print getDataListStatus(accList)

    print 'len datalist:', len(dataList), ' len acclist:', len(accList)

    buckets = splitDataListByStatus(accList)

    slices = []
    for bucket in buckets:
        list = splitDataListBySampleGranularity(granularity, bucket)
        slices.extend(list)

    y2 = assignL2ClassToBucket(slices)
    y1 = assignL1ClassToBucket(slices)

    return slices, y2, y1

def processRawData(data, granularity):
    accList = getDataBySensorType('accelerometer', data)

    print getDataListStatus(accList)
    print 'len datalist:', len(data), ' len accList:', len(accList)

    buckets = splitDataListBySampleGranularity(granularity, accList)
    y2 = assignL2ClassToBucket(buckets)
    return buckets, y2




def printDataLabels(filePath):
    statusCounter = {}
    dataList = readFile(filePath)
    for dt in dataList:
        status = dt['status']
        if status in statusCounter:
            statusCounter[status] += 1
        else:
            statusCounter[status] = 1
    print statusCounter

def getFileStatus(filePath):
    dataList = readFile(filePath)
    return getDataListStatus(dataList)


def getDataListStatus(dataList):

    for data in dataList:
        if not 'status' in data:
            return 'no status in dataList'

    message = ''
    dataList = getDataBySensorType('accelerometer', dataList)

    previousStatus = dataList[0]['status']

    message += (previousStatus + ' starts at:' + str(0))

    for i, dt in enumerate(dataList):
        status = dt['status']
        if status != previousStatus:
            message += str(' ends at:' + str(i-1))
            message += str('|' + status + ' starts at:' + str(i))
            previousStatus = status

    message += str(' ends at:' + str(len(dataList)))

    return message

def getCorrectRate(trueTags, pred):
    count = 0
    for trueTag, p in zip(trueTags, pred):
        if trueTag == p:
            count += 1
    return count / len(trueTags)
