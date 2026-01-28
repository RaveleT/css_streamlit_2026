# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 10:57:42 2026

@author: Thendo
"""

import streamlit as st

st.title("Thendo's Streamlit App")

st.title("My App Is The Best")

name = st.slider("Pick a number", 1, 100)
st.write(f"You picked: {name}")





