# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 11:12:54 2024

@author: lgxsv2
"""
import os 
find the folder and put into os.chdir()
from locateImage import locateImage


fn_wm = [r"D:\RT_temperaturePrivate\Data\imagery\Planet\m20Masks\Rhone_reach_6_20220308.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\m20Masks\Rhone_reach_6_20220418.tif",r"D:\RT_temperaturePrivate\Data\imagery\Planet\m20Masks\Rhone_reach_6_20220512.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\m20Masks\Rhone_reach_6_20220620.tif",r"D:\RT_temperaturePrivate\Data\imagery\Planet\m20Masks\Rhone_reach_6_20220708.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\m20Masks\Rhone_reach_6_20220816.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\m20Masks\Rhone_reach_6_20221018.tif"]
fn_raw=[r"D:\RT_temperaturePrivate\Data\imagery\Planet\zip\Rhone_reach_6\20220308\5ea59983-3358-4df1-8cbb-bdb80a0c8fb1\composite.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\zip\Rhone_reach_6\20220418\cd7b3fcb-f7d7-41ed-9285-2770a63e116d\composite.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\zip\Rhone_reach_6\20220512\cc91dcc5-e820-4d0e-9396-99723cfbeecf\composite.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\zip\Rhone_reach_6\20220620\115e2c1f-9884-48d5-b30e-c264c1f8c83b\composite.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\zip\Rhone_reach_6\20220708\092a832a-bcb1-4e9c-afc2-8e49d958fd54\PSScene\20220708_101026_06_248e_3B_AnalyticMS_SR_clip.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\zip\Rhone_reach_6\20220816\5be2b946-e249-4fea-bb94-8ccb480a8052\composite.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\zip\Rhone_reach_6\20221018\25534a8f-f621-4e84-b589-1e603d326772\composite.tif"]
out = [r"D:\RT_temperaturePrivate\Data\imagery\Planet\locatedMasks\Rhone_reach_6_20220308.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\locatedMasks\Rhone_reach_6_20220418.tif",r"D:\RT_temperaturePrivate\Data\imagery\Planet\locatedMasks\Rhone_reach_6_20220512.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\locatedMasks\Rhone_reach_6_20220620.tif",r"D:\RT_temperaturePrivate\Data\imagery\Planet\locatedMasks\Rhone_reach_6_20220708.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\locatedMasks\Rhone_reach_6_20220816.tif", r"D:\RT_temperaturePrivate\Data\imagery\Planet\locatedMasks\Rhone_reach_6_20221018.tif"]
for i in range(len(fn_wm)):
    locateImage(fn_wm[i], fn_raw[i], out[i])