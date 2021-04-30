#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,os.path
import numpy as np
import math
import time
import json
import codecs
import gdal
from PIL import Image
import logging
import util
from gdalcmd import GdalCMD
import mapHttp

#添加日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler("gisprocess.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler.setFormatter(formatter)
consoleHandle = logging.StreamHandler()
logger.addHandler(fileHandler)
logger.addHandler(consoleHandle)

def tif2png(tiffName, pngName, factor):
  dataset = gdal.Open(tiffName)
  if dataset == None:
    print('无法打开文件')
    return

  imBands = dataset.RasterCount
  im_geotrans = dataset.GetGeoTransform
  im_width = dataset.RasterXSize
  im_height = dataset.RasterYSize
  im_data = dataset.GetRasterBand(1).ReadAsArray(xoff=0, yoff=0)
  zmin = int(np.min(im_data))
  zmax = int(np.max(im_data))

  newImg = Image.new('RGBA', (im_width,im_height))
  for i in range(0, im_data.shape[0]):
    for j in range(0, im_data.shape[1]):
      # color = (0,0,0,0)
      d = im_data[i][j]
      color = util.getColor(d, str(factor))
      # colorIndex = math.floor((d - zmin) / (zmax - zmin) * len(colortabledata))
      # if(colorIndex < len(colortabledata) and d > 0):
      #   colorIndex = len(colortabledata) - 1
      #   color = tuple(colortabledata[colorIndex])

      newImg.putpixel((j,i), color)
  newImg.save(pngName,"PNG")

def createFeature(p, properties):
    geoObj = {}
    geoObj['type'] = 'Point'
    geoObj['coordinates'] = p
    
    ftObj = {}
    ftObj['type'] = 'Feature'
    ftObj['properties'] = properties
    ftObj['geometry'] = geoObj
    return ftObj

# 增加边界点，有用插值图边界校正
def addBoxPoint(box, propertiesTemp):
  p1 = [box[0], box[1]]
  p2 = [box[2], box[1]]
  p3 = [box[2], box[3]]
  p4 = [box[0], box[3]]
  pointList = [p1, p2, p3, p4]

  features = []
  for p in pointList:
    properties = propertiesTemp.copy()
    properties[config['zName']] = 0
    ft = createFeature(p, properties)
    features.append(ft)
  return features

def checkXYValue(xStr, yStr):
  try:
    float(xStr)
    float(yStr)
    return True
  except ValueError:
    pass
  return False

def json2geojson(jsonData, outfile, xKey, yKey, factor, report):
  features = []
  min, max = [0,0]
  for d in jsonData:
    if(checkXYValue(d[xKey], d[yKey])):
      x = float(d[xKey])
      y = float(d[yKey])
      ft = createFeature([x,y], d)
      features.append(ft)

      valueKey = config['zName']
      value = float(d[valueKey])
      max = max if value < max else value
      min = min if value > min else value
  
  
  features = features + addBoxPoint(config['mapExtent'], jsonData[0])

  geojsonObj = {}
  geojsonObj['type'] = 'FeatureCollection'

  report['min'] = str(min)
  report['max'] = str(max)
  report['pointCount'] = len(jsonData)
  logger.debug('factor:%s, min:%s, max:%s'%(factor, str(min), str(max)))

  name = os.path.split(outfile)[1]
  geojsonObj['name'] = name.split('.')[0]
    
  projObj = {}
  projProperties = {'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'}
  projObj = {'type': 'name', 'properties': projProperties}
  geojsonObj['crs'] = projObj

  geojsonObj['features'] = features

  with codecs.open(outfile, 'w', 'utf-8') as geojsonFile:
    jsonstr = json.dumps(geojsonObj)
    geojsonFile.write(jsonstr)
    geojsonFile.close()

def checkPath(path):

  if os.path.exists(path):
    if(os.path.isdir(path)):
      fileList = os.listdir(path)
      for f in fileList:
        os.remove(os.path.join(path, f))
    else:
      os.remove(path)
  else:
    if not os.path.isfile(path):
      os.mkdir(path)

def getSopId(years):
  sopIds = []
  for year in years:
    postResult = mapHttp.getSopListInfo(year)
    if(postResult.code == 200):
      ids = []
      for item in postResult.data:
        sopIds.append(item['inventoryId'])
  return sopIds

def main(conf):
  '''
  '''
  global config
  config = conf
  idList = getSopId(config['sopList'])
  if(len(idList) == 0):
    logger.warning('未获取到污染源清单，任务退出,下一周期会重新执行....')
    return

  checkPath(config['tempFilePath'])
  checkPath(config['outFilePath'])

  convert = GdalCMD()
  
  for sopItemId in idList:
    for factor in config['factors']:
      try:
        # 用于记录生成图片的数据参数
        mapInfo = {}
        mapInfo['sopId'] = str(sopItemId)
        mapInfo['factor'] = str(factor)
        mapInfo['extent'] = config['mapExtent']
        

        logger.info('生成参数：清单：' + str(sopItemId) + '，因子：' + str(factor))
        result = mapHttp.getSopPoints(sopItemId, factor)
        if(result.code == 0):
          logger.error('获取清单数据失败....')
          continue
        name = str(sopItemId) + '_' + str(factor)
        geojsonName = os.path.join(config['tempFilePath'], name + '.geojson')
        json2geojson(result.data, geojsonName, config['xName'], config['yName'], factor, mapInfo)

        tiffName = geojsonName.replace('.geojson', '.tiff')
        mapExtent = config['mapExtent']
        r = convert.interpolation(geojsonName, tiffName, config['zName'], mapExtent)
        if(r != 0):
          logger.error('插值命令错误，程序退出')
          continue

        clipName = tiffName.replace(name, name + '_clip')
        r = convert.warp(tiffName, clipName, config['clipFile'])
        if(r != 0):
          logger.error('裁剪命令错误，程序退出')
          continue
        
        pngName = os.path.join(config['outFilePath'], name + '.png')
        tif2png(clipName, pngName, factor)
        
        infoName = os.path.join(config['outFilePath'], name + '.json')
        mapInfo['createTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(infoName, 'w') as infoFile:
          infoStr = json.dumps(mapInfo)
          infoFile.write(infoStr)
          infoFile.close()

        logger.info('done.....')
      except Exception as e:
        logger.error(e.message)
        logger.error(e.args)
  logger.info('task done....')


if __name__ == '__main__':
  configFile = r'./config.json'
  config = json.load(open(configFile))
  main(config)