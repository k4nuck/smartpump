#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smartthingscontroller.py
#  
#  Copyright 2023  <pi@raspberrypi>
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

'''''
' Controller from smartthings 
'''

class SmartthingsController:
	
	def __init__ (self,token):
		self.token = token
		self._session = aiohttp.ClientSession()
		
		logging.debug("SmartthingsController:Init:token:"+token)
		
	# Clean up    
	async def __aenter__ (self):
		logging.debug("SmartthingsController:aenter called")
		return self
	async def __aexit__(self, *args, **kwargs):
		logging.debug("smartthingsController:aexit called")
		await self.close()
	async def close(self):
		logging.debug("SmartthingsController:Close Called:"+str(self._session.closed))
		if not self._session.closed:
			await self._session.close()
			
	# Helper function
	def get_smartthings_session(self):
		return self._session
	
	# Helper Function	
	def find_device(devices,label):
		logging.debug("Smarthings:find_device:"+str(len(devices))+" Devices found")
		logging.debug("Smarthings:find_device:label:"+str(label))

		for device in devices:
			logging.debug("Smarthings:find_device:"+device.label+"("+str(device.device_id)+")")
			if(device.label == label):
				return device
			
		return None
	
	# Query State of a smartthings device by name
	async def query_by_name(self,device_name):
		device = None
		token = self.token

		logging.debug("Smartthings_query_by_name:token:"+str(token)+":device name:"+str(device_name))

		async with self.get_smartthings_session() as session:
			api = pysmartthings.SmartThings(session, token)			
			devices = await api.devices()

			device = SmartthingsController.find_device(devices, device_name)

			if (device == None):
				logging.error("smartthings_query_by_name:Device:"+device_name+":NOT FOUND!!!")
				return None
			
			logging.debug("smartthings_query_by_name:smartthings query:"+device_name+":value:"+str(device.status.switch))

		# Error Check
		if (device == None):
			logging.critical("smartthingscontroller_query_by_name:"+":failed to find device:"+device_name)
			return None
		
		return device.status.switch
	
	# Helper Function
	async def set_state(device, value):
		logging.info ("SmartthingsController:Set Device:"+str(device.label) + " to "+str(value))
		
		await device.status.refresh()
		
		logging.info("SmartthingsController:Set Device: Prior Switch: "+str(device.status.switch))
		
		if value:
			logging.info("SmartthingsController:Set Status:ON:"+device.label)
			result = await device.switch_on()
			logging.info("SmartthingsController:Set Device:TRUE:Result: "+ str(result))
		else:
			logging.info("SmartthingsController:Set Status:OFF:"+device.label)
			result = await device.switch_off()
			logging.info ("SmartthingsController:Set Device:FALSE:Result: "+ str(result))

	# Set State of a device by name
	async def set_state_by_name(self, device_name, value):
		token = self.token

		logging.info("SmartthingsController:set_by_name:token:"+str(token)+"device Name:"+device_name+":Value:"+str(value))

		# Get Device and Set it
		async with self.get_smartthings_session() as session:
			api = pysmartthings.SmartThings(session, token)			
			devices = await api.devices()
			device = SmartthingsController.find_device(devices, device_name)

			if (device == None):
				logging.critical("smartthingsController:smartthings_set:device not found:"+":name:"+device_name)
				return
			await SmartthingsController.set_state(device,value)