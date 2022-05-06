
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
import json
import time

logger = logging.getLogger(__name__)


class TasmotaMQTTExtension(CBPiExtension):

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.app.on_cleanup.append(self.stop_task)
        self._task = asyncio.create_task(self.init_sensor())
    
    async def init_sensor(self):
        global cache
        cache = {}
        await self.TasmotaConfig()
        if self.TasmotaTopic is not None:
            self.mqtt_task = self.cbpi.satellite.subcribe(self.TasmotaTopic, self.on_message)

    async def on_message(self, message):
        global cache
        cache = json.loads(message)
        cache["Time"]=time.time()
        
    async def TasmotaConfig(self):
        self.TasmotaTopic = self.cbpi.config.get("TasmotaTopic", None)
        if self.TasmotaTopic is None:
            logger.info("INIT TasmotaTopic")
            try:
                await self.cbpi.config.add("TasmotaTopic", "", ConfigType.STRING, "Tasmota MQTT Topic")
                self.TasmotaTopic = self.cbpi.config.get("TasmotaTopic", None)
            except:
                logger.warning('Unable to update database')

    async def stop_task(self):
        if self.mqtt_task.done() is False:
            self.mqtt_task.cancel()
            try:
                await self.mqtt_task
            except asyncio.CancelledError:
                pass


@parameters([Property.Text("Payload", description="Select Tasmota Sensor # to register for this sensor.")])
class TasmotaSensor(CBPiSensor):
    
    def __init__(self, cbpi, id, props):
        super(TasmotaSensor, self).__init__(cbpi, id, props)
        self.value = 0
        self.old_time=0.0
        self.payload_text=self.props.get("Payload", None)
        if self.payload_text != None:
            self.payload_text = self.payload_text.split('.')


    async def run(self):
        current_time=0.0
        while self.running is True:
            try:
                current_time=float(cache.get("Time"))
            except:
                pass
            if current_time > self.old_time:
                self.old_time = current_time
                val=cache
                try:
                    if self.payload_text is not None:
                        for key in self.payload_text:
                            val = val.get(key, None)

                    if isinstance(val, (int, float, str)):
                        self.value = float(val)
                        self.log_data(self.value)
                        self.push_update(self.value)
                except Exception as e:
                    logging.info("Tasmota MQTT Sensor Error {}".format(e))

            await asyncio.sleep(1)
    
    def get_state(self):
        return dict(value=self.value)


def setup(cbpi):
    cbpi.plugin.register("TasmotaSensor", TasmotaSensor)
    cbpi.plugin.register("TasmotaMQTTExtension", TasmotaMQTTExtension)
    pass
