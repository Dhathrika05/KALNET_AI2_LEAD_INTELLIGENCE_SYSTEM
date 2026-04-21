from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from typing import Optional
app=FastAPI()


pd_data=pd.DataFrame(
    {
        "id":[1,2,3,4,5],
        "Name":["school1","school2","school3","school4","school5"],
        "state":["Telangana","andhrapradesh","maharastra","Telangana","kerla"],
        "school_type":["Governament","Private","Private","Governament","Private"],
        "tier":["Tier1","Tier2","Tier3","Tier4","Tier5"],
        "has_email":[True,False,True,False,True]

    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

class Data(BaseModel):
    id:Optional[int]=None
    search:Optional[str]=None
    state:Optional[str]=None
    school_type:Optional[str]=None
    tier:Optional[str]=None
    has_email:Optional[bool]=None


@app.post("/leads")
def get_leads(data:Data):

    ans=pd_data
    if data.search:
        ans=ans[ans["Name"]==data.search] #ans=data[data["Name"].str.contains(data.search,case=False)]
    if data.state:
        ans=ans[ans["state"]==data.state]
    if data.school_type:
        ans=ans[ans["school_type"]==data.type]
    if data.tier:
        ans=ans[ans["tier"]==data.tier]
    if data.has_email:
        ans=ans[ans["has_email"]==data.has_email]
    

    return {"message":ans.to_dict(orient="records")}
    

app.get("/lead/{id}")
def get_lead(id:int):
    ans=pd_data[pd_data['id'].astype(int)==id]
    if ans.empty:
        return {"message":"No Record Found"}
    else:
        return {"message":ans.to_dict(orient="records")}    


