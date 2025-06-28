from flask import Flask, render_template, request, redirect
from flask_pymongo import PyMongo
from datetime import datetime
import string, random

#DB connection
app=Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Littlify"
db = PyMongo(app).db


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/shorten", methods=['POST'])
def storeURL():
    if request.method=='POST':
        url=request.form.get('url')
        custom_id=request.form.get('custom_id')
        created_date=datetime.now()
        updated_date=created_date
        # print("custom_id=",custom_id)
        
        #if user has not provided a custom code then generate a random one of length 7 chars
        #else make a short url using user given custom code
        if not custom_id:
            short_code=gen_short_code(7) 
            short_url=request.host_url+short_code
            print("short code=",short_code)
        else:
            short_url=request.host_url+custom_id
        #insert all the above information into db
        new={
            "url":url,
            "short_url":short_url,
            "created":created_date,
            "updated":updated_date,
            "hit_counts":0
        }   

        db.urls.insert_one(new)
    return f"{short_url}- short url created"

#retrieve the orginial url from short one and redirect user to the original url
@app.route('/<custom_id>', methods=['GET'])
def retrieve(custom_id):
    given_url=request.host_url+custom_id
    url_obj=db.urls.find_one({"short_url":given_url})

    #if match is found for the given short url, then increase the hit count by 1 
    # and redirect user t ooriginal url else return 404 error
    if url_obj:
        count=url_obj["hit_counts"]+1
        db.urls.update_one({"_id":url_obj["_id"]},{"$set":{"hit_counts":url_obj["hit_counts"]+1}})
        return redirect(url_obj["url"])
    else:
        return "URL not found! :(", 404

#update URL
@app.route("/updateUrl", methods=['POST', 'GET'])
def update_url():
    if request.method=='POST':
        updatedUrl=request.form.get('updatedUrl')
        shortUrl=request.form.get('shortUrl')
        print(updatedUrl, shortUrl)
        url_obj=db.urls.find_one({"short_url":shortUrl})
        updatedTime=datetime.now()
        if url_obj:
            db.urls.update_one({"_id":url_obj["_id"]},{"$set":{"url":updatedUrl, "updated":updatedTime}},upsert=True)
                                # {"$set":{"updated":updatedTime}}, 
            return "URL successfully updated", 200
        else:
            return "URL not found! :(", 404

#delete URL
@app.route("/deleteUrl", methods=['POST'])
def delete_url():
    if request.method=='POST':
        shortUrl=request.form.get('shortUrl')
        # print(shortUrl)
        url_obj=db.urls.find_one({"short_url":shortUrl})
        if url_obj:
            db.urls.delete_one({"_id":url_obj["_id"]})
            print("url deletd")
            return "URL successfully deleted", 204
        else:
            return "URL not found! :(", 404


#get stats of the URL
@app.route("/getStats", methods=['POST'])
def check_stats():
    if request.method=='POST':
        shortUrl=request.form.get('shortUrl')
        # print(shortUrl)
        url_obj=db.urls.find_one({"short_url":shortUrl})
        if url_obj:
            print(url_obj["hit_counts"])
            return f"URL was accessed for totat {url_obj["hit_counts"]} times! :D", 200
        else:
            return "URL not found! :(", 404

#function to short alphaneumeric code of length 7
def gen_short_code(limit):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(limit))
app.run(debug=True)