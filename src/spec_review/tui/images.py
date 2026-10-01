from textual_image.renderable import TGPImage as KittyRenderable
from textual_image.widget import TGPImage


class KittyImage(TGPImage, Renderable=KittyRenderable):
    """Release uploaded Kitty images when their document leaves the screen."""

    def on_unmount(self):
        self.image = None
