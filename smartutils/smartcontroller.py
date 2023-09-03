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

from pyharmony import client as harmony_client

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

		
		# Get Config Data for Harmony Hub
		with open("/home/k4nuck/.harmony_settings.json") as harmony_object:
			harmony_data = json.load(harmony_object)
			self.harmony_ip = harmony_data["ip"]
			self.harmony_port = harmony_data["port"]
			logging.debug("Harmony Config - ip:"+self.harmony_ip+" - port:"+self.harmony_port)
	
	# Helper Function	
	def findDevice(devices,label):
		logging.debug("Smarthings:FindDevice:"+str(len(devices))+" Devices found")
		logging.debug("Smarthings:FindDevice:label:"+str(label))

		
		for device in devices:
			logging.debug("Smarthings:FindDevice:"+device.label+"("+str(device.device_id)+")")
			if(device.label == label):
				return device
			
		return None

	#Helper function
	# Return pysmartthings object
	async def smartthings_find_device_by_name(self, device_name):
		device = None
		token = self.smartthings_token

		logging.info("Smartthings_find_by_name:token:"+str(token)+":device name:"+str(device_name))

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
	
	#Smartthings Query
	#Device Typr doesnt matter at this time for Smartthings
	async def smartthings_query(self, device_type, device_name):
		data = {"type":device_type, "name":device_name, "state":False}
		
		token = self.smartthings_token

		logging.info("Smartthings_query:token:"+str(token)+":device name:"+device_name)
		
		# Make Query
		logging.info("smarthhings query:type:"+ device_type+":name:"+device_name+":token:"+token)

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

		logging.info("smartthings_set:device type:"+device_type+":device name:"+device_name+":cmd:"+str(cmd))

		device = await self.smartthings_find_device_by_name(device_name)

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


	# Query Harmony Devices
	def harmony_query(self, device_type, device_name):
		data = {"type":device_type, "name":device_name, "state":False}
		
		#This IP and PORT from config
		ip = self.harmony_ip
		port = self.harmony_port
		activity_callback=None
		client = harmony_client.create_and_connect_client(ip, port, activity_callback)
	
		config = client.get_config()
		current_activity_id = client.get_current_activity()
		
		client.disconnect(send_close=True)
		
		activity = [x for x in config['activity'] if int(x['id']) == current_activity_id][0]
		
		if activity['label'] == "PowerOff":
			data["state"] = False
		else:
			data["state"] = True
		
		return data	
		
	# Public Accessor to query any type of device
	def query(self, controller, device_type, device_name):
		if controller == "SAMSUNG":
			try:
				return asyncio.run(self.smartthings_query(device_type, device_name))
			except Exception as X:
				logging.critical("Smart Controller Query: Smartthings:Failed:"+str(X))
				return {"type":"None", "name":"None", "state":False}
				
		if controller == "HARMONY":
			try:
				return self.harmony_query(device_type,device_name)
			except:
				logging.critical("Smart Controller Query: Harmony:Failed")
				return {"type":"None", "name":"None", "state":False}
		else:
			logging.warning( "SmartController:Query:UNKNOWN Controller: "+controller)
			return None
			
	# Public Accessor to set value for any device type
	def set(self, controller, device_type, device_name, cmd):
		#JB - Support Set for HARMONY Devices
		if controller == "SAMSUNG":
			#return asyncio.run(self.smartthings_set(device_type,device_name, cmd))
			try:
				req = asyncio.run(self.smartthings_set(device_type,device_name, cmd))
			except Exception as X:
				logging.critical("Smart Controller Set:Failed to Set the device:"+str(X))
				return None
					
		else:
			logging.warning( "SmartController:Set:UNKNOWN Controller: "+controller)
			return None


