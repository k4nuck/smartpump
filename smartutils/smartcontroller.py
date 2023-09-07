#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smartcontroller.py
#  
#  Copyright 2018  <pi@raspberrypi>
#  Joseph Bersito
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
# 

import os
import sys
import logging
import time

import asyncio
import aiohttp
import pysmartthings
import json

from smartutils.smarthingscontroller import *

'''
' Generic Interface for Smart Devices
' Current support:
'      Samsung Smartthings
' Format of return
'      {"type":"<DEVICE TYPE>", "name":"<DEVICE NAME>", "state":<BOOL>}
'''
class SmartController:
	
	def __init__ (self):
		#Get Config Data for Smartthings
		with open("/home/k4nuck/.smartthings_settings.json") as smartthings_object:
			snartthings_data = json.load(smartthings_object)
			self.smartthings_token = snartthings_data["token"]
			logging.debug("Smartthings Config - token:"+self.smartthings_token)

	'''
	'Smartthings Query
	'Device Type doesnt matter at this time for Smartthings
	'''
	async def smartthings_query(self, device_type, device_name):
		data = {"type":device_type, "name":device_name, "state":False}
		
		# Make Query
		logging.debug("smarthhings query:type:"+ device_type+":name:"+device_name)

		async with SmartthingsController(self.smartthings_token) as controller:
			state = await controller.query_by_name(device_name)

			if state == None:
				logging.critical("smartthings_query:State Not Found:"+device_name)
				
			logging.debug("smartthings_query:state:"+str(state))
			data["state"] = state

		return data
	
	
	#Smartthings Set
	async def smartthings_set(self, device_type, device_name, cmd):
		# Make update
		logging.info("smartthings_set:device type:"+device_type+":device name:"+device_name+":cmd:"+str(cmd))

		async with SmartthingsController(self.smartthings_token) as controller:
			if cmd == "on":
				logging.info("smartthings_set:True")
				await controller.set_state_by_name(device_name,True)
			else:
				logging.info("smartthings_set:False")
				await controller.set_state_by_name(device_name,False)
		
	# Public Accessor to query any type of device
	def query(self, controller, device_type, device_name):
		if controller == "SAMSUNG":
			try:
				return asyncio.run(self.smartthings_query(device_type, device_name))
			except Exception as X:
				logging.critical("Smart Controller Query: Smartthings:Failed:"+str(X))
				return {"type":"None", "name":"None", "state":False}
		else:
			logging.warning( "SmartController:Query:UNKNOWN Controller: "+controller)
			return None
			
	# Public Accessor to set value for any device type
	def set(self, controller, device_type, device_name, cmd):
		if controller == "SAMSUNG":
			try:
				req = asyncio.run(self.smartthings_set(device_type,device_name, cmd))
			except Exception as X:
				logging.critical("Smart Controller Set:Failed to Set the device:"+str(X))
				return None
					
		else:
			logging.warning( "SmartController:Set:UNKNOWN Controller: "+controller)
			return None


