import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config("菜品推荐系统登陆界面")

# HIDE NAVBAR and stFormSubmitButton
css = '''
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

# Start the connection to Google Sheets
# conn = st.connection("gsheets", type=GSheetsConnection)
# users_db = st.connection("usersDB", type=GSheetsConnection)


# ===========  Start FUNCTIONS  ====================
# @st.cache_data(ttl=60)
# def read_users_db(worksheet, usecols):
#     user_data = users_db.read(worksheet=worksheet, usecols=usecols)
#     user_data = user_data.dropna(how="all")
#     return user_data
#
#
# @st.cache_data(ttl=60)
# def read_data(worksheet, usecols):
#     data = conn.read(worksheet=worksheet, usecols=usecols)
#     data = data.dropna(how="all")
#     return data


def login():
    login_placeholder = st.empty()
    with login_placeholder.form(key="login", clear_on_submit=True):
        st.title("菜品推荐系统登录")
        username = st.text_input("Username")
        passwd = st.text_input("Password", type="password")
        # Read the Users Database
        # read_user = read_users_db("users_db", list(range(4)))
        read_user = {
            'user': 'guojiajing',
            'passwd': '123456'
        }
        ippo = None
        imps = None
        if username:  # Check if username is not empty
            user_exists = read_user['user'] == username
            if user_exists:
                correct_password = read_user['passwd'] == passwd
                if correct_password:
                    # ippo = read_user.loc[user_exists, 'ppo_cpo'].values[0]
                    # imps = read_user.loc[user_exists, 'mps_cps'].values[0]
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    # Store Appo in session_state
                    st.session_state.Appo = ippo
                    # Store Amps in session_state
                    st.session_state.Amps = imps
                else:
                    st.error('密码错误，请重新输入！')
            else:
                st.error('该用户不存在！')
        if st.form_submit_button("Login", type="primary"):
            if 'logged_in' in st.session_state and st.session_state.logged_in:
                st.write(f'Logged in as {username}')
                st.switch_page("pages/1_👋_Hello.py")
                # login_placeholder.empty()  # Clear the login form
        return ippo, imps


# Initialize Login
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    Appo, Amps = login()
else:
    # st.session_state.Appo
    # st.session_state.Amps
    Appo, Amps = login()