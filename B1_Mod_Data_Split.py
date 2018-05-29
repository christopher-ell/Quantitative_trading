# -*- coding: utf-8 -*-
"""
Splits data into three parts Training, Validation and Testing
"""

def ml_data_split(data):
    
    import pandas as pd

    train_data = data[0:int(len(data)*0.6)]

    val_data = data[int(len(data)*0.6):int(len(data)*0.8)]

    test_data = data[int(len(data)*0.8):]
    
    return train_data, val_data, test_data


#train, val, test = ml_data_split(data)