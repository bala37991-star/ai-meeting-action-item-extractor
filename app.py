import json, re
from datetime import date, timedelta
import pandas as pd
import streamlit as st

try:
    from groq import Groq
except ImportError:
    Groq = None

st.set_page_config(page_title="AI Meeting Action-Item Extractor", page_icon="📝", layout="wide")
st.title("📝 AI Meeting Action-Item Extractor")
st.write("Convert meeting transcripts into structured action items with task, owner, deadline, status, and confidence.")
st.info("Review all extracted items before using them as official meeting records. Do not upload confidential transcripts without approval.")

def deadline(text):
    today=date.today(); t=text.lower()
    if "tomorrow" in t: return (today+timedelta(days=1)).isoformat()
    if "today" in t or "eod" in t: return today.isoformat()
    if "next week" in t: return (today+timedelta(days=7)).isoformat()
    for i,day in enumerate(["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]):
        if re.search(r"\b"+day+r"\b",t):
            delta=(i-today.weekday())%7 or 7
            return (today+timedelta(days=delta)).isoformat()
    m=re.search(r"\bby\s+(\d{4}-\d{2}-\d{2})",t)
    if m:
        try: return date.fromisoformat(m.group(1)).isoformat()
        except ValueError: pass
    m=re.search(r"\bby\s+(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b",t)
    if m:
        a,b,y=m.groups(); year=int(y) if y else today.year
        if year<100: year+=2000
        for month,day in [(int(b),int(a)),(int(a),int(b))]:
            try: return date(year,month,day).isoformat()
            except ValueError: pass
    return "Not specified"

def rule_extract(text):
    out=[]; seen=set()
    for raw in text.splitlines():
        line=raw.strip()
        if not line: continue
        m=re.match(r"^([A-Z][A-Za-z0-9 .'-]{0,30}):\s*(.*)$",line)
        owner=m.group(1).strip() if m else "Unassigned"
        sent=m.group(2).strip() if m else line
        assigned=re.match(r"^([A-Z][A-Za-z .'-]{1,25})\s+(will|shall|must|should|needs to|need to)\s+(.+)",sent,re.I)
        if assigned: owner=assigned.group(1).strip()
        if not re.search(r"\b(will|shall|must|should|need to|needs to|follow up|action item|send|prepare|update|review|schedule|create|share)\b",sent,re.I): continue
        task=re.sub(r"^.*?:\s*","",sent)
        task=re.sub(r"^(I|we)\s+(will|shall|must|should|need to|needs to)\s+","",task,flags=re.I)
        task=re.sub(r"^(will|shall|must|should|need to|needs to)\s+","",task,flags=re.I)
        task=re.sub(r"\s+by\s+.+$","",task,flags=re.I).strip(" .;")
        if len(task.split())<2: continue
        key=re.sub(r"\W","",task.lower())
        if key in seen: continue
        seen.add(key); due=deadline(sent)
        conf=.78 if owner!="Unassigned" else .56
        if due!="Not specified": conf=min(.94,conf+.08)
        out.append({"Task":task[:1].upper()+task[1:],"Owner":owner,"Deadline":due,"Status":"Open",
                    "Confidence":conf,"Source":"Rule-based NLP",
                    "Review":"Yes" if owner=="Unassigned" or due=="Not specified" else "No"})
    return out

def llm_extract(text,key):
    if Groq is None: raise RuntimeError("Groq package missing; install requirements.txt.")
    client=Groq(api_key=key)
    prompt=("Extract only explicit action items. Return JSON with action_items array; each object has task, owner, "
            "deadline (YYYY-MM-DD or Not specified), status (Open), confidence (0-1). Never invent details. "
            "Resolve relative dates using "+date.today().isoformat()+".\nTRANSCRIPT:\n"+text)
    response=client.chat.completions.create(model="llama-3.3-70b-versatile",temperature=0.1,
        response_format={"type":"json_object"},
        messages=[{"role":"system","content":"Extract structured meeting tasks. Output JSON only."},
                  {"role":"user","content":prompt}])
    data=json.loads(response.choices[0].message.content); out=[]
    for x in data.get("action_items",[]):
        task=str(x.get("task","")).strip()
        if not task: continue
        owner=str(x.get("owner","Unassigned")).strip() or "Unassigned"
        due=str(x.get("deadline","Not specified"))
        try:
            if due.lower()!="not specified": due=date.fromisoformat(due).isoformat()
            else: due="Not specified"
        except ValueError: due="Not specified"
        try: conf=max(0,min(1,float(x.get("confidence",.7))))
        except: conf=.7
        out.append({"Task":task,"Owner":owner,"Deadline":due,"Status":"Open","Confidence":conf,
                    "Source":"LLM (Groq)","Review":"Yes" if owner.lower()=="unassigned" or due=="Not specified" or conf<.7 else "No"})
    return out

def validate(df):
    if df.empty:return df
    df=df.copy()
    for i,r in df.iterrows():
        owner=str(r.get("Owner","Unassigned")); due=str(r.get("Deadline","Not specified")); review="No"
        if not owner.strip() or owner.lower()=="unassigned": review="Yes"
        if not due.strip() or due.lower()=="not specified": review="Yes"
        else:
            try:
                parsed=date.fromisoformat(due)
                if parsed<date.today(): review="Yes"
            except ValueError: review="Yes"
        if float(r.get("Confidence",0))<.7: review="Yes"
        df.at[i,"Review"]=review
    return df

st.sidebar.header("Extraction mode")
mode=st.sidebar.radio("Choose method",["Rule-based NLP","LLM (Groq API)"])
st.sidebar.caption("LLM mode requires your own API key in Streamlit Secrets. Default mode works without a key.")
up=st.file_uploader("Upload transcript (.txt or .docx)",type=["txt","docx"])
uploaded_text=""
if up:
    if up.name.lower().endswith(".txt"): uploaded_text=up.getvalue().decode("utf-8",errors="replace")
    else:
        try:
            from docx import Document
            uploaded_text="\n".join(p.text for p in Document(up).paragraphs)
        except Exception as e: st.error(f"Could not read DOCX: {e}")
transcript=st.text_area("Or paste transcript",value=uploaded_text,height=230,
    placeholder="Maya: I will send the revised proposal by Friday.\nArun: I will schedule the review tomorrow.")
if st.button("Extract action items",type="primary"):
    if not transcript.strip(): st.warning("Upload or paste a transcript first.")
    else:
        try:
            with st.spinner("Extracting action items..."):
                if mode=="LLM (Groq API)":
                    key=st.secrets.get("GROQ_API_KEY","")
                    if not key: raise RuntimeError("GROQ_API_KEY is not configured in app Secrets.")
                    items=llm_extract(transcript,key)
                else: items=rule_extract(transcript)
            st.session_state["action_items"] = validate(pd.DataFrame(items))
            st.session_state.transcript=transcript
        except Exception as e: st.error(str(e))

if "action_items" in st.session_state:
    df = st.session_state["action_items"]
    st.subheader("Extracted action items")
    if df.empty: st.warning("No explicit action items found. Try sentences with clear commitments.")
    else:
        a,b,c,d=st.columns(4)
        a.metric("Items",len(df)); b.metric("Unassigned",int((df.Owner=="Unassigned").sum()))
        c.metric("No deadline",int((df.Deadline=="Not specified").sum())); d.metric("Needs review",int((df.Review=="Yes").sum()))
        edited=st.data_editor(df,use_container_width=True,hide_index=True,num_rows="dynamic",
            column_config={"Confidence":st.column_config.NumberColumn(min_value=0,max_value=1,step=.01,format="%.2f"),
                           "Source":st.column_config.TextColumn(disabled=True),"Review":st.column_config.TextColumn(disabled=True)})
        edited = validate(edited)
        st.session_state["action_items"] = edited
        x,y=st.columns(2)
        x.download_button("Download CSV",edited.to_csv(index=False).encode(),"meeting_action_items.csv","text/csv",use_container_width=True)
        y.download_button("Download JSON",edited.to_json(orient="records",indent=2).encode(),"meeting_action_items.json","application/json",use_container_width=True)
        st.caption("Confidence is an estimate, not a calibrated probability. Check and correct the output.")
    with st.expander("View source transcript"): st.text(st.session_state.get("transcript",""))

sample="""Maya: I will send the revised project proposal by Friday.
Arun: I will schedule the client review tomorrow.
Priya: I need to update the risk register by 2026-10-08.
Maya: Arun will share the meeting notes by next week.
Team: We discussed the budget and agreed to revisit it later."""
with st.expander("Sample transcript"):
    st.code(sample)
    if st.button("Load sample"):
        st.session_state.demo=sample
        st.rerun()
if "demo" in st.session_state:
    st.caption("Sample loaded below; copy it into the transcript field to analyze.")
    st.code(st.session_state.demo)
st.divider()
st.caption("AI Capstone demonstration • Human verification recommended")
