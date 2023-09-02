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
	
		
	#Smartthings Query
	def smartthings_query(self, device_type, device_name):
		data = {"type":device_type, "name":device_name, "state":False}
		
		#JB - Make Query
		
		
		return data
	
	#Smartthings Set
	def smartthings_set(self, device_type, device_name, cmd):
		
		#JB - Make update

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
				return self.smartthings_query(device_type, device_name)
			except:
				logging.critical("Smart Controller Query: Smartthings:Failed")
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
			try:
				req = self.smartthings_set(device_type,device_name, cmd])
			except:
				logging.critical("Smart Controller Set:Failed to Set the device")
				return None
					
			return req
		else:
			logging.warning( "SmartController:Set:UNKNOWN Controller: "+controller)
			return None


