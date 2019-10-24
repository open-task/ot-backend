from peewee import *

database = MySQLDatabase('kovan3', **{'host': 'localhost', 'password': 'rknl20190919ro', 'charset': 'utf8', 'use_unicode': True, 'user': 'ro'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Accept(BaseModel):
    block = IntegerField(null=True)
    solution_id = CharField(null=True)
    tx = CharField(null=True, unique=True)
    txtime = CharField(null=True)
    updatetime = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)

    class Meta:
        table_name = 'accept'

class Config(BaseModel):
    k = CharField(primary_key=True)
    updatetime = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)
    v = CharField(null=True)

    class Meta:
        table_name = 'config'

class Confirm(BaseModel):
    arbitration_id = CharField(null=True)
    block = IntegerField(null=True)
    solution_id = CharField(null=True)
    tx = CharField(null=True)
    txtime = CharField(null=True)
    updatetime = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)

    class Meta:
        table_name = 'confirm'

class Mission(BaseModel):
    block = IntegerField(null=True)
    context = CharField(null=True)
    filter = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    mission_id = CharField(null=True)
    publisher = CharField(null=True)
    reward = DecimalField(null=True)
    solution_num = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    solved = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    tx = CharField(null=True, unique=True)
    txtime = CharField(null=True)
    updatetime = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)

    class Meta:
        table_name = 'mission'

class Reject(BaseModel):
    block = IntegerField(null=True)
    solution_id = CharField(null=True)
    tx = CharField(null=True, unique=True)
    txtime = CharField(null=True)
    updatetime = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)

    class Meta:
        table_name = 'reject'

class Solution(BaseModel):
    block = IntegerField(null=True)
    context = CharField(null=True)
    filter = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    mission_id = CharField(null=True)
    solution_id = CharField(null=True)
    solver = CharField(null=True)
    status = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    tx = CharField(null=True, unique=True)
    txtime = CharField(null=True)
    updatetime = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)

    class Meta:
        table_name = 'solution'

