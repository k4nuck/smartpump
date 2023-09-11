#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hacontroller.py
#  
#  Copyright 2023 
#  Joseph Bersito
#  
#  Wrapper around homeassitant_api
#

import os
import sys
import logging
import time

from homeassistant_api import Client

'''''
' Controller for homeassistant 
'''

class HomeAssistantController:
    # Initialization
    def __init__ (self,token, api_url):
        self.token = token
        self.api_url = api_url

        logging.debug("ha_controller_init:token:"+self.token)
        logging.debug("ha_controller_init:url:"+self.api_url)

    # Helper function.  Return entity name from device type and name
    def form_entity_name(device_type, device_name):
        return str(device_type+"."+device_name)
    
    # Query device state by type and name
    def query_state_by_name(self,device_type, device_name):

        logging.debug("ha_controller:get_state_by_name:type:"+device_type+":name:"+device_name)

        # Create Client
        # From experimenting ... needed to create client everytime to get the latest state from 
        # Home Automation Server
        client = Client(self.api_url, self.token)

        # Get Device
        entity = HomeAssistantController.form_entity_name(device_type,device_name)

        logging.debug("ha_controller:query_state_by_name:entity:"+str(entity))

        device = client.get_entity(entity_id=entity)

        if device == None:
            logging.critical("query_state_by_name:failed to find device:"+str(entity))
            return None
        
        state = device.get_state().state
        if device == None:
            logging.critical("query_state_by_name:failed to get state:"+str(entity))
            return None
    
        # Return Bool
        logging.debug("ha_controller:query_state_by_name:state:"+state)

        if (state=="on"):
            return True
        else:
            return False
    
    # Set State of device by type and name
    def set_state_by_name(self, device_type, device_name, value):

        logging.debug("ha_controller:set_state_by_name:type:"+device_type+":name:"+device_name+":value:"+str(value))

        # Create Client
        # From experimenting ... needed to create client everytime to get the latest state from 
        # Home Automation Server
        client = Client(self.api_url, self.token)

        # Get Domain
        domain = client.get_domain(device_type)

        if domain == None:
            logging.critical("ha_controller:set_state_by_name:failed to find domain:"+str(device_type))
            return 

        # Set State
        entity = HomeAssistantController.form_entity_name(device_type,device_name)

        logging.debug("ha_controller:set_state_by_name:entity:"+str(entity))

        if (value):
            # Set Real Device State
            logging.debug("ha_controller:set_state_by_name:ON")
            resp = domain.turn_on(entity_id=entity)
            logging.debug("ha_controller:set_state_by_name:resp:"+str(resp))
        else:
            # Set Real Device State
            logging.debug("ha_controller:set_state_by_name:OFF")
            resp = domain.turn_off(entity_id=entity)
            logging.debug("ha_controller:set_state_by_name:resp:"+str(resp))
