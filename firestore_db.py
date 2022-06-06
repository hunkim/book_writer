import os
import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


from dotenv import load_dotenv

load_dotenv()

FIREBASE_KEY_JSON = os.environ["FIREBASE_KEY_JSON"]

# https://stackoverflow.com/questions/44293241/check-if-a-firebase-app-is-already-initialized-in-python
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_JSON)
    default_app = firebase_admin.initialize_app(cred)

db = firestore.client()


def add_sentence(email, line, base64_img=None, bookname="main"):
    today = datetime.datetime.now()

    book_ref = db.collection(email).document(bookname)
    line_ref = book_ref.collection("lines")

    res = line_ref.add({"date": today, "line": line, "base64_img": base64_img})
    return res[1].id


def get_sentences(email, bookname="main"):
    book_ref = db.collection(email).document(bookname)
    # order by date
    lines = (
        book_ref.collection("lines")
        .order_by("date", direction=firestore.Query.ASCENDING)
        .get()
    )

    ret_list = []
    for line in lines:
        ret = line.to_dict()
        ret["_id"] = line.id
        ret_list.append(ret)

    return ret_list


def del_sentence(email, line_id, bookname="main"):
    book_ref = db.collection(email).document(bookname)
    line_ref = book_ref.collection("lines").document(line_id)
    line_ref.delete()


if __name__ == "__main__":
    print(add_sentence("hunkim@xxx", "hello" + str(datetime.datetime.now())))
    for line in get_sentences("hunkim@xxx"):
        print(line.id, line.to_dict())
        del_sentence("hunkim@xxx", line.id)
