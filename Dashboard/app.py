import streamlit as st
import requests
import pandas as pd
st.title("DashBoard :")

st.divider()
apiurl='your_url/leads?'
formdata={}
with st.form(key="DataForm"):
    #numid=st.number_input("Search by id")
    search=st.text_input("Search Something")
    state=st.selectbox("State",[None,'Telangana','Maharastra','Banglore','chennai'])
    school_type=st.selectbox("Type",[None,"Governament","Private"])
    tier=st.selectbox("Tier",[None,"Tier 1","Tier 2","Tier 3"])
    has_email=st.checkbox("Has Email ?")
    submitted_button=st.form_submit_button(label="submit")

if  submitted_button:
    #if numid:
    #    apiurl+=f'id={numid}'
    if search:
        formdata["search"]=search
        apiurl+=f'search={search}&'
    if state:
        formdata['state']=state
        apiurl+=f'state={state}&'
    if school_type:
        formdata['school_type']=school_type
        apiurl+=f'school_type={school_type}&'
    if tier:
        formdata['tier']=tier
        apiurl+=f'tier={tier}&'
    if has_email:
        formdata['has_email']=has_email
        apiurl+=f'has_email={has_email}&'                         

    try:
        response=requests.get(apiurl,json=formdata)
        if response.status_code==200:
            data=response.json().get("message",[])
            print(data)
            if data:
                df_result = pd.DataFrame(data)
                st.success(f"found {len(data)}")
                st.dataframe(data)
                st.divider()
                st.bar_chart(data)
                st.divider()
                st.area_chart(data)
                st.divider()
                chart_data = pd.crosstab(df_result['tier'], df_result['school_type'])
                st.bar_chart(chart_data)
            else:
                st.warning("Nothing found")
        else:
            st.error(f"error code {response.status_code}")        
    except Exception as e:
        st.error(f"could not connect to api : {e}")
st.divider()