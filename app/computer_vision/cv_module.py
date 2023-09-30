class CVModule:
    active = True

    def update(self, img) -> None:
        """Update the Computer Vision module"""
        pass

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
