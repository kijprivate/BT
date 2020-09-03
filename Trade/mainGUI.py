import coinex as coinex
import mxc as mxc
import kucoin as kucoin
import bkex as bkex
import liquid as liquid
import huobi as huobi
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import time
import math
from functools import partial

labels1 = []
labels2 = []

labelAmount1 = None

class Data():
    def __init__(self):
        self.firstDropdown = coinex
        self.secondDropdown = mxc
        self.currentPair = "ETHBTC"
        
        
def scanAll1(pair, module):
    ask = module.get_orders_asks(pair, 10)
    bid = module.get_orders_bids(pair, 10)
    ask.reverse()
    i=0
    for l in labels1:
        l.destroy()
    for a in range(len(ask)):
        label = tk.Label(frame, text = ask[a][0], bg = "red")
        labels1.append(label)
        label.place(x=0, y=70 + i)
        label = tk.Label(frame, text = ask[a][1], bg = "red")
        labels1.append(label)
        label.place(x=80, y=70 + i)
        i+=25
    
    for b in range(len(bid)):
        label = tk.Label(frame, text = bid[b][0], bg = "green")
        labels1.append(label)
        label.place(x=0, y=70 + i)
        label = tk.Label(frame, text = bid[b][1], bg = "green")
        labels1.append(label)
        label.place(x=80, y=70 + i)
        i+=25
        
def scanAll2(pair, module):
    ask = module.get_orders_asks(pair, 10)
    bid = module.get_orders_bids(pair, 10)
    ask.reverse()
    i=0
    for l in labels2:
        l.destroy()
    for a in range(len(ask)):
        label = tk.Label(frame, text = ask[a][0], bg = "red")
        labels2.append(label)
        label.place(x=700, y=70 + i)
        label = tk.Label(frame, text = ask[a][1], bg = "red")
        labels2.append(label)
        label.place(x=780, y=70 + i)
        i+=25
        
    for b in range(len(bid)):
        label = tk.Label(frame, text = bid[b][0], bg = "green")
        labels2.append(label)
        label.place(x=700, y=70 + i)
        label = tk.Label(frame, text = bid[b][1], bg = "green")
        labels2.append(label)
        label.place(x=780, y=70 + i)
        i+=25

def retrieve_input_copyPair(data):
    inputValue=copyPairText.get("1.0","end-1c")
    data.currentPair = inputValue
    scan1.configure(command=partial(scanAll1, data.currentPair, data.firstDropdown))
    scan2.configure(command=partial(scanAll2, data.currentPair, data.secondDropdown))

def retrieve_input_getAmount(module):
    inputValue=getAmountText.get("1.0","end-1c")
    val = module.get_amount(inputValue)
    
    labelAmount1 = tk.Label(frame, text = val, bg = "orange")
    labelAmount1.pack()
    # add label

def retrieve_input_withdrawalFee(module):
    inputValue=(str)(getWithdrawalText.get("1.0","end-1c"))
    val = module.withdraw_fee(inputValue)
    
    labelAmount1 = tk.Label(frame, text = val, bg = "orange")
    labelAmount1.pack()

def change_dropdown1(*args):
    if(popupMenu1.current() == 0):
        data.firstDropdown = coinex
        scan1.configure(command=partial(scanAll1, data.currentPair, data.firstDropdown))
    elif(popupMenu1.current() == 1):
        data.firstDropdown = mxc
        scan1.configure(command=partial(scanAll1, data.currentPair, data.firstDropdown))
    elif(popupMenu1.current() == 2):
        data.firstDropdown = kucoin
        scan1.configure(command=partial(scanAll1, data.currentPair, data.firstDropdown))
        
def change_dropdown2(*args):
    if(popupMenu2.current() == 0):
        data.secondDropdown = coinex
        scan2.configure(command=partial(scanAll2, data.currentPair, data.secondDropdown))
    elif(popupMenu2.current() == 1):
        data.secondDropdown = mxc
        scan2.configure(command=partial(scanAll2, data.currentPair, data.secondDropdown))
    elif(popupMenu2.current() == 2):
        data.secondDropdown = kucoin
        scan2.configure(command=partial(scanAll2, data.currentPair, data.secondDropdown))
        
if __name__ == '__main__':

    data = Data()
    
    root = tk.Tk()
    
    canvas = tk.Canvas(root, height=700, width=1000, bg="#263D42")
    canvas.pack()
    
    frame = tk.Frame(root, bg="white")
    frame.place(relwidth=0.9, relheight=0.9, relx=0.05, rely=0.05)
    
    copyPairText = tk.Text(frame, height=2, width=10, bg="grey")
    copyPairText.pack()
    
    copyPair = tk.Button(frame, text="CopyPair", padx=10, pady=5, fg="white", bg="#263D42", command=lambda:retrieve_input_copyPair(data))
    copyPair.pack()
    
    getAmountText = tk.Text(frame, height=2, width=10, bg="grey")
    getAmountText.pack()
    
    getAmount = tk.Button(frame, text="GetAmount", padx=10, pady=5, fg="white", bg="#263D42", command=lambda:retrieve_input_getAmount(data.firstDropdown))
    getAmount.pack()
    
    getWithdrawalText = tk.Text(frame, height=2, width=10, bg="grey")
    getWithdrawalText.pack()
    
    getWithdrawalFee = tk.Button(frame, text="GetWithdrawalFee", padx=10, pady=5, fg="white", bg="#263D42", command=lambda:retrieve_input_withdrawalFee(data.firstDropdown))
    getWithdrawalFee.pack()

    popupMenu1 = ttk.Combobox(frame, values = [coinex, mxc, kucoin])
    popupMenu1.current(0)
    popupMenu1.bind("<<ComboboxSelected>>", change_dropdown1)
    popupMenu1.place(x=0, y=40)
    
    popupMenu2 = ttk.Combobox(frame, values = [coinex, mxc, kucoin])
    popupMenu2.current(1)
    popupMenu2.bind("<<ComboboxSelected>>", change_dropdown2)
    popupMenu2.place(x=750, y=40)
    

                    
    scan1 = tk.Button(frame, text="Scan", padx=10, pady=5, fg="white", bg="#263D42", command=partial(scanAll1, data.currentPair, data.firstDropdown))
    scan1.place(x=0, y=0)
    
    scan2 = tk.Button(frame, text="Scan", padx=10, pady=5, fg="white", bg="#263D42", command=partial(scanAll2, data.currentPair, data.secondDropdown))
    scan2.place(x=800, y=0)
    
    root.mainloop()

