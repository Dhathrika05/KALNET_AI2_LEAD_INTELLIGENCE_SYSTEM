import streamlit as st
import requests
import pandas as pd

st.title("DashBoard :")

st.divider()

apiurl='http://127.0.0.1:8000/leads?'

formdata={}

with st.form(key="DataForm"):

    search=st.text_input("Search Something")

    state=st.selectbox(
        "State",
        [None,'Telangana','Maharashtra','Andhra Pradesh','Tamil Nadu']
    )

    school_type=st.selectbox(
        "Type",
        [None,"Govt","Private"]
    )

    tier=st.selectbox(
        "Tier",
        [None,"Tier1","Tier2","Tier3"]
    )

    has_email=st.checkbox("Has Email ?")

    submitted_button=st.form_submit_button(label="submit")

if submitted_button:

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

                df_result=pd.DataFrame(data)

                st.success(f"found {len(data)}")

                st.dataframe(df_result)

                st.divider()

                if 'student_count' in df_result.columns:
                    chart_df=df_result[['name','student_count']].set_index('name')
                    st.bar_chart(chart_df)

                st.divider()

                if 'student_count' in df_result.columns:
                    area_df=df_result[['name','student_count']].set_index('name')
                    st.area_chart(area_df)

                st.divider()

                if 'icp_tier' in df_result.columns and 'type' in df_result.columns:
                    chart_data=pd.crosstab(
                        df_result['icp_tier'],
                        df_result['type']
                    )
                    st.bar_chart(chart_data)

            else:
                st.warning("Nothing found")

        else:
            st.error(f"error code {response.status_code}")

    except Exception as e:
        st.error(f"could not connect to api : {e}")

st.divider()