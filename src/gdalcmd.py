#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,os.path
import subprocess as sp

class GdalCMD:
  def __init__(self):
    self.interpolationexe = r'tools\gdal_grid.exe'
    self.warpexe = r'tools\gdalwarp.exe'
    
  def interpolation(self, inputFile, outFile, zFieldName, extent):
    '''
    插值
    '''
    layerName = os.path.split(inputFile)[1].split('.')[0]
    headParams = self.interpolationexe
    interparams = '-a invdist:power=2.0:smothing=0.0:radius1=0.0:radius2=0.0:angle=0.0:max_points=0:min_points=0:nodata=0.0'
    boundParams = '-spat ' + ' '.join([str(v) for v in extent])
    typeParams = '-ot Float32'
    layerNameParams = '-l ' + layerName
    zFieldParams = '-zfield ' + zFieldName

    params = [headParams, interparams, boundParams, typeParams, layerNameParams, zFieldParams, inputFile, outFile]
    return self.run(params)
  
  def warp(self, inputFile, outFile, clipLayer):
    '裁剪'
    headParams = self.warpexe
    typeParams = '-ot Float32'
    formatParams = '-of GTiff'
    cutParams = '-cutline ' + clipLayer
    cropParams = '-crop_to_cutline'

    params = [headParams, typeParams, formatParams, cutParams, cropParams, inputFile, outFile]
    return self.run(params)

  def run(self, params):
    try:
      cmd = ' '.join(params)
      print(cmd)
      subProc = sp.Popen(cmd, shell=True)
      subProc.wait()
      return subProc.returncode
    except Exception as e:
      print(e)
      print('task run failed!')
      return 9000

def csv2vrt(csv, lngFiled, latField):
  path,name = os.path.split(csv)
  name = name.split('.')[0]
  vrtname = os.path.join(path, name + '.vrt')
  with open(vrtname, 'w') as vf:
    ft = '<OGRVRTDataSource>\n' + \
      '<OGRVRTLayer name="{layerName}">\n' +\
        '<SrcDataSource>{layerName}.csv</SrcDataSource>\n' + \
        '<GeometryType>wkbPoint</GeometryType>\n' + \
        '<GeometryField encoding="PointFromColumns" x="{x}" y="{y}"/>\n' + \
      '</OGRVRTLayer>\n'+\
    '</OGRVRTDataSource>'
    ft = ft.replace('{layerName}', name)
    ft = ft.replace('{x}', lngFiled)
    ft = ft.replace('{y}', latField)
    vf.write(ft)
    vf.close
  return vrtname


def testInterpolation():
  p = r'.\data\sop.geojson'
  outFile = os.path.splitext(p)[0] + '.tiff'
  print(os.getcwd())
  convert = GdalCMD()
  code = convert.interpolation(p, outFile,'pfl')
  print(code)

def testWarp():
  p = r'.\data\sop.tiff'
  outFile = p.replace('sop', 'sop_clip')
  clipFile = r'.\data\sc.geojson'
  print(os.getcwd())
  convert = GdalCMD()
  code = convert.warp(p, outFile, clipFile)
  print(code)

if __name__ == '__main__':
  # testInterpolation()
  testWarp()