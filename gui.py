from tkinter import *
from app import App
from utils.thread_killer import KThread
import logging, logging.config, sys
from datetime import datetime
from logs.base_logger import logger
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
from matplotlib.figure import Figure
import tkinter.font as font
import matplotlib.ticker as ticker
from pdb import set_trace
from PIL import Image, ImageTk
from tkinter import ttk
from typing import List, Tuple
import smtplib


class AppGUI:
    '''
    Graphical Interface for CovidHelper
    '''

    def __init__(
        self
        ) -> None:
        '''
        Initializes the GUI's dependencies
        '''
        
        print('INFO: GUI initialized.')
        self.app = App()
        self.status = False # stores running status
        self.main_thread = KThread(target=self.app.main) # thread to run app on
        self.to_plot = 'temp' # indicates what plot to display
        self.plot_coordinates = (None, None) 
        self.is_shown = {'o2': False, 'temp': False, 'table': False} # keeps track of shown tables / plots
        self.label_bg_color = '#e6e6fa' # all labels will have this background color
        self.button_bg_color = '#D8BFD8' # all buttons will have this background color
        self.max_show = 12

    def _exit_handler(self):
        '''
        Called when window is closed.
        If user does not manually STOP the app thread before closing the window, this function will kill it.
        '''
        if self.main_thread is not None and self.main_thread.is_alive():
            self.main_thread.kill()
            logger.info('Main thread has been killed.')
            print('INFO: Main thread killed.')

        print('INFO: GUI closed.')
        self.window.destroy() # destroy the window

    def main(
        self
        ) -> None:
        '''
        Main method of the GUI
        '''

        def on_main_button_click() -> None:
            '''
            Called when START/STOP button is called
            Spawns or kills the app thread    
            '''
            print('INFO: Start/Stop button clicked.')

            def show_warning(
                message: str
                ) -> None:
                '''
                Displays a pop-up window with a warning message
                '''
                print('WARN: {}'.format(message))
                warning_window = Toplevel(self.window)
                warning_window.title('Warning')
                warning_window.geometry('300x100')

                warning_label = Label(warning_window, text = message)
                warning_label['font'] = font.Font(size=13, weight='normal')
                warning_label.place(relx = 0, rely = 0.2)


            if not self.app.email_handler.sender_email or not self.app.email_handler.sender_password or not self.app.email_handler.reciever_email:
                # if atleast one of the necessary creds are missing, display a warning message
                show_warning(message = 'Missing Credentials:\nPlease go to the settings section to update your details.')
                return

            
            if not self.status:
                # if program is not running, start the thread 

                if not self.app.email_handler.check_email():
                    show_warning(message = 'Invalid Credentials:\nPlease check your email and password.')
                    return

                running_status_label.configure(text="Program has begun running!")
                self.status = True
                if not self.main_thread:
                    self.main_thread = KThread(target=self.app.main)

                self.main_thread.start()
                logger.info('App thread has been started.')
                print('INFO: Main thread started.')

            else:

                # if program is already running, kill the thread
                running_status_label.configure(text="Program has been shut down!")
                self.status = False
                self.main_thread.kill()
                logger.info('app thread has been killed.')
                print('INFO: Main thread killed.')
                self.main_thread = None

        
        def on_refresh_updates_click() -> None:
            '''
            Called when REFRESH button is clicked
            Updates all tables and graphs if already displayed
            '''

            print('INFO: Refresh stats button clicked.')
            logger.info('Refresh stats button clicked.')
            updates_label.configure(
                text = '''Number of reminder emails sent: {}\nNumber of readings recieved: {}\nNumber of daily tables sent out: {}'''.format(
                        self.app.n_reading_reminder_emails,
                        self.app.n_recieved_reading_emails,
                        self.app.n_daily_table_emails
                    )
                )

            if self.is_shown['table']:
                show_table()
            if self.is_shown['o2']:
                plot_o2()
            if self.is_shown['temp']:
                plot_temp()



        def plot_graph() -> None:
            '''
            Plots either temperature or oxygen-saturation on the GUI
            '''

            print('INFO: {} has been graphed.'.format('Temperature' if self.to_plot == 'temp' else 'O2-Saturation'))
            # getting the data
            data = pd.DataFrame(self.app.get_todays_readings(), columns = ['id', 'temp', 'o2', 'time'])

            fixed_times = []
            for index in range(data.shape[0]):
                # make time readable
                fixed_times.append(data.iloc[index].time.strftime("%I:%M %p"))

            data = data.sort_values('time', ascending=True).head(self.max_show) # sort data based on time
            data.time = fixed_times
            
            # plotting
            fig = Figure(figsize = (4, 3), dpi = 100, tight_layout = True)
            plot1 = fig.add_subplot(111)
            plot1.title.set_text('{} vs Time'.format(
                'Temperature' if self.to_plot == 'temp' else 'O2-Saturation'
            ))
            plot1.set_xticklabels(labels = fixed_times, rotation = 75)
            plot1.plot(data['time'], data[self.to_plot], label = 'Readings')
            
            # also plotting worst case readings
            # considering 94% saturation and 104* F as critical readings
            danger_zone = pd.DataFrame(data.time, columns = ['time'])
            danger_zone['danger_vals'] = [104] * data.shape[0] if self.to_plot == 'temp' else [94] * data.shape[0]

            plot1.plot(danger_zone['time'], danger_zone['danger_vals'], color='red', linestyle = 'dashed', label = 'Max temperature' if self.to_plot == 'temp' else 'Min O2-Saturation')
            plot1.legend()

            canvas = FigureCanvasTkAgg(fig, self.window)  
            canvas.draw()
            canvas.get_tk_widget().place(relx = self.plot_coordinates[0], rely = self.plot_coordinates[1], anchor = CENTER)


        def plot_o2() -> None:
            '''
            Called when Plot O2 button is called
            '''
            self.to_plot = 'o2'
            self.is_shown['o2'] = True
            self.plot_coordinates = (0.8, 0.7)
            plot_graph()

        def plot_temp() -> None:
            '''
            Called when plot temp button is called
            '''
            self.to_plot = 'temp'
            self.is_shown['temp'] = True
            self.plot_coordinates = (0.2, 0.7)
            plot_graph()

        def show_table():
            '''
            Displays readings
            '''

            print('INFO: Readings table displayed.')
            self.is_shown['table'] = True
            cols = ['ID', 'Temperature', 'O2-Saturation', 'Time']
            #data = pd.DataFrame(self.app.db_handler.get_all_values(), columns = cols)
            data = pd.DataFrame(self.app.get_todays_readings(), columns = cols)
        
            data = data.sort_values('Time', ascending=False, ignore_index=True)

            for y in range(min(len(data)+1, self.max_show)):
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

        def open_settings() -> None:
            '''
            Opens a pop-up window to set credentials
            '''

            print('INFO: Settings window opened.')
            logger.info('Settings window opened.')

            settings_window = Toplevel(self.window)
            settings_window.title('Settings')
            settings_window.geometry('600x400')

            # user email
            label_user_email = Label(settings_window, text = 'Enter your email:')
            label_user_email['font'] = font.Font(size=13, weight='normal')
            label_user_email.place(relx = 0.2, rely = 0.1)
            user_email = Text(settings_window, height = 2, width = 20)
            user_email.place(relx = 0.5, rely = 0.1)

            # burner email
            label_burner_email = Label(settings_window, text = 'Enter your burner email:')
            label_burner_email['font'] = font.Font(size=13, weight='normal')
            label_burner_email.place(relx = 0.2, rely = 0.3)
            burner_email = Text(settings_window, height = 2, width = 20)
            burner_email.place(relx = 0.5, rely = 0.3)

            # burner email password
            label_burner_pass = Label(settings_window, text = 'Enter your burner\nemail\'s password:')
            label_burner_pass['font'] = font.Font(size=13, weight='normal')
            label_burner_pass.place(relx = 0.2, rely = 0.5)
            burner_pass = Text(settings_window, height = 2, width = 20)
            burner_pass.place(relx = 0.5, rely = 0.5)


            def get_inputs() -> None:
                '''
                Retrieves inputs from the input fields in settings window
                '''

                inputs = []
                input_fields = [user_email, burner_email, burner_pass]
                for field in input_fields:
                    inputs.append(field.get(1.0, 'end-1c'))

                self.app.email_handler.set_credentials(
                    reciever_email = inputs[0],
                    sender_email = inputs[1],
                    sender_password = inputs[2],
                    save_changes = True
                    )         

                save_status.configure(text = 'Changes have been saved.')       
                
            save_button = Button(settings_window, text = 'Save changes', command = get_inputs)
            save_button.place(relx = 0.5, rely = 0.8)

            save_status = Label(settings_window, text='')
            save_status['font'] = font.Font(size=10, weight='normal')
            save_status.place(relx = 0.45, rely = 0.7)

        
        self.window = Tk() # create the GUI object

        self.window.protocol('WM_DELETE_WINDOW', self._exit_handler) # override exit handler
        self.window.title("Covid Helper")
        self.window.geometry('1400x800') # set resolution
        
        bg = ImageTk.PhotoImage(Image.open("utils/tkinter_bg.jpg")) # use picture as GUI background
        # Create Canvas
        canvas1 = Canvas(self.window, width = 1400, height = 800)
        canvas1.place(relx = 0, rely = 0)
        
        # Display image
        canvas1.create_image(0, 0, image = bg, anchor = CENTER)

        # set title
        title_label = Label(self.window, text='Covid Helper',bg = '#4169e1', fg='#ffffff')
        title_label.place(relx = 0.5, rely=0.05, anchor=CENTER)
        _title_label_font = font.Font(size=25, weight='bold')
        Font_tuple = ("Unispace", 20, "bold")
        title_label['font'] = Font_tuple

        # display running status
        running_status_label = Label(self.window, text='Program ready to start.', bg = self.label_bg_color)
        _running_status_label_font = font.Font(size=15, weight='normal')
        running_status_label['font'] = _running_status_label_font
        running_status_label.place(relx = 0.425, rely = 0.4)

        # display updates
        updates_label = Label(
            self.window,
            text = '''Number of reminder emails sent: 0\nNumber of readings recieved: 0\nNumber of daily tables sent out: 0\nPlease click refresh to see the latest statistics''',
            bg = self.label_bg_color
            )
        _updates_label_font = font.Font(size=12, weight='normal')
        updates_label['font'] = _updates_label_font
        updates_label.place(relx = 0.8, rely = 0.15, anchor = CENTER)

        updates_btn = Button(self.window, text='Refresh Stats', command = on_refresh_updates_click, bg = self.button_bg_color)
        _updates_btn_font = font.Font(size=12, weight='normal')
        updates_btn['font'] = _updates_btn_font
        updates_btn.place(relx = 0.825, rely = 0.25, anchor = CENTER)

        # start-stop button
        main_btn = Button(self.window, text="Start/Stop", command=on_main_button_click, bg = '#b0c4de', fg = '#000080')
        main_btn.config(height = 3, width = 10 )
        _main_btn_font = font.Font(size=15, weight='bold')
        main_btn['font'] = _main_btn_font
        main_btn.place(relx=0.5, rely=0.2, anchor=CENTER)
        
        # button that displays the plot
        plot_temp_button = Button(self.window, command = plot_temp, text = "Plot Temperature", bg = self.button_bg_color)
        plot_temp_button['font'] = font.Font(size=12, weight='normal')
        plot_temp_button.place(relx = 0.2, rely = 0.91, anchor = CENTER)

        plot_o2_button = Button(self.window, command = plot_o2, text = "Plot O2-Saturation", bg = self.button_bg_color)
        plot_o2_button['font'] = font.Font(size=12, weight='normal')
        plot_o2_button.place(relx = 0.8, rely = 0.91, anchor = CENTER)

        # show readings as a table
        show_table_btn = Button(self.window, command = show_table, text = 'Show Readings', bg = self.button_bg_color)
        show_table_btn['font'] = font.Font(size=12, weight='normal')
        show_table_btn.place(relx = 0.16, rely = 0.4)


        settings_button = Button(self.window, text='Settings', command = open_settings, bg = self.button_bg_color)
        settings_button['font'] = font.Font(size=12, weight='normal')
        settings_button.place(relx=0.94, rely=0.05)

        # infinite loop for GUI
        self.window.mainloop()

if __name__ == '__main__':
    logger.info('GUI has started running.')
    gui = AppGUI()
    gui.main()
    logger.info('GUI has been terminated.')