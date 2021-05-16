import asyncio
import glob
import os
from copy import deepcopy
from dataclasses import dataclass
from os.path import join
from pathlib import Path

from minotaur import Inotify, Mask

PROC_PATH = "/proc"


def lsof(filename):
    pids = [int(name) for name in os.listdir(PROC_PATH) if name.isnumeric()]
    result = set()
    for pid in pids:
        try:
            p_path = join(PROC_PATH, str(pid))
            fd_path = join(p_path, "fd")
            fds = os.listdir(fd_path)
            for fd in fds:
                if os.readlink(join(fd_path, fd)) == filename:
                    p_name = join(p_path, "comm")
                    name = Path(p_name).read_text().rstrip()
                    result.add(name)
        except (PermissionError, FileNotFoundError):
            continue
    return list(result)


async def camera_users():
    result = []
    for filename in glob.glob("/dev/video*"):
        result += lsof(filename)
    return list(set(result))


class Camera:
    def __init__(self):
        self._users = []

    async def users(self):
        self._users = await camera_users()
        yield deepcopy(self._users)
        self._cameras = glob.glob("/dev/video*")

        with Inotify(blocking=False) as inotify:
            for camera in self._cameras:
                inotify.add_watch(camera, Mask.OPEN | Mask.CLOSE)

            async for event in inotify:
                users = await camera_users()
                if users != self._users:
                    self._users = users
                    yield deepcopy(self._users)