#import mysql.connector
import numpy as np
import time
import pickle
from pymongo import MongoClient
import pandas as pd
#conn = mysql.connector.connect(user='root', password='root', database='zdb')
# 1.dp_tr: transient delta p
# 2.dp_t: transient delta t for p
# 3.dq_tr: transient delta q
# 4.dq_t: transient delta t for q
# 5.du_tr: transient delta u
# 6.du_t: transient delta t for u
# 7.di_tr: transient delta i
# 8.di_t: transient delta t for i
# 9.dp_s: stable delta p
# 10.dq_s: stable delta q
# 11.du_s: stable delta u
# 12.di_s: stable delta i
# 13.dp_dq: delta p over delta q
# 14.first_h: first harmonic
# 15.third_h: third harmonic
# 16.fifth_h: fifth harmonic
# 18.demi: delta emi


client = MongoClient()
db = client.nilm

def saveRaw2mdb(db,data):
    result = db.rawData.insert_one(
    {
        "rawData":pickle.dumps(data),
        "activePower":float(np.array(data[2]).mean()),
        "timeStamp":time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(data[6]))
#        "voltage":data[0],
#        "current":data[1],
#        "active_power":data[2], 
#        "reactive_power":data[3],
#        "harmony": pickle.dumps(data[4]), 
#        "emi": pickle.dumps(data[5]),
#        "time_stamp":pickle.dumps(data[6])
    }    
    )
   # print("finish inserting raw data into mongodb, and ID is \n", result.inserted_id)
    
def saveFeature2mdb(db,feature):
    result = db.featureData.insert_one(
    {
        "featureData":pickle.dumps(feature),
    }    
    )
    #print("finish inserting feature into mongodb, and ID is \n", result.inserted_id)
    
def saveModel2mdb(db,model):
    result = db.modelData.update_one(
    {"modelNo":1},
    {
        "$set":{
        "modelData":pickle.dumps(model),
        "modelNo":1
        },
    },
    upsert=True
    )
    print("finish update model into mongodb, and the number is ", result.matched_count)
    
def readFeature(db):
    cursor = db.featureData.find()
    for i, document in enumerate(cursor):
        if i == 0:
            feature = pickle.loads(document['featureData'])
        else:
            feature = pd.concat([feature,pickle.loads(document['featureData'])])
    return feature

def readRaw(db):
    cursor = db.rawData.find()
    for i, document in enumerate(cursor):
        if i == 0:
            data = pickle.loads(document['rawData'])
        else:
            data = pd.concat([data,pickle.loads(document['rawData'])])
    return data

def readModel(db):
    cursor = db.modelData.find({"modelNo":1})
    for i, document in enumerate(cursor):
        model = pickle.loads(document['modelData'])
    return model
#def save_raw(conn, voltage, current, active_power, reactive_power, harmony, emi, time_stamp):
#	cursor = conn.cursor()
#	f = '%Y-%m-%d %H:%M:%S'
#	time_stamp = time.strftime(f, time.gmtime(time_stamp))
#	raw_data = [pickle.dumps(voltage), pickle.dumps(current), pickle.dumps(active_power), pickle.dumps(reactive_power), pickle.dumps(harmony), time_stamp]
#	cursor.execute('insert into tb_voltage_current_collection (VCCvol, VCCcur, VCCapow, VCCrpow, VCChar, VCCtime) values (%s, %s, %s, %s, %s, %s)', raw_data)
#	cursor.execute('insert into tb_power (Pstate, VCCtime) values (%s, %s)', [float(np.array(active_power).mean()), time_stamp])# this is for web publish
#	cursor.execute('insert into tb_emi_collection (VCCEMI, VCCtime) values (%s, %s)', [pickle.dumps(emi[:10]), time_stamp])
#	conn.commit()
#	cursor.close()
#
#def save_feature(conn, dp_tr, dp_t, dq_tr, dq_t, du_tr, du_t, di_tr, di_t, dp_s, dq_s, du_s, di_s, dp_dq, first_h, third_h, fifth_h, demi, time_stamp):
#	cursor = conn.cursor()
#	f = '%Y-%m-%d %H:%M:%S'
#	time_stamp = time.strftime(f, time.gmtime(time_stamp))
#	feature_data = [dp_tr, dp_t, dq_tr, dq_t, du_tr, du_t, di_tr, di_t, dp_s, dq_s, du_s, di_s, dp_dq, first_h, third_h, fifth_h, pickle.dumps(demi), time_stamp]
#	cursor.execute('insert into tb_sample (dp_tr, dp_t, dq_tr, dq_t, du_tr, du_t, di_tr, di_t, dp_s, dq_s, du_s, di_s, dp_dq, first_h, third_h, fifth_h, demi, Stime) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', feature_data)
#	conn.commit()
#	cursor.close()