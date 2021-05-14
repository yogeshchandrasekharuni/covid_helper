from tkinter import *
from bot import Bot
from gui.thread_killer import KThread
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


class AppGUI:

    def __init__(self):
        self.bot = Bot()
        self.status = False
        self.main_thread = KThread(target=self.bot.main)
        self.to_plot = 'temp'
        self.plot_coordinates = (None, None)


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
                text = '''\
                    Number of reminder emails sent: {}
                    Number of readings recieved: {}
                    Number of daily tables sent out: {}
                    '''.format(
                        self.bot.n_reading_reminder_emails,
                        self.bot.n_recieved_reading_emails,
                        self.bot.n_daily_table_emails
                    )
                )

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
            print(data)
            
            # plotting
            fig = Figure(figsize = (4, 4), dpi = 100)
            plot1 = fig.add_subplot(111)
            plot1.plot(data['time'], data[self.to_plot])

            canvas = FigureCanvasTkAgg(fig, window)  
            canvas.draw()
            canvas.get_tk_widget().place(relx = self.plot_coordinates[0], rely = self.plot_coordinates[1], anchor = CENTER)


        def plot_o2():
            self.to_plot = 'o2'
            self.plot_coordinates = (0.8, 0.6)
            plot_graph()

        def plot_temp():
            self.to_plot = 'temp'
            self.plot_coordinates = (0.2, 0.6)
            plot_graph()


        window = Tk()
        window.title("Covid Helper")
        window.geometry('1400x800')

        title_label = Label(window, text='Covid Helper', bg='#0052cc', fg='#ffffff')
        title_label.place(relx = 0.5, rely=0.05, anchor=CENTER)
        _title_label_font = font.Font(size=25, weight='bold')
        title_label['font'] = _title_label_font


        running_status_label = Label(window, text=self.status)
        running_status_label.grid(column=0, row=0)

        updates_label = Label(
            window,
            text = '''\
            Number of reminder emails sent: 0
            Number of readings recieved: 0
            Number of daily tables sent out: 0

            Please click refresh to see the latest statistics
            ''' 
            )
        _updates_label_font = font.Font(size=12, weight='normal')
        updates_label['font'] = _updates_label_font
        updates_label.place(relx = 0.1, rely = 0.15, anchor = CENTER)

        updates_btn = Button(window, text='refresh stats', command = on_refresh_updates_click)
        _updates_btn_font = font.Font(size=12, weight='normal')
        updates_btn['font'] = _updates_btn_font
        updates_btn.place(relx = 0.1, rely = 0.22, anchor = CENTER)

        main_btn = Button(window, text="Start/Stop", command=on_main_button_click)
        main_btn.config(height = 3, width = 10 )
        _main_btn_font = font.Font(size=15, weight='bold')
        main_btn['font'] = _main_btn_font
        main_btn.place(relx=0.5, rely=0.2, anchor=CENTER)
        
        # button that displays the plot
        plot_temp_button = Button(window, command = plot_temp, text = "Plot Temperature")
        plot_temp_button.place(relx = 0.2, rely = 0.9, anchor = CENTER)

        plot_o2_button = Button(window, command = plot_o2, text = "Plot O2-Saturation")
        plot_o2_button.place(relx = 0.8, rely = 0.9, anchor = CENTER)

        window.mainloop()

if __name__ == '__main__':
    logger.info('GUI has started running.')
    gui = AppGUI()
    gui.main()
    logger.info('GUI has been terminated.')