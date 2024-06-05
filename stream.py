import streamlit as st
import firebase_admin
import pandas as pd
import json
import boto3
import altair as alt
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

#파이어 베이스 경로 및 권한 설정 
cred = credentials.Certificate("/home/ec2-user/environment/stream/mykey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred,{
    "databaseURL" : "https://console.firebase.google.com/project/cityfarmer-afb6f/firestore/databases/-default-/data/~2F?hl=ko"
    })

#넓은 화면으로 설정
st.set_page_config(layout="wide")
#제목
st.title(":blue[대시보드!]")

#데이터베이스 경로 설정
db = firestore.client()
doc_ref0 = db.collection("User").document("TvAqbRIHDRNqS8GvqmLzFQyLFb93").collection("crop")

crops  = doc_ref0.get()
cropname : list = []
for crop in crops:
    cropname.append(crop.id)

#셀렉트 박스에서 식물 선택
choice = st.selectbox("식물 선택",cropname)

#선택된 식물의 생장 기준 가져옴
doc_ref1 = db.collection("Standard").document(choice)
stand = doc_ref1.get().to_dict()
standH = stand["H"]
standT = stand["T"]
standM = stand["M"]
standard : list = []

#선택된 식물의 정보 db에서 가져옴
doc_ref = db.collection("User").document("TvAqbRIHDRNqS8GvqmLzFQyLFb93").collection("crop").document(choice)
#온도, 대기습도, 토양습도 데이터 가져옴
docst = doc_ref.get(field_paths={"t"})
docsh = doc_ref.get(field_paths={"h"})
docsm = doc_ref.get(field_paths={"m"})

mapt = docst.to_dict()
maph = docsh.to_dict()
mapm = docsm.to_dict()

vtlist : list = []
vhlist : list = []
vmlist : list = []
ttlist : list = []
#가져온 정보 분리
for t in mapt.values():
    for t2 in t:
        vtlist.append(t2[0:t2.find("*")])
        ttlist.append(t2[t2.find("*")+1:])
for h in maph.values():
    for h2 in h:
        vhlist.append(h2[0:h2.find("*")])
for m in mapm.values():
    for m2 in m:
        vmlist.append(m2[0:m2.find("*")])

#string으로 되어있는 값을 float으로 변경
vhlist = list(map(float, vhlist))
vmlist = list(map(float, vmlist))
vtlist = list(map(float, vtlist))

#데이터프레임 생성
df = pd.DataFrame({
'대기습도' : vhlist, 
'토양습도' : vmlist, 
'온도' : vtlist}, index = ttlist)
#생성된 데이터 프레임 출력
st.dataframe(df)
#시간 정보를 넣은 데이터 프레임 재생성
df = pd.DataFrame({'대기습도' : vhlist, '토양습도' : vmlist, '온도' : vtlist, '날짜' : ttlist})

#컬럼 1:1:1 비율로 생성
col1,col2,col3 = st.columns([1,1,1])

#각 컬럼마다 메트릭 넣음
col1.metric(label="대기습도", value=vhlist[-1], delta=(float(vhlist[-1])-float(vhlist[-2])))
col2.metric(label="토양습도", value=vmlist[-1], delta=(float(vmlist[-1])-float(vmlist[-2])))
col3.metric(label="온도", value=vtlist[-1], delta=(float(vtlist[-1])-float(vtlist[-2])))

#위에서 생성한 데이터 프레임으로 라인 차트 출력
#st.line_chart(df,x='날짜')

st.header('_차트에 출력할 값을_',anchor=None, help=None)
st.header('_선택하세요!_ :smile:', divider='rainbow',anchor=None, help=None)

options = st.multiselect( '직선 = 식물 생장 표준', 
                         ['대기습도', '토양습도', '온도'],
                         ['대기습도', '토양습도', '온도'])

#시간 정보와 표준 정보를 넣은 데이터 프레임 재생성
newDate : list =[]
newType : list = []
newValue : list = []
looplen = len(ttlist)
if len(options) != 0:
    for i in range(looplen):
        date = ttlist.pop(0)
        if "대기습도" in options:
            newDate.append(date)
            newType.append("대기습도")
            newValue.append(vhlist.pop(0))
            standard.append(standH)
        if "토양습도" in options:
            newDate.append(date)
            newType.append("토양습도")
            newValue.append(vmlist.pop(0))
            standard.append(standM)
        if "온도" in options:
            newDate.append(date)
            newType.append("온도")
            newValue.append(vtlist.pop(0))
            standard.append(standT)
            

#알테어 차트를 그리기 위한 데이터 프레임 재설정
df = pd.DataFrame({
    '센서값' : newValue,
    '종류' : newType, 
    '날짜' : newDate,
    '표준값' : standard
    })
base = alt.Chart(df)

line = base.mark_line(
    point=alt.OverlayMarkDef(filled=False, fill="white")
     ).encode( 
    x='날짜',y="센서값",color="종류"
)

rule = base.mark_rule().encode(
    y="표준값",
    color="종류",
    size=alt.value(2)
)

text = line.mark_text(
    align="left",
    baseline="top",
    dx=3
    ).encode(text="센서값",color=alt.value("black"))

if len(options) != 0:
    st.altair_chart(line+rule+text ,use_container_width=True)
