import streamlit as st
import pandas as pd
import pyrebase
import time
import re
from streamlit_javascript import st_javascript
from utils.dashboard_utils import read_config
from utils.constants import paths


class FirebaseHandler:
    def __init__(self, firebaseConfig):
        self.firebase = pyrebase.initialize_app(firebaseConfig)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()
        self.storage = self.firebase.storage()

    def _reload(self):
        """Reload the page (to make sure person is logged off, etc.)"""
        st_javascript(
            """
            window.location.reload()
            """,
            key=str(st.session_state.reload_key),  # it needs a key to be reloaded
        )
        st.session_state.reload_key = st.session_state.reload_key + 1

    def upload_file(self, uploaded_file, uid, child):
        """Upload a file to Firebase Storage"""
        if uploaded_file is not None:
            if isinstance(uploaded_file, dict):
                data = uploaded_file
            else:
                if hasattr(uploaded_file, "name"):
                    if uploaded_file.name.endswith(".xlsx"):
                        df = pd.read_excel(uploaded_file)
                        data = df.to_dict(orient="records")
                    else:
                        raise ValueError("Invalid file type")
                else:
                    raise ValueError("Invalid file type")
            self.db.child(uid).child(child).push(data)
            st.success("File uploaded successfully")
        else:
            st.error("Please select a file to upload")
        st.rerun()

    def create_account(self, email, password, handle):
        """Create a new account"""
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            self.db.child(user["localId"]).child("Handle").set(handle)
            st.success("Your account is created successfully! Log in to get started.")
            time.sleep(3)
            return user
        except Exception as e:
            error_msg = str(e)
            match = re.search(r'"message":\s*"([^"]+)"', error_msg)
            if match:
                # Extract the matched group, which is the actual error message
                error_msg = match.group(1)
            st.error(f"Error creating account: {error_msg}. Try again.")
            st.stop()

    def login_account(self, email, password):
        """Log in to an existing account"""
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            st.success("You have logged up successfully")
            time.sleep(2)
            st.session_state.config = read_config(paths["default_dashboard_config"])
            st.session_state.cookie_manager.set("user", user, "user")
            st.session_state.cookie_manager.set(
                "user_logged_in", True, "user_logged_in"
            )
            self._reload()
            return user
        except Exception as e:
            error_msg = str(e)
            match = re.search(r'"message":\s*"([^"]+)"', error_msg)
            if match:
                # Extract the matched group, which is the actual error message
                error_msg = match.group(1)
            st.error(f"Error logging in {error_msg}. Try again.")
            st.stop()

    def read_file(self, uid, file_group="TransactionsData"):
        """Read a file from Firebase Storage"""
        stored_files = self.db.child(uid).child(file_group).get().val()
        if stored_files is not None:
            my_files = self.db.child(uid).child(file_group).get()
            selected_file = my_files.each()[-1].val()
            data_fetched = None
            if file_group == "TransactionsData":
                data_fetched = pd.DataFrame(selected_file)
            elif file_group == "Config":
                data_fetched = selected_file
            else:
                raise ValueError("Invalid file group")
            return data_fetched
        else:
            return None

    def logout_account(self):
        """Log out of an existing account"""
        st.session_state.config = read_config(paths["default_dashboard_config"])
        st.session_state.cookie_manager.set("user_logged_in", False, "user_logged_in_")
        st.session_state.cookie_manager.set("user", None, "user_")
        st.session_state.cookie_manager.set("file_exists", False, "file_exists_")
        st.success("You have logged out of your account.")
        time.sleep(1)
        self._reload()

    def delete_account(self, user):
        """Delete an existing account"""
        try:
            st.session_state.firebase.auth.delete_user_account(user["idToken"])
            st.session_state.cookie_manager.delete("user_logged_in")
            st.session_state.cookie_manager.delete("user")
            st.session_state.cookie_manager.delete("file_exists")
            st.success("You have permanently deleted your account")
            time.sleep(2)
            self._reload()
        except Exception as e:
            if "CREDENTIAL_TOO_OLD_LOGIN_AGAIN" in str(e):
                st.error("To delete your account, you must log in again first.")
                time.sleep(3)
                self.logout_firebase()
            else:
                st.error(e)

    def forgot_password(self, email):
        """Send a password reset email to the given email"""
        st.session_state.firebase.auth.send_password_reset_email(email)
        st.success(
            "Password reset email sent if the email is connected to an account (check spam also!)"
        )
