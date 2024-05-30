import streamlit as st
import firebase_admin
import pandas as pd
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

#파이어 베이스 경로 및 권한 설정
cred = credentials.Certificate("mykey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred,{
    "databaseURL" : "myfirebaseURL"
    })

#넓은 화면으로 설정
st.set_page_config(layout="wide")
#제목
st.title("대시보드")

#데이터베이스 경로 설정
db = firestore.client()
doc_ref0 = db.collection("User").document("TvAqbRIHDRNqS8GvqmLzFQyLFb93").collection("crop")

crops  = doc_ref0.get()
cropname : list = []
for crop in crops:
    cropname.append(crop.id)

#셀렉트 박스에서 식물 선택
choice = st.selectbox("식물 선택",cropname)
st.write(choice)

#선택된 식물의 정보 db에서 가져옴
doc_ref = db.collection("User").document("TvAqbRIHDRNqS8GvqmLzFQyLFb93").collection("crop").document(choice)
docsd = doc_ref.get(field_paths={"d"})
docst = doc_ref.get(field_paths={"t"})
docsh = doc_ref.get(field_paths={"h"})
docsm = doc_ref.get(field_paths={"m"})
mapd = docsd.to_dict()
mapt = docst.to_dict()
maph = docsh.to_dict()
mapm = docsm.to_dict()
vdlist : list = []
vtlist : list = []
vhlist : list = []
vmlist : list = []
ttlist : list = []
#가져온 정보 분리
for d in mapd.values():
    for d2 in d:
        vdlist.append(d2[0:d2.find("*")])
        ttlist.append(d2[d2.find("*")+1:])
for t in mapt.values():
    for t2 in t:
        vtlist.append(t2[0:t2.find("*")])
for h in maph.values():
    for h2 in h:
        vhlist.append(h2[0:h2.find("*")])
for m in mapm.values():
    for m2 in m:
        vmlist.append(m2[0:m2.find("*")])

#string으로 되어있는 값을 float으로 변경
vdlist = list(map(float, vdlist))
vhlist = list(map(float, vhlist))
vmlist = list(map(float, vmlist))
vtlist = list(map(float, vtlist))

#데이터프레임 생성
df = pd.DataFrame({'D' : vdlist, 'H' : vhlist, 'M' : vmlist, 'T' : vtlist}, index = ttlist)
#생성된 데이터 프레임 출력
st.dataframe(df)
#시간 정보를 넣은 데이터 프레임 재생성
df = pd.DataFrame({'D' : vdlist, 'H' : vhlist, 'M' : vmlist, 'T' : vtlist, 'Date' : ttlist})

#컬럼 1:1:1:1 비율로 생성
col1,col2,col3,col4 = st.columns([1,1,1,1])

#각 컬럼마다 메트릭 넣음
col1.metric(label="Darkness", value=vdlist[-1], delta=(float(vdlist[-1])-float(vdlist[-2])))
col2.metric(label="Humidity", value=vhlist[-1], delta=(float(vhlist[-1])-float(vhlist[-2])))
col3.metric(label="Moisture", value=vmlist[-1], delta=(float(vmlist[-1])-float(vmlist[-2])))
col4.metric(label="Temperature", value=vtlist[-1], delta=(float(vtlist[-1])-float(vtlist[-2])))

#위에서 생성한 데이터 프레임으로 라인 차트 출력
st.line_chart(df,x='Date')