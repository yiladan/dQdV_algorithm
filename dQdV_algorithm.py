import pandas as pd
import matplotlib.pyplot as plt
import os
import time
import numpy as np


        
def df_process(df):                          # 数据表格处理
    df = df.copy()
    df.reset_index(inplace=True)
    df.drop(['index'], axis=1, inplace=True)
    df = df[df['工步号'] == 4]

    pd.to_datetime(df['系统记录时间'])
    df_sum = df.copy()
    df_sum.drop_duplicates('系统记录时间',keep='first',inplace=True)
    df_sum.index=df_sum['系统记录时间']

    return df_sum


def interf_value(df, str='辅助电压1(V)', X_1=3.35, X_2=3.45):
    data = df.copy()
    data.drop_duplicates(str,keep='last',inplace=True)             # 删除重复数据
    
    if data.iloc[:,4].size <2:                                       # 处理报错
        interp = 0
        max_value = 0
    else:
        df_dQ = np.gradient(data.iloc[:,4])                       # 产生array数组
        df_dV = np.gradient(data[str])
        df_dQdV = df_dQ/df_dV
        max_value = max(df_dQdV)
    
        df3 = np.where((data[str] >= X_1) & (data[str] <= X_2))          # 计算积分区间
        df4 = data[str][data[str].between(X_1, X_2)]
        df5 = df_dQdV[df3]
    
        interp = 0
        for i in range(len(df4)-1):
            interp += (df5[i+1]+df5[i])*(df4[i+1]-df4[i])/2
    
        # if df3[0].size == 0:                                                # 判断出现问题数据时，删掉
        #     interp = 0
        # else:    
        #     interp = interp - (df_dQdV[df3[0][-1]]+df_dQdV[df3[0][0]])*(X_2-X_1)/2         # 减去积分区域底座
        
    return interp, max_value

# TODO 返回值是积分列表
def all_calculate(df):
    df_test = pd.DataFrame(None, columns=df.columns)
    df_values = pd.DataFrame(None, columns=df.columns[-12:])
    k = 1                                                                                         # k 用来指示数据段数
    for i in range(len(df)-1):
    
        sr = pd.DataFrame(None, index=[str(k)],  columns = df.columns[-12:])
        if (df['系统记录时间'][i+1]-df['系统记录时间'][i]).seconds < 100:
            df_test = pd.concat([df_test,  pd.DataFrame(df.iloc[i,:]).T])               # 合并同一次充电数据
        else:
            for j in range(12):
                n = interf_value(df_test, str='{}'.format(df.columns[-12:][j]), X_1=3.35, X_2=3.45)[0]
                sr.iloc[:,j] = n
            df_values = pd.concat([df_values, sr])
            df_test = pd.DataFrame(None, columns=df.columns)
            k = k+1  
    df_values = df_values[df_values!=0].dropna()
    return df_values



def interf_value_maxrange(df, str_V='辅助电压1(V)', range_max = 0.1):
    data = df.copy()
    data.drop_duplicates(str_V,keep='last',inplace=True)             # 删除重复数据
    
    if data.iloc[:,4].size <2:                                       # 处理报错
        interp = 0
        max_value = 0
        max_index1 = 0
    else:
        df_dQ = np.gradient(data.iloc[:,4])                       # 产生array数组
        df_dV = np.gradient(data[str_V])
        df_dQdV = df_dQ/df_dV
        max_value = max(df_dQdV)
        max_index = np.argmax(df_dQdV)
        X_1 = data[str_V][max_index] - range_max/2
        X_2 = data[str_V][max_index] + range_max/2
        max_index1 = data[str_V][max_index]                            # 最大值对应的电压
    
        df3 = np.where((data[str_V] >= X_1) & (data[str_V] <= X_2))          # 计算积分区间
        df4 = data[str_V][data[str_V].between(X_1, X_2)]
        df5 = df_dQdV[df3]
    
        interp = 0
        for i in range(len(df4)-1):
            interp += (df5[i+1]+df5[i])*(df4[i+1]-df4[i])/2
    
        # if df3[0].size == 0:                                                # 判断出现问题数据时，删掉
        #     interp = 0
        # else:    
        #     interp = interp - (df_dQdV[df3[0][-1]]+df_dQdV[df3[0][0]])*(X_2-X_1)/2         # 减去积分区域底座
        
    return interp, max_value, max_index1

# TODO 返回值是积分列表、最大值列表和最大值对应电压列表
def all_calculate_maxrange(df):
    df_test = pd.DataFrame(None, columns=df.columns)
    df_values = pd.DataFrame(None, columns=df.columns[-12:])
    df_max = pd.DataFrame(None, columns=df.columns[-12:])
    df_maxindex = pd.DataFrame(None, columns=df.columns[-12:])
    
    k = 1                                                                                         # k 用来指示数据段数
    for i in range(len(df)-1):
    
        sr = pd.DataFrame(None, index=[str(k)],  columns = df.columns[-12:])
        sr_max = pd.DataFrame(None, index=[str(k)],  columns = df.columns[-12:])
        sr_maxindex = pd.DataFrame(None, index=[str(k)],  columns = df.columns[-12:])
        if (df['系统记录时间'][i+1]-df['系统记录时间'][i]).seconds < 10:
            df_test = pd.concat([df_test,  pd.DataFrame(df.iloc[i,:]).T])               # 合并同一次充电数据
            
        else:
            for j in range(12):
                n, o, p = interf_value_maxrange(df_test, str_V='{}'.format(df.columns[-12:][j]), range_max = 0.1)
                sr.iloc[:,j] = n
                sr_max.iloc[:,j] = o
                sr_maxindex.iloc[:,j] = p
            df_values = pd.concat([df_values, sr])
            df_max = pd.concat([df_max, sr_max])
            df_maxindex = pd.concat([df_maxindex, sr_maxindex])
            df_test = pd.DataFrame(None, columns=df.columns)
            k = k+1  
    # df_values = df_values[df_values!=0].dropna()
    return df_values, df_max, df_maxindex