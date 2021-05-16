import asyncio
import json
import traceback

from gmqtt import Client as MQTTClient
from gmqtt.mqtt.constants import MQTTv311


class MQTTPublisher:
    def __init__(self, host, port, username, password, queue):
        self._client = MQTTClient("call_watcher")
        self._client.set_auth_credentials(username, password)
        self._host = host
        self._port = port
        self._queue = queue

        self._connected = False

    async def run(self):
        while True:
            try:
                msg = await self._queue.get()
                await self._connect()

                self._client.publish(
                    f"call_watcher/{msg['type']}",
                    json.dumps(
                        {
                            "count": len(msg["apps"]),
                            "apps": msg["apps"],
                        }
                    ),
                    qos=1,
                )
            except Exception as err:
                traceback.print_tb(err.__traceback__)
                self._connected = False
                await asyncio.sleep(5)

    async def _connect(self):
        if self._connected:
            return

        await self._client.connect(
            self._host, port=self._port, ssl=True, version=MQTTv311
        )
        self._connected = True
