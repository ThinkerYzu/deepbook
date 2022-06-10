import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import font
import os
import subprocess
import argparse

def get_gpg_enc_keys():
    fo = os.popen('gpg -k --with-colons', 'r')
    lines = [line.split(':') for line in fo.readlines()]
    ekeys = [l[4]
             for l in lines if l[0] == 'sub' and l[11] == 'e' and l[1] == 'u']
    return ekeys

def encrypt(plaintext, key):
    p = subprocess.Popen(['gpg', '--encrypt', '--recipient', key],
                         shell=False,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    (cipher, err) = p.communicate(input=plaintext, timeout=15)
    return cipher

def decrypt(cipher, key):
    p = subprocess.Popen(['gpg', '--decrypt', '--recipient', key],
                         shell=False,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    (plaintext, err) = p.communicate(input=cipher, timeout=15)
    return plaintext

def run_gui():
    def remove_found():
        ranges = text.tag_ranges('found')
        if ranges:
            text.tag_remove('found', ranges[0], ranges[1])
            pass
        pass

    def handle_save():
        txt = text.get('1.0', 'end')
        if txt[-1] == '\n':
            # tk text always append a new line.
            txt = txt[:-1]
            pass
        cipher = encrypt(txt.encode('utf-8'), enc_key)
        fo = open('deepbook.gpg', 'bw')
        fo.write(cipher)
        fo.close()
        bt_save['state'] = 'disabled'
        status_text.set('Updated')
        text.edit_modified('False')
        pass

    def do_search(pos):
        search_entry.grid(row=1, column=1, sticky='w')
        search_entry.focus_force()
        pass

    def stop_search(pos):
        remove_found()
        search_entry.grid_remove()
        text.focus_force()
        search_entry.delete('0', 'end')
        pass

    def do_search_cont(pos):
        remove_found()
        ptn = search_entry.get()
        if not ptn:
            return
        pos = text.search(ptn, 'insert')
        if not pos:
            return
        last = [int(v) for v in pos.split('.')]
        last[1] += len(ptn)
        last = '.'.join([str(v) for v in last])
        text.tag_add('found', pos, last)
        text.see(pos)
        text.mark_set('insert', pos)
        pass

    def do_search_next(pos):
        remove_found()
        ptn = search_entry.get()
        if not ptn:
            return
        pos = text.search(ptn, 'insert+1c')
        if not pos:
            return
        last = [int(v) for v in pos.split('.')]
        last[1] += len(ptn)
        last = '.'.join([str(v) for v in last])
        text.tag_add('found', pos, last)
        text.see(pos)
        text.mark_set('insert', pos)
        pass

    def do_modified(pos):
        if text.edit_modified():
            status_text.set('Modified')
            bt_save['state'] = 'normal'
            pass
        pass

    do_search.doing = False

    window = tk.Tk(className='DeepBook')
    window.wm_title('DeepBook')

    window.rowconfigure(0, minsize=800, weight=1)
    window.columnconfigure(1, minsize=800, weight=1)

    text = ScrolledText(window)
    fr_buttons = tk.Frame(window)
    bt_save = tk.Button(fr_buttons, text="Save", command=handle_save)

    bt_save.grid(row=0, column=0)

    fr_buttons.grid(row=0, column=0, sticky="ns")
    text.grid(row=0, column=1, sticky="nsew")
    status_text = tk.StringVar()
    status_text.set('Updated')
    status = tk.Label(window, font=font.Font(size=7), foreground='grey', textvariable=status_text)
    status.grid(row=1, column=0, pady=3)

    try:
        fo = open('deepbook.gpg', 'br')
        cipher = fo.read()
        fo.close()
        plaintext = decrypt(cipher, enc_key).decode('utf-8')
        text.insert('1.0', plaintext)
        text.edit_modified(False)
    except:
        pass

    text.tag_config('found', background='pink')

    search_entry = tk.Entry(window, font=font.Font(size=7))

    text.bind('<Control-KeyPress-s>', func=do_search)
    text.bind('<KeyRelease>', func=do_modified)
    bt_save['state'] = 'disabled'
    search_entry.bind('<Control-KeyPress-s>', func=do_search_next)
    search_entry.bind('<Escape>', func=stop_search)
    search_entry.bind('<KeyRelease>', func=do_search_cont)
    window.mainloop()
    pass

parser = argparse.ArgumentParser(description='DeepBook is a simple encrypted notebook')
parser.add_argument('--key', dest='key', help='Key ID for encryption (check: gpg -K)')
args = parser.parse_args()

if not args.key:
    ekeys = get_gpg_enc_keys()
    enc_key = ekeys[0]
else:
    enc_key = args.key
    pass

run_gui()
