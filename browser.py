from threading import Thread
from time import time
import grpc
import robot_pb2, robot_pb2_grpc
import asyncio
import json
from logging import DEBUG
import os
import aiortc
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling, TcpSocketSignaling
from aiortc.contrib.media import MediaPlayer, MediaRelay
from loguru import logger
from aiohttp import web
from aiortc.rtcrtpsender import RTCRtpSender
import platform

ROOT = os.path.dirname(__file__)

class NotifierServicer(notifier_pb2_grpc.NotifierServicer):
    def __init__(self) -> None:
        super().__init__()
        self.web_thread = Thread(target=self.webserver)
        self.web_thread.start()
        self.notifications_queue = asyncio.Queue()
        self.notifier_channel = None

    def SetStatusBox(self, request, context):
        if self.notifier_channel is not None:
            self.notifications_queue.put_nowait(json.dumps({
                "id": request.Id,
                "value": request.Value
            }))
            return notifier_pb2.Status2(Ok=True, Timestamp=time())
        return notifier_pb2.Status2(Ok=False, Timestamp=time())

    def webserver(self):
        try:
            self.run_webserver()
        except Exception as err:
            logger.error(err)
            exit(1)

    def run_webserver(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        channel = grpc.insecure_channel('localhost:50051')
        robot_stub = robot_pb2_grpc.RobotStub(channel)

        last_ping_time = 0
        stopped = True
        watchdog_running = False
        with open(os.path.join(ROOT, 'cameras.json'), 'r', encoding='utf-8') as file:
            cameras = json.loads(file.read())

        system = platform.system()

        camera_config = cameras[system]['config']

        pcs: set[aiortc.RTCPeerConnection] = set()
        async def index(request):
            content = open(os.path.join(ROOT, "rtc_user.html"), "r").read()
            return web.Response(content_type="text/html", text=content)

        def force_codec(pc, sender, forced_codec):
            kind = forced_codec.split("/")[0]
            codecs = RTCRtpSender.getCapabilities(kind).codecs
            transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
            transceiver.setCodecPreferences(
                [codec for codec in codecs if codec.mimeType == forced_codec]
            )

        players = []

        async def register_callbacks(pc: aiortc.RTCPeerConnection, camera_quality: str):
            @pc.on("connectionstatechange")
            async def on_connectionstatechange():
                print("Connection state is %s" % pc.connectionState)
                if pc.connectionState == "failed":
                    print("Close connection.")
                    await pc.close()
                    pcs.discard(pc)
            @pc.on("iceconnectionstatechange")
            async def on_iceconnectionstatechange():
                print(f"ICE connection state is {pc.iceConnectionState}")

                if pc.iceConnectionState == "failed":
                    print("Ice failed.")
            control_channel = pc.createDataChannel('control')
            @pc.on("datachannel")
            def on_datachannel(channel):
                @channel.on("message")
                def on_message(message):
                    global last_ping_time, stopped
                    try:
                        data: dict = json.loads(message)
                        if data['type'] == 'motors':
                            robot_stub.SetThrust(robot_pb2.MotorsThrust(LeftMotor=data['left'], RightMotor=data['right']))
                            stopped = False
                        elif data['type'] == 'gimbal':
                            robot_stub.SetGimbal(robot_pb2.GimbalPosition(VerticalAngle=data['vertical'], HorizontalAngle=data['horizontal']))
                            stopped = False
                        elif data['type'] == 'laser':
                            robot_stub.SetLaser(robot_pb2.LaserState(Power=data['value']))
                        elif data['type'] == 'ping':
                            last_ping_time = time()
                        else:
                            logger.warning("An unexpected data type got.")
                    except json.JSONDecodeError:
                        logger.warning("JSON decode error.")
                    except KeyError:
                        logger.warning("KeyError. Message json payload is not valid.")
            self.notifier_channel = pc.createDataChannel('notify')
            relay = MediaRelay()
            for p in players:
                p._stop(p.video)
            player = MediaPlayer(cameras[system]['camera'], format=cameras[system]['format'], options={**camera_config, 'video_size': camera_quality})
            players.append(player)
            # audio_player = MediaPlayer("default", format="pulse", options={
            #     'enable-libpulse': True
            # })
            video = relay.subscribe(player.video, buffered=False)
            track = pc.addTrack(video)
            force_codec(pc, track, cameras[system]['codec'])
            # audio = relay.subscribe(audio_player.audio)
            # track2 = pc.addTrack(audio)
            # force_codec(pc, track)

        @logger.catch()
        async def start_notifications_sender():
            while True:
                ...
                # msg = await self.notifications_queue.get()
                # if self.notifier_channel is None:
                #     logger.warning("Notifier channel is None!")
                # else:
                #     if self.notifier_channel.readyState != 'open':
                #         ...
                #         # logger.warning("Trying to send notification to a closed channel.")
                #     else:
                #         self.notifier_channel.send(msg)

        async def offer(request):
            params = await request.json()
            offer = aiortc.RTCSessionDescription(sdp=params["sdp"], type=params["type"])

            pc = aiortc.RTCPeerConnection()
            # pc_id = "PeerConnection(%s)" % uuid.uuid4()
            pcs.add(pc)

            await register_callbacks(pc, params['camera_size'])

            await pc.setRemoteDescription(offer)

            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            if not watchdog_running:
                asyncio.create_task(watchdog())
                asyncio.create_task(start_notifications_sender())

            return web.Response(
                content_type="application/json",
                text=json.dumps(
                    {
                        "sdp": pc.localDescription.sdp, 
                        "type": pc.localDescription.type,
                        "expected_framerate": camera_config['min_framerate']
                    }
                ),
            )

        def emergency_stop():
            global stopped
            logger.warning("Emergency stop")
            robot_stub.SetThrust(robot_pb2.MotorsThrust(LeftMotor=0, RightMotor=0))
            robot_stub.SetGimbal(robot_pb2.GimbalPosition(VerticalAngle=0, HorizontalAngle=0))
            stopped = True

        async def watchdog():
            global watchdog_running
            watchdog_running = True
            while True:
                if not stopped and time() - last_ping_time > 1000:
                    emergency_stop()
                await asyncio.sleep(200)

        async def on_shutdown(app):
            # close peer connections
            coros = [pc.close() for pc in pcs]
            await asyncio.gather(*coros)
            pcs.clear()

        app = web.Application()
        app.on_shutdown.append(on_shutdown)
        app.router.add_get("/", index)
        # app.router.add_get("/client.js", javascript)
        app.router.add_post("/offer", offer)

        web.run_app(
            app, access_log=None, host='0.0.0.0', port=8080
        )