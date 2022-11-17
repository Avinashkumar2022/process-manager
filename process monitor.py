import psutil
from datetime import datetime
import pandas as pd
import time
import os
import tkinter
from tkinter import*
from prettytable import PrettyTable

root=Tk()
root.geometry("500x500")
root.maxsize(900,700)
root.minsize(200,300)
root.title("PROCESS MONITOR")
root.configure(bg="black")

f=Frame(root,borderwidth=5,bg="red",relief=RAISED)
f.pack(side=LEFT,anchor="nw")

battery = psutil.sensors_battery().percent
# print("----Battery Available: %d " % (battery,) + "%")
btr=str(battery)

def pro():
    t1=PrettyTable([""])
    for process in psutil.process_iter():
            # get all process info in one shot
            with process.oneshot():
                # get the process id
                pid = process.pid
                print(process)

def network():
    print("----Networks----")
    table = PrettyTable(['Network', 'Status', 'Speed'])
    for key in psutil.net_if_stats().keys():
            name = key
            up = "Up" if psutil.net_if_stats()[key].isup else "Down"
            speed = psutil.net_if_stats()[key].speed
            table.add_row([name, up, speed])
    print(table)

def mem():   
 print("----Memory----")
 memory_table = PrettyTable(["Total(GB)", "Used(GB)","Available(GB)", "Percentage"])
 vm = psutil.virtual_memory()
 memory_table.add_row([
 		f'{vm.total / 1e9:.3f}', f'{vm.used / 1e9:.3f}', f'{vm.available / 1e9:.3f}', vm.percent
   ])
 
 print(memory_table)


def clear():
    os.system('cls') 
def main(): 
    def get_size(bytes):
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
                return f"{bytes:.2f}{unit}B"
            bytes /= 1024
    
    
    def get_processes_info():
    
        processes = []
        for process in psutil.process_iter():
        
            with process.oneshot():
                pid = process.pid
    
                name = process.name()
                try:
                    create_time = datetime.fromtimestamp(process.create_time())
                    
                except OSError:
                    create_time = datetime.fromtimestamp(psutil.boot_time())
                    
                try:
                    cores = len(process.cpu_affinity())
                    cpu_usage = process.cpu_percent()
                    status = process.status()
                except psutil.AccessDenied:
                    cores = 0
                cpu_usage = process.cpu_percent()
                status = process.status()
                try:
                    nice = int(process.nice())
                except psutil.AccessDenied:
                    nice = 0
                try:
                    memory_usage = process.memory_full_info().uss
                except psutil.AccessDenied:
                    memory_usage = 0
                io_counters = process.io_counters()
                read_bytes = io_counters.read_bytes
                write_bytes = io_counters.write_bytes
                n_threads = process.num_threads()
                try:
                    username = process.username()
                except psutil.AccessDenied:
                    username = "N/A"
                
            processes.append({
                'pid': pid, 'name': name, 'create_time': create_time,
                'cores': cores, 'cpu_usage': cpu_usage, 'status': status, 'nice': nice,
                'memory_usage': memory_usage, 'read_bytes': read_bytes, 'write_bytes': write_bytes,
                'n_threads': n_threads, 'username': username,
                            })
    
        return processes

 
    def construct_dataframe(processes):
        df = pd.DataFrame(processes)
        df.set_index('pid', inplace=True)
        df.sort_values(sort_by, inplace=True, ascending=not descending)
        df['memory_usage'] = df['memory_usage'].apply(get_size)
        df['write_bytes'] = df['write_bytes'].apply(get_size)
        df['read_bytes'] = df['read_bytes'].apply(get_size)
        df['create_time'] = df['create_time'].apply(datetime.strftime, args=("%Y-%m-%d %H:%M:%S",))
        df = df[columns.split(",")]
        return df
    
    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser(description="Process Viewer & Monitor")
        parser.add_argument("-c", "--columns", help="""Columns to show,
                                                    available are name,create_time,cores,cpu_usage,status,nice,memory_usage,read_bytes,write_bytes,n_threads,username.
                                                    Default is name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,nice,n_threads,cores.""",
                            default="name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,nice,n_threads,cores")
        
        parser.add_argument("-s", "--sort-by", dest="sort_by", help="Column to sort by, default is memory_usage .", default="memory_usage")
        parser.add_argument("--descending", action="store_true", help="Whether to sort in descending order.")
        parser.add_argument("-n", help="Number of processes to show, will show all if 0 is specified, default is 25 .", default=4000)
        parser.add_argument("-u", "--live-update", action="store_true", help="Whether to keep the program on and updating process information each second")

        args = parser.parse_args()
        columns = args.columns
        sort_by = args.sort_by
        descending = args.descending
        n = int(args.n)
        live_update = args.live_update
        processes = get_processes_info()
        df = construct_dataframe(processes)
        if n == 0:
            print(df.to_string())
        elif n > 0:
            print(df.head(n).to_string())
        while live_update:
            processes = get_processes_info()
            df = construct_dataframe(processes)
            os.system("cls") if "nt" in os.name else os.system("clear")
            if n == 0:
                print(df.to_string())
            elif n > 0:
                print(df.head(n).to_string())
            time.sleep(0.7)



title= Label(text="PROCESS MONITOR",fg="yellow",bg="black",font="arial_rounded 30 bold", borderwidth=5,padx=20,pady=60,width=50).pack(side=TOP)


m=Button(root,fg="green yellow",text="MAIN",bg="black",font="gothic 0 bold",padx=44,pady=0, command=main).pack(side=TOP)

c=Button(root,fg="dodgerblue2",text="CLEAR",bg="black",font="gothic 0 bold",padx=39,pady=0, command=clear).pack(side=TOP)

p=Button(root,fg="red",text="PROCESSES",bg="black",font="gothic 0 bold",padx=21,pady=0, command=pro).pack(side=TOP)

n=Button(root,fg="darkorange",text="NETWORK",bg="black",font="gothic 0 bold",padx=31,pady=0, command=network).pack(side=TOP)


btr_lbl = Label(text="Battery status: " + btr + "%",fg="gold",bg="black",font="arial 10 bold", borderwidth=5,padx=2,pady=2).pack(side=BOTTOM,anchor="se")

root.mainloop()

    
    
