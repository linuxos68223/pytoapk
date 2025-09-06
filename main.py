from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.core.audio import SoundLoader
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.list import MDList, MDListItem, MDListItemLeadingIcon, MDListItemHeadlineText
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
import os, shutil, zipfile

KV = '''
BoxLayout:
    orientation: "vertical"

    MDTopAppBar:
        title: "Advanced File Manager"
        left_action_items: [["folder", lambda x: None]]

    MDScrollView:
        MDList:
            id: file_list
'''

class FileManagerApp(MDApp):
    def build(self):
        # Set theme
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.root = Builder.load_string(KV)
        # Start at home directory
        self.current_path = os.path.expanduser("~")
        self.load_files(self.current_path)
        return self.root

    # ---------- Snackbar helper ----------
    def show_snackbar(self, message):
        snackbar = MDSnackbar(
            MDSnackbarText(text=message),
            y=dp(24),
            pos_hint={"center_x": 0.5},
        )
        snackbar.open()

    # ---------- Load files/folders into MDList ----------
    def load_files(self, path):
        self.current_path = path
        file_list = self.root.ids.file_list
        file_list.clear_widgets()

        # Parent folder button
        parent = os.path.dirname(path)
        if parent and parent != path:
            item = MDListItem()
            item.add_widget(MDListItemLeadingIcon(icon="arrow-up"))
            item.add_widget(MDListItemHeadlineText(text=".. (Parent Folder)"))
            item.on_release = lambda p=parent: self.load_files(p)
            file_list.add_widget(item)

        # List folders first, then files
        for f in sorted(os.listdir(path), key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower())):
            full_path = os.path.join(path, f)
            item = MDListItem()
            icon = "folder" if os.path.isdir(full_path) else "file"
            item.add_widget(MDListItemLeadingIcon(icon=icon))
            item.add_widget(MDListItemHeadlineText(text=f))
            item.on_release = lambda p=full_path: self.on_item_click(p)
            file_list.add_widget(item)

    # ---------- When user clicks file/folder ----------
    def on_item_click(self, path):
        if os.path.isdir(path):
            self.load_files(path)
        else:
            self.open_options(path)

    # ---------- File options popup ----------
    def open_options(self, path):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        layout.add_widget(Button(text="Open", on_release=lambda x: self.open_file(path)))
        layout.add_widget(Button(text="Rename", on_release=lambda x: self.rename_file(path)))
        layout.add_widget(Button(text="Delete", on_release=lambda x: self.delete_file(path)))
        layout.add_widget(Button(text="Zip", on_release=lambda x: self.zip_file(path)))
        layout.add_widget(Button(text="Unzip", on_release=lambda x: self.unzip_file(path)))

        popup = Popup(title="Options", content=layout, size_hint=(0.7, 0.7))
        layout.add_widget(Button(text="Close", on_release=popup.dismiss))
        popup.open()

    # ---------- File openers ----------
    def open_file(self, path):
        ext = os.path.splitext(path)[1].lower()

        if ext in [".png", ".jpg", ".jpeg"]:
            popup = Popup(title="Image Viewer", content=Image(source=path), size_hint=(0.9, 0.9))
            popup.open()

        elif ext in [".mp3", ".wav"]:
            sound = SoundLoader.load(path)
            if sound:
                sound.play()
                self.show_snackbar("Playing audio...")

        elif ext in [".mp4", ".avi", ".mkv"]:
            video = Video(source=path)
            popup = Popup(title="Video Player", content=video, size_hint=(0.9, 0.9))
            video.state = 'play'
            popup.open()

        elif ext in [".txt", ".py", ".md"]:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            ti = TextInput(text=text, multiline=True)
            popup = Popup(title="Text Editor", content=ti, size_hint=(0.9, 0.9))
            popup.open()

        else:
            self.show_snackbar(f"Cannot open {ext} files yet")

    # ---------- File operations ----------
    def rename_file(self, path):
        box = BoxLayout(orientation="vertical")
        ti = TextInput(text=os.path.basename(path), multiline=False)
        box.add_widget(ti)
        btn = Button(text="Rename")
        box.add_widget(btn)

        popup = Popup(title="Rename File", content=box, size_hint=(0.7, 0.5))

        def do_rename(_):
            new_name = ti.text.strip()
            if new_name:
                new_path = os.path.join(os.path.dirname(path), new_name)
                os.rename(path, new_path)
                self.show_snackbar("Renamed successfully")
                popup.dismiss()
                self.load_files(self.current_path)

        btn.bind(on_release=do_rename)
        popup.open()

    def delete_file(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
            self.show_snackbar("Deleted successfully")
            self.load_files(self.current_path)
        except Exception as e:
            self.show_snackbar(str(e))

    def zip_file(self, path):
        try:
            zip_path = path + ".zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                if os.path.isfile(path):
                    zipf.write(path, os.path.basename(path))
                else:
                    for root, _, files in os.walk(path):
                        for file in files:
                            full_path = os.path.join(root, file)
                            zipf.write(full_path, os.path.relpath(full_path, os.path.dirname(path)))
            self.show_snackbar("Zipped successfully")
        except Exception as e:
            self.show_snackbar(str(e))

    def unzip_file(self, path):
        try:
            if path.endswith(".zip"):
                extract_path = os.path.splitext(path)[0]
                with zipfile.ZipFile(path, 'r') as zipf:
                    zipf.extractall(extract_path)
                self.show_snackbar(f"Unzipped to {extract_path}")
                self.load_files(self.current_path)
        except Exception as e:
            self.show_snackbar(str(e))


if __name__ == "__main__":
    FileManagerApp().run()

