import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)
# st.sidebar.page_link("pages/2_💪_Diet_Recommendation.py", label='饮食推荐')
st.write("# 欢迎来到一个专属于您的饮食推荐系统! 👋")

st.sidebar.success("请选择一个适合您的推荐应用.")

st.markdown(
    """
   这是一个饮食推荐web应用程序，使用基于内容的方法与Scikit-Learn, FastAPI和Streamlit。
    """
)
