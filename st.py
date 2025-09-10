import streamlit as st
import pandas as pd

data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
st.dataframe(data)
