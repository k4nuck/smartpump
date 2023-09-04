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

		# Initialize smartthings Session
		# asyncio.run(self.init_smartthings())

	# Helper Function	
	def findDevice(devices,label):
		logging.debug("Smarthings:FindDevice:"+str(len(devices))+" Devices found")
		logging.debug("Smarthings:FindDevice:label:"+str(label))

		for device in devices:
			logging.debug("Smarthings:FindDevice:"+device.label+"("+str(device.device_id)+")")
			if(device.label == label):
				return device
			
		return None

	# Helper function
	def get_smartthings_session(self):
		return self.Smartthings_session

	# Return pysmartthings device
	async def smartthings_find_device_by_name(self, device_name):
		device = None
		token = self.smartthings_token

		logging.info("Smartthings_find_by_name:token:"+str(token)+":device name:"+str(device_name))

		# Getting Smartthings Object
		# session = self.get_smartthings_session() - JB

		async with aiohttp.ClientSession() as session:
			api = pysmartthings.SmartThings(session, token)			
			devices = await api.devices()

		deviceName = device_name
		device = SmartController.findDevice(devices, deviceName)

		if (device == None):
			logging.error("smartthings_find_device_by_name:Device:"+deviceName+":NOT FOUND!!!")
			return None
			
		logging.info("smartthings_find_device_by_name:smartthings query:"+device_name+":value:"+str(device.status.switch))

		return device 

	# Helper Function
	async def setDeviceStatus(device, value):
		logging.info ("Smartthings:Set Device:"+str(device.label) + " to "+str(value))
		
		await device.status.refresh()
		
		logging.info("Smartthings:Set Device: Prior Switch: "+str(device.status.switch))
		
		if value:
			logging.info("smartthings Set Statud:ON:"+device.label)
			result = await device.switch_on()
			logging.info("Smartthings:Set Device:TRUE:Result: "+ str(result))
		else:
			logging.info("smartthings Set Statud:OFF:"+device.label)
			result = await device.switch_off()
			logging.info ("Smartthings:Set Device:TRUE:Result: "+ str(result))
	
	# Init Smartthings Session
	async def init_smartthings(self):
		self.Smartthings_session=aiohttp.ClientSession()
		logging.info("init_smartthings:session:"+str(self.get_smartthings_session()))

	#Smartthings Query
	#Device Typr doesnt matter at this time for Smartthings
	async def smartthings_query(self, device_type, device_name):
		data = {"type":device_type, "name":device_name, "state":False}
		
		# Make Query
		logging.info("smarthhings query:type:"+ device_type+":name:"+device_name)

		device = await self.smartthings_find_device_by_name(device_name)

		# Error Check
		if (device == None):
			logging.info("smartthings_query:"+":failed to find device:"+device_name)
			return data

		data["state"] = device.status.switch

		return data
	
	#Smartthings Set
	async def smartthings_set(self, device_type, device_name, cmd):
		
		# Make update
		token = self.smartthings_token

		logging.info("smartthings_set:device type:"+device_type+":device name:"+device_name+":cmd:"+str(cmd))

		async with aiohttp.ClientSession() as session:
			api = pysmartthings.SmartThings(session, token)			
			devices = await api.devices()

			deviceName = device_name
			device = SmartController.findDevice(devices, deviceName)

			#JB - device = await self.smartthings_find_device_by_name(device_name)

			if (device == None):
				logging.info("smartthings_set:device not found:"+":name:"+device_name)
				return
		
			if (cmd == "on"):
				logging.info("smartthings_set:ON:"+device.label)
				await SmartController.setDeviceStatus(device,True)
			else:
				logging.info("smartthings_set:OFF:"+device.label)
				await SmartController.setDeviceStatus(device,False)
		
		return
		
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


