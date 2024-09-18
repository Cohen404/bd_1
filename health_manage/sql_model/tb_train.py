import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base


class Train(declarative_base()):
    __tablename__ = 'tb_train'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    model_name = Column(String(255), comment='模型名称')
    model_path = Column(String(255), comment='模型路径')
    lr = Column(Float, comment='学习率')
    epoch = Column(Integer, comment='训练次数')
    cross_validation = Column(Integer, comment='交叉验证次数')
    result_img_path = Column(String(255), comment='结果图片路径')
    cv_acc = Column(Float, comment='交叉验证准确率')
    test_acc = Column(Float, comment='测试准确率')
    test_time = Column(DateTime, default=datetime.datetime.now(), comment='测试时间')
    import_time = Column(DateTime, default=datetime.datetime.now(), comment='导入时间')
    user_id = Column(Integer, default=1, comment='导入模型用户id')
    use = Column(Integer,default=0, comment='是否使用模型')
    data_id = Column(Integer, comment='训练数据的id号，关联data表')
