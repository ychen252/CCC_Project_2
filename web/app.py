"""
Team 47
Guoning Qi 1022700
Longxuan Xu 963988
Hongju Xia 957832
Yihan Chen 1060155
Yuxuan Chen 1035457
"""


import re
import xlrd
from flask import Flask, render_template
from pyecharts import options as opts
from pyecharts.charts import Bar, Geo, Map, Line
from pyecharts.charts import Bar
from pyecharts.faker import Faker
import couchdb

app = Flask(__name__)


def getdb(name):
    couch = couchdb.Server("http://admin:123456@172.26.133.148:5984/")
    db = couch[name]
    return db


def getaurin():
    workbook = xlrd.open_workbook('aurin.xls')
    sheet = workbook.sheets()[0]
    i = 1
    aurin = []
    for i in range(1, 302):
        suburb = sheet.cell(i, 6).value
        density = sheet.cell(i, 23).value
        income = sheet.cell(i, 27).value
        data = {'suburb': suburb, 'density': density, 'income': income}
        aurin.append(data)
    res = sorted(aurin, key=lambda k: k['suburb'])
    for each in res:
        pattern = r',|-|\$'
        if each['income'] != '0':
            fincome = re.split(pattern, each['income'])
            temp = fincome[1] + fincome[2]
            temp1 = int(temp)
            each['income'] = temp1
        else:
            each['income'] = 0
    return res


def queryfood():
    db = getdb("food_twitters")
    db.__reduce__()
    list = []
    res = []
    for row in db.view('designs/agg_by_region', group=True):
        content = {}
        if row.key is not None and row.value != "":
            content['name'] = row.key['name']
            content['value'] = row.value['total']
            list.append(content)
            res = sorted(list, key=lambda k: k['name'])

    return res


def querysmoke():
    db = getdb("smoke_twitters")
    db.__reduce__()
    list = []
    res = []
    for row in db.view('designs/agg_by_region', group=True):
        content = {}
        if row.key is not None and row.value != "":
            content['name'] = row.key['name']
            content['value'] = row.value['total']
            list.append(content)
            res = sorted(list, key=lambda k: k['name'])
    return res


@app.route('/')
def index():
    return render_template('index.html')



def incomeline() -> Line:
    aurin_data = getaurin()
    food_data = queryfood()
    smoke_data = querysmoke()
    suburb = []
    food_value = []
    smoke_value = []
    aurin_income = []
    for food in food_data:
        suburb.append(food['name'])
        food_value.append(food['value'])
    for smoke in smoke_data:
        if smoke['name'] in suburb:
            smoke_value.append(smoke['value'])
    for data in aurin_data:
        if data['suburb'] in suburb:
            aurin_income.append(data['income'])
    c = (
        Line()
            .add_xaxis(suburb)
            .add_yaxis("income", aurin_income)
            .add_yaxis("food", food_value)
            .add_yaxis("smoke", smoke_value)
            .set_global_opts(title_opts=opts.TitleOpts(title="Income-Food-Smoke"))
    )
    return c


def densityline() -> Line:
    aurin_data = getaurin()
    food_data = queryfood()
    smoke_data = querysmoke()
    suburb = []
    food_value = []
    smoke_value = []
    aurin_density = []
    for food in food_data:
        suburb.append(food['name'])
        food_value.append(food['value'])
    for smoke in smoke_data:
        if smoke['name'] in suburb:
            smoke_value.append(smoke['value'])
    for data in aurin_data:
        if data['suburb'] in suburb:
            aurin_density.append(data['income'])
    c = (
        Line()
            .add_xaxis([str(food['name']) for food in food_data])
            .add_yaxis("density", [data['density'] for data in aurin_data])
            .add_yaxis("food", [data['value'] for data in food_data])
            .add_yaxis("smoke", [data['value'] for data in smoke_data])
            .set_global_opts(title_opts=opts.TitleOpts(title="Density-Food-Smoke"))
    )
    return c


@app.route('/linechart1')
def linechart():
    income = incomeline()
    density = densityline()
    return render_template('linechart1.html', income_options=income.dump_options(),
                           density_options=density.dump_options())


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)
