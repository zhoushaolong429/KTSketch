cmake_minimum_required(VERSION 3.21)
project(KT_1_0)

set(CMAKE_CXX_STANDARD 14)

add_executable(KT_1_0 main.cpp basicDataStruct/Bitmap.h hashFunc/hash.h ../newtest/basicDataStruct/FreeBS_SSD_h2b.h sketch/KTSketch.h basicDataStruct/BloomFilter.h basicDataStruct/CountMin.h sketch/BFCM.h basicDataStruct/Summary2.h basicDataStruct/FreeBS_SSD_Linklist.h sketch/VHLL.h RealExp.h)
