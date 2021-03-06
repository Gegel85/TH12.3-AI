# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 12:03:42 2018

@author: 北海若
"""

import game_utils as gu
import time
import os
import subprocess
import psutil


# Config for Auto Replay to Data
AUTO = True
BEGIN = 0
END = 5518
REPLAY_PATH = r"D:\AI_DataSet\DATASET_REMI"
EXE_PATH = r"D:\AI_DataSet\TH123\th123\th123.exe"
# To be automatic, SWRSToys & ReplayDnD should be enabled
# with Ver = 1.10 and filename Starting with Index_

OUTPUT_PATH = "D:/AI_DataSet/DATASET_REMI_TXT"


def replay_to_data(cancel_on_title_met=False):
    print("Wait For Battle Detection...")
    time_begin = time.time()
    while (gu.fetch_status() not in [0x05, 0x0e]
            or gu.fetch_wincnt()[0] > 256
            or gu.fetch_wincnt()[1] > 256):
        if gu.fetch_status() == 0x02 and cancel_on_title_met:
            th123.terminate()
            return
        if not psth123.is_running():
            return
        if time.time() > time_begin + 30.0:
            return
        time.sleep(0.5)
    print("Battle Detected!")
    gu.update_base()
    hp1, hp2 = 10000, 10000
    data = []
    f = open(OUTPUT_PATH + "/" + str(int(time.time() * 1000)) + ".txt", "w+")
    f.write("P1: ")
    f.write(str(gu.fetch_char()[0]))
    f.write(", ")
    f.write("P2: ")
    f.write(str(gu.fetch_char()[1]))
    f.write("\n")
    while (psth123.is_running()
           and hp1 > 0 and hp2 > 0
           and gu.fetch_status() in [0x05, 0x0e]):
        hp1, hp2 = gu.fetch_hp()
        key1, key2 = gu.fetch_operation()
        pos1x, pos2x = gu.fetch_posx()
        pos1y, pos2y = gu.fetch_posy()
        act1, act2 = gu.fetch_action()
        data.append(hp1)
        data.append(round(pos1x, 4))
        data.append(round(pos1y, 4))
        data.append(key1)
        data.append(act1)
        data.append(hp2)
        data.append(round(pos2x, 4))
        data.append(round(pos2y, 4))
        data.append(key2)
        data.append(act2)
        time.sleep(1.0 / 30.0)
    if hp1 <= 0 and hp2 > 0:
        f.write("P2 Won.")
    elif hp2 <= 0 and hp1 > 0:
        f.write("P1 Won.")
    elif hp2 <= 0 and hp1 <= 0:
        f.write("Tie.")
    else:
        f.write("Interrupted Battle.")
    f.write("\n# P1 HP P1 Pos X P1 Pos Y P1 Key P1 Act; P2 etc.\n")
    if len(data) == 0:
        f.close()
        return
    for x in range(0, len(data), 10):
        for i in range(x, x + 5):
            f.write(str(data[i]))
            if i != x + 4:
                f.write(" ")
        f.write("; ")
        for i in range(x + 5, x + 10):
            f.write(str(data[i]))
            if i != x + 9:
                f.write(" ")
        f.write("\n")
    f.close()
    if gu.fetch_wincnt()[0] < 2 and gu.fetch_wincnt()[1] < 2:
        while hp1 <= 0 or hp2 <= 0:
            time.sleep(0.5)
            hp1, hp2 = gu.fetch_hp()
            if (gu.fetch_status() not in [0x05, 0x0e]
                    or not psth123.is_running()):
                return
        replay_to_data(cancel_on_title_met)


if __name__ == "__main__":
    print("Start From:")
    BEGIN = int(input())
    print("End With:")
    END = int(input())
    if not AUTO:
        replay_to_data()
    else:
        ds = []
        for r, d, f in os.walk(REPLAY_PATH):
            for n in f:
                ds.append((r, n))
        for i in range(len(ds)):
            ds[i] = (int(ds[i][1].split("_")[0]), ds[i][0], ds[i][1])
        ds = sorted(ds)
        for d in ds:
            if d[0] < BEGIN or d[0] > END:
                continue
            stinfo = subprocess.STARTUPINFO()
            stinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
            stinfo.wShowWindow = subprocess.SW_HIDE
            gu.update_proc()
            th123 = subprocess.Popen([EXE_PATH, os.path.join(d[1], d[2])],
                                     startupinfo=stinfo)
            psth123 = psutil.Process(th123.pid)
            print("Current:", d[0],
                  d[2].encode("gbk", errors='ignore').decode('gbk'))
            gu.update_proc_with_pid(th123.pid)
            replay_to_data(True)
            th123.terminate()
            time_begin = time.time()
            while psth123.is_running():
                if time.time() > time_begin + 30.0:
                    break
                time.sleep(1.0)
