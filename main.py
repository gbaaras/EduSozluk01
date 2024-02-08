from flask import Flask, render_template, request, redirect, session
import pymongo
app = Flask(__name__)
app.secret_key = 'cok gizli super secret key'

# MongoDB'ye bağlantı kur
client = pymongo.MongoClient()
db = client["EduSozlukDB"]


def get_sequence(seq_name):
    return db.counters.find_one_and_update(filter={"_id": seq_name}, update={"$inc": {"seq": 1}}, upsert=True)["seq"]


@app.route('/hello/<name>')
def hello_name(name):
    return 'Hello %s!' % name


@app.route('/')
def home_page():
    basliklar = list(db["basliklar"].find({}))
    print("ilk başlık:",basliklar[0])
    yazilar = list(db["yazilar"].find({"baslik_id": basliklar[0]["_id"]}))
    return render_template("baslik.html",aktif_baslik=basliklar[0], basliklar=basliklar, yazilar=yazilar)


@app.route('/baslik/<baslik_id>')
def baslik_goster(baslik_id):
    if request.method == 'GET':
        basliklar = list(db["basliklar"].find({}))
        aktif_baslik = db["basliklar"].find_one({"_id": int(baslik_id)})
        yazilar = list(db["yazilar"].find({"baslik_id": int(baslik_id) }))
        return render_template("baslik.html", aktif_baslik=aktif_baslik, basliklar=basliklar, yazilar=yazilar)


@app.route('/yazi-ekle', methods=["POST"])
def yazi_ekle():
    if request.method == 'POST':
        baslik_id = request.form["baslik_id"]
        db["yazilar"].insert_one({
            "_id": get_sequence("yazilar"),
            "baslik_id": int(baslik_id),
            "yazi": request.form["yeni_yazi"]
        })

        return redirect("/baslik/"+baslik_id, 302)


@app.route('/uye-ol', methods=["GET", "POST"])
def uye_ol():
    if request.method == 'GET':
        return render_template("uye-ol.html")
    else:
        # Formdan gelen verileri al
        email = request.form["email"]
        sifre = request.form["sifre"]
        adsoyad = request.form["adsoyad"]



        # Verileri collection'a ekle
        db["kullanicilar"].insert_one({
            "_id": email,
            "sifre": sifre,
            "adsoyad": adsoyad
        })

        return redirect("/giris", 302)


@app.route('/giris', methods=["GET", "POST"])
def giris():
    if request.method == 'GET':
        return render_template("giris.html")
    else:
        # Formdan gelen verileri al
        email = request.form["email"]
        sifre = request.form["sifre"]

        kullanici = db["kullanicilar"].find_one({"_id": email})
        print("kullanici:",kullanici)
        if kullanici and kullanici["sifre"] == sifre:
            session['kullanici'] = kullanici
            return redirect("/", 302)
        else:
            return "Kullanıcı bulunamadı ya da şifre geçersiz"


@app.route('/cikis', methods=["GET", "POST"])
def cikis():
    session.pop('kullanici', None)
    return redirect("/", 302)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
