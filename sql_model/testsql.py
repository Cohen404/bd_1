from sql_model.tb_result import Result
from util.db_util import SessionClass
from sql_model.tb_data import Data


session = SessionClass()
kk = session.query(Data).filter(Data.upload_user == 1).all()
session.close()
info = []
for item in kk:
    info.append([item.id, item.personnel_id, item.data_path, item.upload_user, item.personnel_name])