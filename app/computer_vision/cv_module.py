from cv2.typing import MatLike


class CVModule:
    active = True

    def update(self, img: MatLike) -> None:
        """Update the Computer Vision module"""
        pass

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
