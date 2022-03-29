# 初始化資料庫連線
from flask import Flask, render_template, request, redirect, session, template_rendered
import pymongo
client = pymongo.MongoClient(
    "mongodb+srv://cwlizd:qQ1122@mycluster1.hvmmb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.member_system
print('建立連線成功')

# 初始化 Flask 伺服器
app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/"
)
app.secret_key = "any str"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/delaccount", methods=["post"])
def delaccount():
    return render_template("delaccount.html")


@app.route("/delaccount2", methods=["post"])
def delaccount2():
    email = request.form["email"]
    password = request.form["password"]
    collection = db.user
    userdata = collection.find_one({
        "$and": [
            {"email": email},
            {"password": password}
        ]
    })
    if userdata == None:
        return redirect('/error?msg=沒有此帳號阿哥!!!')
    else:
        collection.delete_one({
            "$and": [
                {"email": email},
                {"password": password}
            ]
        })
        return redirect("/finish?msg=完成刪除檔案囉~")


@app.route("/userdata", methods=["post"])
def userdata():
    email = request.form["email"]
    collection = db.user
    userd = collection.find_one({
        "email": email
    })
    if userd == None:
        return redirect("/error?msg=找不到該帳號")
    else:
        nickname = userd["nickname"]
        password = userd["password"]
        print(email, nickname, password)
        return render_template("userdata.html", email=email, nickname=nickname, password=password)


@app.route("/signin", methods=["post"])
def signin():
    email = request.form["email"]
    password = request.form["password"]
    collection = db.user
    result = collection.find_one({
        "$and": [
            {"email": email},
            {"password": password}
        ]
    })
    print(result)
    if result == None:
        return redirect("/error?msg=找不到該帳號或密碼")

    else:
       # 登入成功後，紀錄會員資訊，導向會員頁面
        session["nickname"] = result["nickname"]
        session["email"] = result["email"]
        session["password"] = result["password"]
        return redirect("/member")


@app.route("/member")
def member():
    if "nickname" in session:
        return render_template("member.html")
    else:
        return redirect("/")


@app.route("/upgrade", methods=["post"])
def upgrade():
    email = request.form["email"]
    nickname = request.form["nickname"]
    password = request.form["password"]

    collection = db.user
    upgradedata = collection.update_one({
        "$and": [
            {"nickname": session["nickname"]},
            {"email": session["email"]},
            {"password": session["password"]}
        ]
    }, {
        "$set": {
            "nickname": nickname,
            "email": email,
            "password": password
        }
    })

    del session["nickname"]
    del session["email"]
    del session["password"]
    return redirect("/finish?msg=更改資料完畢請重新登入")

# /error?msg=錯誤訊息


@app.route("/error")
def error():
    message = request.args.get("msg", "發生錯誤請聯繫客服")
    return render_template("error.html", msg=message)


@app.route("/finish")
def finish():
    message = request.args.get("msg", "你完成了某些事歐")
    return render_template("finish.html", msg=message)


@app.route("/signup", methods=["post"])
def signup():
    return render_template("signup.html")


@app.route("/signup2", methods=["post"])
def signup2():
    # 從前端接受資料
    nickname = request.form["nickname"]
    email = request.form["email"]
    password = request.form["password"]
    print(nickname, email, password)

    # 根據接收到的資料，和資料庫互動
    collection = db.user
    result = collection.find_one({
        "email": email
    })
    if result != None:
        return redirect("/error?msg=信箱已被註冊囉!!!")
    else:
        collection.insert_one({
            "nickname": nickname,
            "email": email,
            "password": password
        })
        return redirect("/finish?msg=完成註冊!恭喜你!")


@app.route("/signout")
def signout():
    # 移除session
    del session["nickname"]
    return redirect("/")


app.run(port=3000)
