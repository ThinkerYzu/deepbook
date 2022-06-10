import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import os
import subprocess

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
        last = [int(v) for v in pos.split('.')]
        last[1] += len(ptn)
        last = '.'.join([str(v) for v in last])
        text.tag_add('found', pos, last)
        text.see(pos)
        text.mark_set('insert', pos)
        pass

    do_search.doing = False

    window = tk.Tk()
    window.title("DeepBook")

    window.rowconfigure(0, minsize=800, weight=1)
    window.columnconfigure(1, minsize=800, weight=1)

    text = ScrolledText(window)
    fr_buttons = tk.Frame(window)
    bt_save = tk.Button(fr_buttons, text="Save", command=handle_save)

    bt_save.grid(row=0, column=0)

    fr_buttons.grid(row=0, column=0, sticky="ns")
    text.grid(row=0, column=1, sticky="nsew")

    try:
        fo = open('deepbook.gpg', 'br')
        cipher = fo.read()
        fo.close()
        plaintext = decrypt(cipher, enc_key).decode('utf-8')
        text.insert('1.0', plaintext)
    except:
        pass

    text.tag_config('found', background='pink')

    search_entry = tk.Entry(window)

    text.bind('<Control-KeyPress-s>', func=do_search)
    search_entry.bind('<Control-KeyPress-s>', func=do_search_next)
    search_entry.bind('<Escape>', func=stop_search)
    search_entry.bind('<KeyRelease>', func=do_search_cont)
    window.mainloop()
    pass

ekeys = get_gpg_enc_keys()
enc_key = ekeys[0]

run_gui()
