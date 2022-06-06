import streamlit as st
import os
import logger as log
from dotenv import load_dotenv

import streamlit_google_oauth as oauth
import firestore_db as fdb
import gpt3
import dalle
import textwrap


load_dotenv()
client_id = os.environ["GOOGLE_CLIENT_ID"]
client_secret = os.environ["GOOGLE_CLIENT_SECRET"]
redirect_uri = os.environ["GOOGLE_REDIRECT_URI"]

logger = log.get_logger(__name__)


def del_sentence(user_email, id):
    fdb.del_sentence(user_email, id)
    # constructing the whole new list by all the dictionaries except the one
    blist = [x for x in st.session_state.blist if x["_id"] != id]
    st.session_state.blist = blist
    logger.info(f"Deleted line {id}")


def add_sentence(line, pil_img, user_email=None):
    base64_img = dalle.img_to_base64(pil_img)
    id = fdb.add_sentence(user_email, line, base64_img)

    st.session_state.blist.append(
        {"_id": id, "line": line, "pil_img": pil_img, "base64_img": base64_img}
    )
    logger.info(f"Added line {line} for {user_email}")
    # Reset generated line
    st.session_state.generated_line = None


def main(user_id=None, user_email=None):

    # Set session stages
    if "blist" not in st.session_state:
        st.session_state.blist = fdb.get_sentences(user_email)

    if "generated_line" not in st.session_state:
        st.session_state.generated_line = None

    if "first_line" not in st.session_state:
        st.session_state.first_line = None

    # Show sentences and images
    for i, b in enumerate(st.session_state.blist):
        col1, col2, col3, col4 = st.columns([1, 30, 20, 3])

        format_str = "{}"
        col1.write(i + 1)
        col2.markdown(
            format_str.format(b["line"]),
            unsafe_allow_html=True,
        )

        if "pill_image" in b and b["pill_image"] is not None:
            col3.image(b["pill_image"])
        elif "base64_img" in b and b["base64_img"] is not None:
            b["pill_image"] = dalle.base64_to_img(b["base64_img"])
            col3.image(b["pill_image"])

        col4.button(
            "Delete 🗑️",
            key=b["_id"],
            on_click=del_sentence,
            args=(
                user_email,
                b["_id"],
            ),
        )

    # If this is a first sentence, get from list of sentences
    if len(st.session_state.blist) == 0:
        if st.session_state.first_line is None:
            st.session_state.first_line = gpt3.get_first_line()
        line = st.text_input(
            "Wite the first sentnece (feel free to midify)",
            value=st.session_state.first_line,
            max_chars=256,
        )
    else:
        if st.session_state.generated_line is None:
            with st.spinner("Generating GPT lines (about 2 sec)..."):
                st.session_state.generated_line = gpt3.get_next_line(
                    list=st.session_state.blist
                )
        gpt_button_holder = st.empty()
        gpt_button = gpt_button_holder.button("✍️ Regenerate Sentnece", key='1')
        if gpt_button:
            gpt_button_holder.button("✍️ Regenerate Sentnece", disabled=True, key='2')
            with st.spinner("Regenerating GPT lines (about 2 sec)..."):
                st.session_state.generated_line = gpt3.get_next_line(
                    list=st.session_state.blist
                )
            gpt_button_holder.button("✍️ Regenerate Sentnece", disabled=False, key='3')


        long_line = st.text_input(
            "Next Sentnece (Feel free to regenerate or edit)",
            value=st.session_state.generated_line,
            max_chars=256,
        )

    img = None
    line = None

    if st.button("🎨 (Re)generate Dalle Illustration"):
        if line and len(line) > 0:
            # Limit the max_tokens parameter to 250 per completion.
            short_line = textwrap.wrap(long_line, 50, break_long_words=False)[0]
            line = textwrap.wrap(long_line, 256, break_long_words=False)[0]

            with st.spinner(
                f"Generating illustration for '{short_line} ...' (about 20 sec)"
            ):
                img = dalle.get_images_from_dalle(prompt=line)
                st.image(img)
                logger.info(f"Generated illustration card for {line}")
        else:
            st.error("Please write sentence first")

    if img and line:
        st.button(
            "💾 Save this sentence and Write next sentence",
            on_click=add_sentence,
            args=(line, img, user_email),
        )


if __name__ == "__main__":
    st.set_page_config(page_title="Book Writer", layout="wide", page_icon="📖")
    login_info = oauth.login(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        login_button_text="Continue with Google",
        logout_button_text="Logout",
    )

    # Got emoj from https://emojipedia.org/
    st.write(
        f"""
        ## 📖 AI Book Writing with GPT3 & Dalle-mini
        Just put the first sentence. *DALLE will generate illustrations and GPT3 will write the next sentences.* 
        Feel free to modify generated sentences and create **your own book**!
        """
    )

    if login_info:
        user_id, user_email = login_info
        main(user_id=user_id, user_email=user_email)
        st.markdown("*Powered by AI Book Writer, https://book.sung.ai*")
