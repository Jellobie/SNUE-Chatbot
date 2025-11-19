
import streamlit as st
import pandas as pd
import numpy as np


st.write ("data analysis")

np.random.seed(2025)
num_rows = 10  # 데이터 행 개수
data = []
for i in range(num_rows):
    data.append(
        {
        "preview":f"https://picsum.photos/200/300?random={i}",
        "Views":np.random.randint(0,1000),
        "Active":np.random.choice([True,False]),
        "Category":np.random.choice(["LLM","Data","Tool"]),
        "Progress":np.random.randint(1,100),
         }
    )
df = pd.DataFrame(data)
st.dataframe(df)