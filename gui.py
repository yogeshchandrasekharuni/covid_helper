from tkinter import *
from bot import Bot
from utils.thread_killer import KThread
import logging, logging.config, sys
from datetime import datetime
from logs.base_logger import logger
import numpy as np
from matplotlib import pyplot as plt
#from data.visualizer import Visualizer
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
from matplotlib.figure import Figure
import tkinter.font as font
import matplotlib.ticker as ticker
from pdb import set_trace
from PIL import Image, ImageTk
from tkinter import ttk


class AppGUI:

    def __init__(self):
        self.bot = Bot()
        self.status = False
        self.main_thread = KThread(target=self.bot.main)
        self.to_plot = 'temp'
        self.plot_coordinates = (None, None)
        self.is_shown = {'o2': False, 'temp': False, 'table': False}
        self.label_bg_color = '#e6e6fa'
        self.button_bg_color = '#D8BFD8'

    def _exit_handler(self):
        if self.main_thread is not None and self.main_thread.is_alive():
            self.main_thread.kill()
    
        self.window.destroy()

    def main(self): 

        def on_main_button_click():        

            if not self.status:
                running_status_label.configure(text="Program has begun running!")
                self.status = True
                if not self.main_thread:
                    self.main_thread = KThread(target=self.bot.main)

                logger.info('Bot thread has been started.')
                self.main_thread.start()

            else:
                running_status_label.configure(text="Program has been shut down!")
                self.status = False
                logger.info('Bot thread has been killed.')
                self.main_thread.kill()
                self.main_thread = None

        
        def on_refresh_updates_click():
            updates_label.configure(
                text = '''Number of reminder emails sent: {}\nNumber of readings recieved: {}\nNumber of daily tables sent out: {}'''.format(
                        self.bot.n_reading_reminder_emails,
                        self.bot.n_recieved_reading_emails,
                        self.bot.n_daily_table_emails
                    )
                )

            if self.is_shown['table']:
                show_table()
            if self.is_shown['o2']:
                plot_o2()
            if self.is_shown['temp']:
                plot_temp()



        def plot_graph():
            '''
            Plots stuff
            '''

            # getting the data
            data = pd.DataFrame(self.bot.db_handler.get_all_values(), columns = ['id', 'temp', 'o2', 'time'])
            fixed_times = []
            for index in range(data.shape[0]):
                #fixed_times.append(data.iloc[index].time.strftime("%d-%M/%H"))
                fixed_times.append(data.iloc[index].time.strftime("%I:%M %p"))

                pass

            data = data.sort_values('time', ascending=True)
            data.time = fixed_times
            
            # plotting
            fig = Figure(figsize = (4, 3), dpi = 100, tight_layout = True)
            plot1 = fig.add_subplot(111)
            plot1.title.set_text('{} vs Time'.format(
                'Temperature' if self.to_plot == 'temp' else 'O2-Saturation'
            ))

            plot1.plot(data['time'], data[self.to_plot], label = 'Readings')
            
            danger_zone = pd.DataFrame(data.time, columns = ['time'])
            danger_zone['danger_vals'] = [104] * data.shape[0] if self.to_plot == 'temp' else [94] * data.shape[0]

            plot1.plot(danger_zone['time'], danger_zone['danger_vals'], color='red', linestyle = 'dashed', label = 'Max temperature' if self.to_plot == 'temp' else 'Min O2-Saturation')

            plot1.legend()

            canvas = FigureCanvasTkAgg(fig, window)  
            canvas.draw()
            canvas.get_tk_widget().place(relx = self.plot_coordinates[0], rely = self.plot_coordinates[1], anchor = CENTER)


        def plot_o2():
            self.to_plot = 'o2'
            self.is_shown['o2'] = True
            self.plot_coordinates = (0.8, 0.7)
            plot_graph()

        def plot_temp():
            self.to_plot = 'temp'
            self.is_shown['temp'] = True
            self.plot_coordinates = (0.2, 0.7)
            plot_graph()

        def show_table():
            self.is_shown['table'] = True
            cols = ['ID', 'Temperature', 'O2-Saturation', 'Time']
            data = pd.DataFrame(self.bot.db_handler.get_all_values(), columns = cols)
            for y in range(len(data)+1):
                for x in range(len(cols)):
                    if y==0:
                        e=Entry(font=('Consolas 8 bold'),bg='light blue',justify='center')
                        #set_trace()
                        e.grid(column=x, row=y)
                        e.insert(0,cols[x])
                    else:
                        e=Entry(bg = self.label_bg_color)
                        e.grid(column=x, row=y)
                        if x == 3:
                            e.insert(0, data[cols[x]][y-1].strftime("%I:%M %p - %d/%m/%Y"))
                        else:
                            e.insert(0,data[cols[x]][y-1])

        
        window = Tk()

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self._exit_handler) 
        window.title("Covid Helper")
        window.geometry('1400x800')
        
        bg = ImageTk.PhotoImage(Image.open("utils/tkinter_bg.jpg"))
        # Create Canvas
        canvas1 = Canvas(window, width = 1400, height = 800)
        canvas1.place(relx = 0, rely = 0)
        
        # Display image
        canvas1.create_image(0, 0, image = bg, anchor = CENTER)

        title_label = Label(window, text='Covid Helper',bg = '#4169e1', fg='#ffffff')
        title_label.place(relx = 0.5, rely=0.05, anchor=CENTER)
        _title_label_font = font.Font(size=25, weight='bold')
        Font_tuple = ("Unispace", 20, "bold")
        title_label['font'] = Font_tuple


        running_status_label = Label(window, text='Program ready to start.', bg = self.label_bg_color)
        _running_status_label_font = font.Font(size=15, weight='normal')
        running_status_label['font'] = _running_status_label_font
        running_status_label.place(relx = 0.425, rely = 0.4)

        updates_label = Label(
            window,
            text = '''Number of reminder emails sent: 0\nNumber of readings recieved: 0\nNumber of daily tables sent out: 0\nPlease click refresh to see the latest statistics''',
            bg = self.label_bg_color
            )
        _updates_label_font = font.Font(size=12, weight='normal')
        updates_label['font'] = _updates_label_font
        updates_label.place(relx = 0.8, rely = 0.15, anchor = CENTER)

        updates_btn = Button(window, text='Refresh Stats', command = on_refresh_updates_click, bg = self.button_bg_color)
        _updates_btn_font = font.Font(size=12, weight='normal')
        updates_btn['font'] = _updates_btn_font
        updates_btn.place(relx = 0.825, rely = 0.25, anchor = CENTER)

        main_btn = Button(window, text="Start/Stop", command=on_main_button_click, bg = '#b0c4de', fg = '#000080')
        main_btn.config(height = 3, width = 10 )
        _main_btn_font = font.Font(size=15, weight='bold')
        main_btn['font'] = _main_btn_font
        main_btn.place(relx=0.5, rely=0.2, anchor=CENTER)
        
        # button that displays the plot
        plot_temp_button = Button(window, command = plot_temp, text = "Plot Temperature", bg = self.button_bg_color)
        plot_temp_button['font'] = font.Font(size=12, weight='normal')
        plot_temp_button.place(relx = 0.2, rely = 0.91, anchor = CENTER)

        plot_o2_button = Button(window, command = plot_o2, text = "Plot O2-Saturation", bg = self.button_bg_color)
        plot_o2_button['font'] = font.Font(size=12, weight='normal')
        plot_o2_button.place(relx = 0.8, rely = 0.91, anchor = CENTER)

        show_table_btn = Button(window, command = show_table, text = 'Show Readings', bg = self.button_bg_color)
        show_table_btn['font'] = font.Font(size=12, weight='normal')
        show_table_btn.place(relx = 0.16, rely = 0.4)

        window.mainloop()

if __name__ == '__main__':
    logger.info('GUI has started running.')
    gui = AppGUI()
    gui.main()
    logger.info('GUI has been terminated.')