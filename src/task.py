import json
import gis

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

configFile = r'./config.json'
config = json.load(open(configFile))

def job():
  gis.main(config)

def task():
  scheduler = BlockingScheduler()
  if('intervalTime'in config.keys()):
    interval = config['intervalTime']
  else:
    interval = ['00', '00', '00']
    
  # 每日定时执行
  scheduler.add_job(job, "cron", day_of_week='*', hour=interval[0], minute=interval[1], second=interval[2])
  scheduler.start()

if __name__ == "__main__":
    print('这是个定时任务，用于生成污染源渲染图')
    task()

