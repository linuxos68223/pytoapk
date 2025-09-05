from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import os

# Change this path to the folder containing your photos
PHOTO_DIR = "/sdcard/DCIM/Camera"  # Common path on Android


class GalleryApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical")

        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=2, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        # Load images from folder
        if os.path.exists(PHOTO_DIR):
            for file in os.listdir(PHOTO_DIR):
                if file.lower().endswith((".jpg", ".png", ".jpeg")):
                    img_path = os.path.join(PHOTO_DIR, file)
                    btn = Button(size_hint_y=None, height=200)
                    img = Image(source=img_path, allow_stretch=True, keep_ratio=True)
                    btn.add_widget(img)
                    grid.add_widget(btn)

        scroll.add_widget(grid)
        root.add_widget(scroll)

        return root


if __name__ == "__main__":
    GalleryApp().run()
