import streamlit as st

firebase = st.session_state.firebase

if st.session_state.cookie_manager.get(cookie="user_logged_in"):
    # If user is logged in, let them delete their account or logour
    user = st.session_state.cookie_manager.get(cookie="user")
    logout_button_section, delete_account_button_section = st.columns(2)
    with logout_button_section:
        st.button("Logout", on_click=firebase.logout_account)
    with delete_account_button_section:
        st.button(
            "Delete account permanently",
            on_click=firebase.delete_account,
            args=([user]),
        )
else:
    choice = st.selectbox("login/Signup", ["Login", "Sign up"])
    email = st.text_input("Please enter your email address")
    password = st.text_input("Please enter your password", type="password")
    if choice == "Sign up":
        handle = st.text_input(
            "Please input your app handle name", value=email.strip().split("@")[0]
        )
        st.button(
            "Create my account",
            on_click=firebase.create_account,
            args=(email, password, handle),
        )
    elif choice == "Login":
        login_button_section, forgot_password_button_section = st.columns(2)
        with login_button_section:
            st.button(
                "Login",
                on_click=firebase.login_account,
                args=(email, password),
            )
        with forgot_password_button_section:
            st.button(
                "Forgot password (fill in email first)",
                on_click=firebase.forgot_password,
                args=([email]),
            )
        st.info(f"You are currently logged out.")
