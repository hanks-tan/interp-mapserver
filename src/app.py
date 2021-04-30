#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from flask_cors import CORS
from flask import Flask, send_from_directory,request

configFile = r'./config.json'
config = json.load(open(configFile))

app = Flask(__name__)


@app.route('/')
def hello_world():
  return 'Hello World!This is Flask!' + os.getcwd()

@app.route('/flask')
def flask():
  return 'this is flask!'

@app.route('/sopgrid', methods=["GET"])
def getSopGrid():
  if request.method == "GET":
    inventoryId = request.args['inventoryId']
    factor = request.args['factor']
    fileName = os.path.join(config['outFilePath'], inventoryId + '_' + factor + '.png')
    if os.path.exists(fileName):
      static = os.path.split(config['outFilePath'])[1]
      name = inventoryId + '_' + factor + '.png'
      return send_from_directory(static, name)

@app.route('/sopgridinfo', methods=["GET"])
def getSopGridInfo():
  if request.method == "GET":
    inventoryId = request.args['inventoryId']
    factor = request.args['factor']
    fileName = os.path.join(config['outFilePath'], inventoryId + '_' + factor + '.json')
    if os.path.exists(fileName):
      static = os.path.split(config['outFilePath'])[1]
      name = inventoryId + '_' + factor + '.json'
      return send_from_directory(static, name)
    

if __name__ == '__main__':
  CORS(app, supports_credentials=True)
  app.run()