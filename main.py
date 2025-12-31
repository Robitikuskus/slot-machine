import tkinter as tk
import random
import time
from pygame import mixer
from threading import Thread


class SlotMachine:
    def __init__(self, root):
        self.root = root
        self.root.title("Slot Machine")

        # Icon image
        self.icon = tk.PhotoImage(file="wild_west_images\\background.png")
        self.root.iconphoto(False, self.icon)

        # Background image
        self.background_image = tk.PhotoImage(file="wild_west_images\\background.png")

        # Adjust window size to match background image
        self.root.geometry(f"{self.background_image.width()}x{self.background_image.height()}")
        self.root.attributes('-fullscreen', True)
        self.state = True
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)

        # Canvas for images
        self.canvas = tk.Canvas(self.root,
                                width=self.background_image.width(),
                                height=self.background_image.height(),
                                bg="black",
                                highlightthickness=0)
        self.canvas.place(x=0, y=0)

        # Background image on canvas
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_image)

        # Images for the slots
        self.images = [tk.PhotoImage(file=f"wild_west_images\\{i}.png") for i in range(1, 11)]
        self.compressed_images_bottom = [tk.PhotoImage(file=f"wild_west_images\\{i}.1.png") for i in range(1, 11)]
        self.compressed_images_top = [tk.PhotoImage(file=f"wild_west_images\\{i}.1.png") for i in range(1, 11)]

        self.win_image = tk.PhotoImage(file="wild_west_images\\victory.png")
        self.jackpot_image = tk.PhotoImage(file="wild_west_images\\jackpot.png")
        self.lose_image = tk.PhotoImage(file="wild_west_images\\lose.png")

        # Slot positions
        self.slot_positions = [580, 1080, 1580]  # X-coordinates for the three slots
        self.slots = []
        for x in self.slot_positions:
            compressed_image_top = self.canvas.create_image(x, 320, image=self.compressed_images_top[0], anchor=tk.NW)
            normal_image = self.canvas.create_image(x, 560, image=self.images[0], anchor=tk.NW)
            compressed_image_bottom = self.canvas.create_image(x, 790, image=self.compressed_images_bottom[0], anchor=tk.NW)
            self.slots.append((compressed_image_top, normal_image, compressed_image_bottom))

        # Sounds
        mixer.init()
        self.win_sound = mixer.Sound("sounds\\jackpot.mp3")
        self.jackpot_sound = mixer.Sound("sounds\\jackpot.mp3")

        self.loss_sound = [mixer.Sound("sounds\\plankton_loss.mp3"),
                           mixer.Sound("sounds\\rot_loss.mp3"),
                           mixer.Sound("sounds\\pipe_loss.mp3"),
                           mixer.Sound("sounds\\kitty_loss.mp3"),
                           mixer.Sound("sounds\\fart_loss.mp3")
                           ]
        self.spinning = mixer.Sound("sounds\\spinning.mp3")

        self.loss_counter = 0

        # Control variables
        self.stopping_times = [5, 7, 9]  # Seconds
        self.current_images = [0, 0, 0]  # Current slot images
        self.running = [True, True, True]  # Animation status for each slot
        self.last_images = self.current_images.copy()
        self.win_chance = 0.20
        self.jackpot_chance = 0.001

        # Start button with image
        self.start_button_image = tk.PhotoImage(file="wild_west_images\\start_button.png").subsample(4, 4)
        self.start_button = tk.Button(self.root,
                                      image=self.start_button_image,
                                      command=self.start_game,
                                      width=493,
                                      height=250)
        self.start_button.place(x=1030, y=1068)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state
        self.root.attributes("-fullscreen", self.state)

    def end_fullscreen(self, event=None):
        self.state = False
        self.root.attributes("-fullscreen", False)

    def start_game(self):
        self.start_button.config(state=tk.DISABLED)
        self.running = [True, True, True]
        self.current_images = [0, 0, 0]
        self.start_time = time.time()

        self.play_sound_in_thread(self.spinning)

        self.update_slots()

    def update_slots(self):
        elapsed_time = time.time() - self.start_time

        for i in range(3):
            if self.running[i]:
                if elapsed_time >= self.stopping_times[i]:
                    self.running[i] = False

                    if i == 0 and random.random() < self.jackpot_chance ** (1/3):
                        self.current_images[0] = len(self.images) - 1

                    elif i == 1:
                        if random.random() < self.jackpot_chance ** (1/3):
                            self.current_images[1] = len(self.images) - 1
                        if random.random() < self.win_chance ** .5:
                            self.current_images[1] = self.current_images[0]

                    elif i == 2:
                        if random.random() < self.jackpot_chance ** (1/3):
                            self.current_images[2] = len(self.images) - 1
                        if random.random() < self.win_chance ** .5 \
                            and self.current_images[0] == self.current_images[1]:
                            self.current_images[2] = self.current_images[0]

                    self.update_slot_images(i)
                else:
                    self.animate_slot(i)

        if any(self.running):
            self.root.after(200, self.update_slots)  # Adjusted speed for smooth animation
        else:
            self.check_result()

    def set_images(self, slot_index):
        next_image = random.randint(0, len(self.images) - 2)
        while next_image == self.current_images[slot_index]:
            next_image = random.randint(0, len(self.images) - 2)

        compressed_image_top, normal_image, compressed_image_bottom = self.slots[slot_index]

        self.canvas.itemconfig(compressed_image_top,
                               image=self.compressed_images_top[next_image])
        self.canvas.itemconfig(normal_image,
                               image=self.images[self.current_images[slot_index]])
        self.canvas.itemconfig(compressed_image_bottom,
                               image=self.compressed_images_bottom[self.last_images[slot_index]])

        return next_image

    def animate_slot(self, slot_index):
        next_image = self.set_images(slot_index)

        self.last_images[slot_index] = self.current_images[slot_index]
        self.current_images[slot_index] = next_image

    def update_slot_images(self, slot_index):
        next_image = self.set_images(slot_index)
        self.root.update()

    def check_result(self):
        time.sleep(1)
        if self.current_images[0] == self.current_images[1] == self.current_images[2]:
            if self.current_images[0] == 10:
                self.show_fullscreen_image(self.jackpot_image)
                self.play_sound_in_thread(self.jackpot_sound)
            else:
                self.play_sound_in_thread(self.win_sound)
                self.show_fullscreen_image(self.win_image)
        else:
            self.play_sound_in_thread(self.loss_sound[self.loss_counter])
            self.loss_counter += 1
            if self.loss_counter == len(self.loss_sound):
                self.loss_counter = 0

            self.show_fullscreen_image(self.lose_image)

        self.start_button.config(state=tk.NORMAL)

    def show_fullscreen_image(self, image):
        fullscreen_canvas = tk.Canvas(self.root,
                                       width=self.background_image.width(),
                                       height=self.background_image.height(),
                                       highlightthickness=0)
        fullscreen_canvas.place(x=0, y=0)
        fullscreen_canvas.create_image(0, 0, image=image, anchor=tk.NW)

        self.root.update()
        time.sleep(5)
        fullscreen_canvas.destroy()

    def play_sound(self, sound):
        mixer.Sound.play(sound)

    def play_sound_in_thread(self, sound):
        Thread(target=self.play_sound, args=(sound,), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SlotMachine(root)
    root.mainloop()

#python -m nuitka main.py --follow-imports --standalone --jobs=4 --onefile --windows-icon-from-ico=wild_west_images/background.png --windows-console-mode=disable --enable-plugin=tk-inter
