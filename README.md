这是个根据地图散点生成插值图的程序，并提供接口服务来获取插值后的结果一

这是一个服务，主要完成以下功能：

1、从外部接口获取带经纬度的散点数据。

2、根据散点数据利用插值法，生成插值图。

3、生成的图片会根据给定范围进行裁剪。

4、会定时去执行上面的操作，定时生成图片。

5、对外提供一个服务接口，用于获取插值后的图片。

# 部署说明
1、gdal

2、参数配置
  详情见config.json
  1) 临时输入输出目录


