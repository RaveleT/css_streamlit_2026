# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 10:57:42 2026

@author: Thendo
"""

import streamlit as st


st.write("CSS 2026:")

st.title("Thendo's First Streamlit App")

name = st.slider("Pick a number", 1, 100)
st.write(f"You picked: {name}")



st.header("heading 1")

st.markdown("some text that you can write")