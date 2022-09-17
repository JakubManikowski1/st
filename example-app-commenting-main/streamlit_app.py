from datetime import datetime

import streamlit as st
from vega_datasets import data
import pandas as pd

from utils import chart, db

COMMENT_TEMPLATE_MD = """{} - {}
> {}"""

from zipfile import ZipFile
from io import BytesIO
import urllib.request as urllib2

def space(num_lines=1):
    """Adds empty lines to the Streamlit app."""
    for _ in range(num_lines):
        st.write("")


st.set_page_config(layout="centered", page_icon="💬", page_title="Commenting app")

# Data visualisation part

st.title("Commenting app")

r = urllib2.urlopen("https://info.bossa.pl/pub/ciagle/omega/omegacgl.zip").read()
files = ZipFile(BytesIO(r))
# spolka_csv = files.open("WOJAS.txt")
# spolka = pd.read_csv(spolka_csv)
# st.write(spolka)

    # spolka['Date'] = spolka['Date'].apply(lambda x: pd.to_datetime(str(x), format='%Y%m%d'))
    # chart1 = chart.get_chart(spolka)
    # st.altair_chart(chart1, use_container_width=True)

text_files = files.namelist()
text_files1 = [x for x in text_files if not x.startswith(('INTL','INTS','BNPPBK','BNPPBS','BNPPC','BNPPE','BNPPG','BNPPS','GSI','GSW','RC','UC')) ]
# filesLen = len(text_files)
filesLen1 = len(text_files1)
# st.write(filesLen)
st.write("Number of unique ISINS: ")
st.write(filesLen1)

for i in range(0, filesLen1):
    sp_csv = files.open(text_files1[i])
    if i == 0:
        sp = pd.read_csv(sp_csv)
        # st.write(sp)
    else:
        # sp_n = pd.read_csv(sp_csv)
        sp = sp.append(pd.read_csv(sp_csv))
        # sp= pd.concat([sp, sp_n], axis= 1)

# st.write(sp.head())

sp['Date'] = sp['Date'].apply(lambda x: pd.to_datetime(str(x), format='%Y%m%d'))
all_symbols = sp.Name.unique()
symbols = st.multiselect("Choose stocks to visualize", all_symbols, all_symbols[:3])
source = sp[sp.Name.isin(symbols)]
chart = chart.get_chart(source)
st.altair_chart(chart, use_container_width=True)

# source = data.stocks()
# all_symbols = source.symbol.unique()
# symbols = st.multiselect("Choose stocks to visualize", all_symbols, all_symbols[:3])

# space(1)

# source = source[source.symbol.isin(symbols)]
# chart = chart.get_chart(source)
# st.altair_chart(chart, use_container_width=True)

# space(2)

# Comments part

conn = db.connect()
comments = db.collect(conn)

with st.expander("💬 Open comments"):

    # Show comments

    st.write("**Comments:**")

    for index, entry in enumerate(comments.itertuples()):
        st.markdown(COMMENT_TEMPLATE_MD.format(entry.name, entry.date, entry.comment))

        is_last = index == len(comments) - 1
        is_new = "just_posted" in st.session_state and is_last
        if is_new:
            st.success("☝️ Your comment was successfully posted.")

    space(2)

    # Insert comment

    st.write("**Add your own comment:**")
    form = st.form("comment")
    name = form.text_input("Name")
    comment = form.text_area("Comment")
    submit = form.form_submit_button("Add comment")

    if submit:
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        db.insert(conn, [[name, comment, date]])
        if "just_posted" not in st.session_state:
            st.session_state["just_posted"] = True
        st.experimental_rerun()
