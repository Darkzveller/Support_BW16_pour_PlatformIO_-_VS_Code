from platformio.public import PlatformBase


class RealtekamebadPlatform(PlatformBase):
    def is_embedded(self):
        return True
