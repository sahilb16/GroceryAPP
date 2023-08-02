from flask import Flask, render_template, request, redirect, url_for,jsonify,flash
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
import requests
import sqlite3
from datetime import datetime
from api import Category1,Items
from errors import BusinessValidationError


app = Flask(__name__, static_folder='static')
app.secret_key="grocery"

# Define models

# class Login(db.Model):
#     __tablename__ = "login"
#     username = db.Column(db.String, db.ForeignKey("users.username"), primary_key=True)
#     password = db.Column(db.String, unique=True)
# class Users(db.Model):
#     __tablename__ = "users"
#     username = db.Column(db.String, primary_key=True, unique=True)
#     name = db.Column(db.String)
#     address = db.Column(db.String(200))
#     email = db.Column(db.String)
#     phno = db.Column(db.Integer)

# class Category(db.Model):
#     __tablename__ = "category"
#     catcode = db.Column(db.String, primary_key=True, nullable=False)
#     catname = db.Column(db.String) 

# class Items(db.Model):
#     __tablename__ = "items"
#     itemcode = db.Column(db.String, primary_key=True, unique=True)
#     catcode = db.Column(db.String, db.ForeignKey("category.catcode"),nullable=False)
#     name = db.Column(db.String)
#     rate = db.Column(db.Integer)
#     Manufacturedate = db.Column(db.DateTime)
#     Expirydate = db.Column(db.DateTime)
#     stock = db.Column(db.Integer)    



# Adding API Resource
api = Api(app)
api.add_resource(Category1, "/api/category1", "/api/category1/<string:catcode>")
api.add_resource(Items, "/api/items", "/api/items/<string:itemcode>")



# Defining routes

#Homepage
@app.route("/", methods=["GET", "POST"])
def homepage():    
    return render_template("homepage.html")

#Register
@app.route("/register",methods=["GET","POST"])
def registeruser():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        name1=request.form['name1']
        name2=request.form['name2']
        address1=request.form['address1']
        address2=request.form['address2']
        city=request.form['city']
        state=request.form['state']
        email=request.form['email']
        phno=request.form['phno']

        name=name1+' '+name2
        address=address1+address2+city+state
        conn = sqlite3.connect('grocery1.sqlite3')
        cursor = conn.cursor()
        result={}
        cursor.execute(
        "SELECT username from users ")
        result = cursor.fetchall()
        
        if result and username==result[0][0]:
           return render_template("register.html",error="username already in use")
        else :

            conn = sqlite3.connect('grocery1.sqlite3')
            cursor = conn.cursor()
            cursor.execute(
            "INSERT into users values(?,?,?,?,?)",(username,name,address,email,phno))
            cursor.execute(
                "INSERT into login values(?,?)",(username,password),)
            conn.commit()
            conn.close()    
            return redirect(url_for('homepage'))
    else:
        return render_template("register.html")    
    


                                        ######## MANAGER SECTION ########



#Manager Login    
@app.route('/managerlogin', methods=['GET', 'POST'])
def managerlogin():
    if request.method == 'POST':
        # to Check if id and pwd fields are present in the form data
        if 'username' not in request.form or 'pwd' not in request.form:
            return render_template('managerlogin.html', error='Missing credentials')

        username = request.form['username']
        passwd = request.form['pwd']
        conn = sqlite3.connect('grocery1.sqlite3')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM login WHERE username in (select username from login where username like 'man%') and username=?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result is None:
            return render_template('managerlogin.html', error='User not registered')
        if "man" not in username:
             return render_template('managerlogin.html', error='Not authorized')
        else:
            if passwd == result[0]:
                activeuser=username
                flash("You are succesfully logged in!")
                return redirect(url_for('display_categories',username=activeuser))
            else:
                return render_template('managerlogin.html', error='Incorrect password')
    return render_template("managerlogin.html")   

#To Display all the Categories.
@app.route('/managerlogin/managerdash/<string:username>')
def display_categories(username):
    catcode = "None"  # Set catcode to None to fetch all categories

    # API URL 
    api_url = "http://localhost:5000/api/category1/"+str(catcode)

    #request to the API
    response = requests.get(api_url)
    
    categories = {}
    if response.status_code == 200:
        categories = response.json()
       
        if len(categories) == 0:
            return render_template('managerdash.html', error="No Categories Present", manager=username)
        else:
            return render_template('managerdash.html', categories=categories, manager=username)
    else:
        return render_template('managerdash.html', categories=categories, manager=username)

#To choose search option
@app.route("/search/<string:username>",methods=["POST"])
def choosesearch(username):
    option=request.form['option']
    searchvariable=request.form['searched']
    if option=="Category":
        return redirect(url_for('search_categories',username=username,value=searchvariable))
    elif option=="Product":
        return redirect(url_for('search_items',username=username,value=searchvariable))
    
#To Search for a particular Category      
@app.route('/managerlogin/managerdash/search/<string:username>/<string:value>',methods=["GET","POST"])
def search_categories(username,value):
    catname=value
    api_url="http://localhost:5000/api/category1/"+str(catname.lower())
    response = requests.get(api_url)
    categories = {}
    categories = response.json()
    if response.status_code != 200:
        return render_template('managerdash.html', error="No such Category", manager=username)
    if response.status_code == 200:
        return render_template('managerdash.html', categories=categories, manager=username) 

#To Search for a particular Items
@app.route('/managerlogin/managerdash/searchproduct/<string:username>/<string:value>',methods=["GET","POST"])
def search_items(username,value):
    productname=value
    api_url1="http://localhost:5000/api/items/"+str(productname.lower())
    response = requests.get(api_url1)
    items = response.json()
    for x in items:
         categories=items[x]['catcode']
    api_url2="http://localhost:5000/api/category1/"+str(categories.lower())
    response = requests.get(api_url2)
    catego=response.json()     
    if response.status_code != 200:
        return render_template('managerproducts.html',categories=catego[1], error="No such Item", manager=username,items=[])
    if response.status_code == 200:
        return render_template('managerproducts.html',categories=catego[1] ,manager=username,items=items)            

#To Add new category
@app.route('/managerlogin/managerdash/newcategory/<string:username>', methods=['GET', 'POST'])  
def addcategories(username):
    if request.method == 'POST':
        url = "http://localhost:5000/api/category1"
        category_code = request.form['catcode']
        category_name = request.form['catname']
        
        a=None
        ur1=url+"/"+str(a)
        response = requests.get(ur1)
        categories = {}
        if response.status_code == 200:
            categories = response.json()
        
        for x in categories:
            if x==category_code:
                
                return render_template('newcategory.html',manager=username,error="Category Code Already Exits")    
        
        # Data to be sent in the request body
        data = {
            'catcode': category_code,
            'catname': category_name
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return redirect(url_for('display_categories',username=username))
        else:
            raise BusinessValidationError(status_code=404,error_code="ADD1001",error_message="Some Error occured")
    else:
        return render_template('newcategory.html',manager=username)        

#To Add new Product
@app.route('/managerlogin/managerdash/newproduct/<string:username>/<string:catcode>', methods=["GET", "POST"])  
def addproducts(username,catcode):
    if request.method == "POST":
        itemcode = request.form['itemcode']
        itemname = request.form['itemname']
        itemrate = request.form['rate']
        mdate = request.form['mdate']
        edate = request.form['edate']
        stock = request.form['stock']

        url = 'http://localhost:5000/api/items'  

        a=None
        url1=url+"/"+str(a)
        response = requests.get(url1)
        items = {}
        if response.status_code == 200:
            items = response.json()
        
        for x in items:
            
            if x[0]==itemcode:
                return render_template('newproduct.html',manager=username,error="Item Code Already Exits")    
        
        # Data to be sent in the request body
        data = {
            'itemcode': itemcode,
            'catcode': catcode,
            'itemname': itemname,
            'itemrate': itemrate,
            'manufacturedate': mdate,
            'expirydate': edate,
            'stock': stock
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return redirect(url_for('fetchproducts',catcode=catcode,username=username)) 
        else:
            raise BusinessValidationError(status_code=404,error_code="ADD1001",error_message="Some Error Occured")
    else:
        return render_template('newproduct.html',manager=username)    
    
#To Display the products of a category
@app.route('/managerlogin/managerdash/managerproducts/<string:username>/<string:catcode>')
def fetchproducts(catcode,username):
    api_url1 = "http://localhost:5000/api/category1/"+str(catcode)
    response = requests.get(api_url1)
    cate = {}
    categories = response.json()
    api_url2 = "http://localhost:5000/api/items/"+str(catcode)

    # Make the request to the API
    response = requests.get(api_url2)
    items = {}
    if response.status_code == 200:
        items = response.json()

        if len(categories) == 0:
            return render_template('managerproducts.html', error="No Categories Present", manager=username,items=items)
        elif len(items) == 0:
            return render_template('managerproducts.html', categories=categories,error="No Items Present", manager=username,items=items)
        else:
            return render_template('managerproducts.html', categories=categories, manager=username,items=items)
    else:
        return redirect(url_for('display_categories',username=username))

#To delete a Category.
@app.route('/managerlogin/managerdash/delete/<string:username>/<string:code>')
def deletecategory(code,username):

    api_url1 = "http://localhost:5000/api/category1/"+str(code)
    response1 = requests.delete(api_url1)
    res1=response1.status_code
    api_url2 = "http://localhost:5000/api/items/"+str(code)
    response2 = requests.delete(api_url2)
    res2=response2.status_code
    if res1==200:
        return redirect(url_for('display_categories',username=username))
    else:
        raise BusinessValidationError(status_code=404,error_code="DEL1001",error_message="Cannot delete")

#To Delete a product    
@app.route('/managerlogin/managerdash/managerproducts/delete/<string:username>/<string:catcode>/<string:code>')
def deleteproduct(code,username,catcode):
    api_url = "http://localhost:5000/api/items/"+str(code)
    response = requests.delete(api_url)
    if response.status_code == 200:
        return redirect(url_for('fetchproducts',username=username,catcode=catcode))
    else:
        raise BusinessValidationError(status_code=404,error_code="DEL1001",error_message="Cannot delete")

#To update a Product
@app.route('/managerlogin/managerdash/managerproducts/update/<string:username>/<string:catcode>/<string:code>', methods=['GET', 'POST'])  
def updateproduct(code,username,catcode):
    name=""
    api_url = 'http://localhost:5000/api/items/'+str(code)
    itemcode=""
    itemname=""
    itemrate=0
    itemmd=None
    itemed=None
    itemst=0
    if request.method == 'POST':
        icode=request.form['itemcode']
        iname=request.form['itemname']
        irate=request.form['rate']
        imdate=request.form['mdate']
        iedate=request.form['edate']
        istock=request.form['stock']

        response1 = requests.get(api_url)
        item = {}
        item=response1.json()
        for x in item:
            itemcode=x
            itemname=item[x]['name']
            itemrate=item[x]['rate']
            itemmd=item[x]['mdate']
            itemed=item[x]['edate']
            itemst=item[x]['stock']

        print(itemcode)    
        if icode=="":
            icode=itemcode
        if iname=="":
            iname=itemname        
        if irate==0:
            irate=itemrate
        if imdate==None:
            imdate=itemmd    
        if iedate==None:
            iedate=itemed
        if istock==0:
            istock=itemst     
        print(iname)
        data = {
            'itemcode': icode,
            'catcode': catcode,
            'name': iname,
            'rate': irate,
            'manufacturedate': imdate,
            'expirydate': iedate,
            'stock': istock
        }
        print(data)
        response = requests.put(api_url,json=data)

        if response.status_code == 200:
            print(itemname)
            return redirect(url_for('fetchproducts',username=username,catcode=catcode))
        else:
            raise BusinessValidationError(status_code=404,error_code="DEL1001",error_message="Cannot Update")
        
    else:
        response1 = requests.get(api_url)
        item = {}
        item=response1.json()
        for x in item:
            itemcode=x
            itemname=item[x]['name']
            itemrate=item[x]['rate']
            itemmd=item[x]['mdate']
            itemed=item[x]['edate']
            itemst=item[x]['stock']
            print(itemname)
        return render_template("changeproduct.html",manager=username,items=item)           

#To update a Category   
@app.route('/managerlogin/managerdash/update/<string:username>/<string:code>', methods=['GET', 'POST'])  
def updatecategory(code,username):
    name=""
    api_url = 'http://localhost:5000/api/category1/'+str(code)
    catcode=""
    catname=""
    if request.method == 'POST':
        caco=request.form['catcode']
        cana=request.form['catname']
        response1 = requests.get(api_url)
        category = {}
        category=response1.json()
        catcode=category[0]
        catname=category[1]
        if caco=="":
            caco=catcode
        if cana=="":
            cana=catname       
        data = {
            'catcode': caco,
            'catname': cana
        }
        api_url1 = 'http://localhost:5000/api/items/'+str(code)
        response = requests.put(api_url,json=data)
        response = requests.put(api_url1,json=data)
        if response.status_code == 200:
            return redirect(url_for('display_categories',username=username))
        else:
            raise BusinessValidationError(status_code=404,error_code="UPDATE1001",error_message="Cannot Update")
        
    else:
        response1 = requests.get(api_url)
        category = {}
        category=response1.json()
        name=category[1]
        catcode=category[0]
        catname=category[1]
        return render_template("changecategory.html",manager=username,categories=category)    






                                        ######## CUSTOMER SECTION ########



temp = {}
#Customer Login
@app.route('/customerlogin', methods=['GET', 'POST'])
def customerlogin():
    if request.method == 'POST':
        # to Check if id and pwd fields are present in the form data
        if 'username' not in request.form or 'pwd' not in request.form:
            return render_template('customerlogin.html', error='Missing credentials')
        username = request.form['username']
        passwd = request.form['pwd']
        conn = sqlite3.connect('grocery1.sqlite3')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM login WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result is None:
            return render_template('customerlogin.html', error='User not registered')
        else:
            if passwd == result[0]:
                activeuser=username
                return redirect(url_for('displaycust_categories',username=activeuser))
            else:
                return render_template('customerlogin.html', error='Incorrect password')
    return render_template("customerlogin.html")

#To display categories on customer side
@app.route('/customerlogin/customerdash/<string:username>')            
def displaycust_categories(username):
    catcode = "None"  # Set catcode to None to fetch all categories
    api_url = "http://localhost:5000/api/category1/"+str(catcode)
    # Make the request to the API
    response = requests.get(api_url)
    categories = {}
    if response.status_code == 200:
        categories = response.json()
        if len(categories) == 0:
            return render_template('customerdash.html', error="No Categories Present", manager=username)
        else:
            return render_template('customerdash.html', categories=categories, manager=username)
    else:
        return render_template('customerdash.html', categories=categories, manager=username)

#To Display the products
@app.route('/customerlogin/customerdash/displayproducts/<string:username>/<string:catcode>',methods=["GET"])
def displaycust_products(username,catcode):
    api_url = "http://localhost:5000/api/items/"+str(catcode)
    response = requests.get(api_url)
    items = {}
    if response.status_code == 200:
        items = response.json()
        if len(items) == 0:
            return render_template('customeritems.html', error="No Items Present", manager=username)
        else:
            return render_template('customeritems.html', items=items, manager=username)
    else:
        return render_template('customeritems.html', items=items, manager=username)

#To Add Items to Cart
@app.route('/customerlogin/customerdash/cart/<string:username>/<string:itemcode>',methods=["GET","POST"])
def addtocart(username,itemcode):
    api_url = "http://localhost:5000/api/items/"+str(itemcode)
    response = requests.get(api_url)
    item={}
    item=response.json()
    rate=0
    available=""
    for x in item:
        rate=item[x]['rate']
        q=item[x]['stock']
        name=item[x]['name']
        catcode=item[x]['catcode']
        if q>0:
            available="In Stock"
        else:
            available="Out of Stock"    

    if request.method=="POST":
        quantity=request.form['quantity']

        if (int(q)-int(quantity))>0:

            cost=round(rate*int(quantity))

            conn = sqlite3.connect('grocery1.sqlite3')
            cursor = conn.cursor()
            str2="SELECT itemname from cart where username=?"
            cursor.execute(str2,(username,))
            presentitems=cursor.fetchall()
            used=0
            for x in presentitems:
                if x[0]==name:
                    used=1
                    break    
            if used==0:        
                str1="INSERT into cart values(?,?,?,?,?,?)"
                cursor.execute(str1, (username,itemcode,catcode,name,rate,cost))
            else:
                str3="UPDATE cart set cost=cost+? where username=? and itemname=?"
                cursor.execute(str3,(cost,username,name,))

            temp[itemcode]={'presentstock':(int(q)-int(quantity)),'quantitypurchased':int(quantity)}
            for x in temp:
                str4="UPDATE items set stock=? where itemcode=?"
                cursor.execute(str4,(temp[x]['presentstock'],x,))
            conn.commit()
            conn.close()
            return redirect(url_for('displaycust_products',username=username,catcode=catcode))
        else:
            return render_template("addtocart.html",manager=username,rate=rate,available=available,itemcode=itemcode,error="Available stock is less than demanded quantity")
    else:
        return render_template("addtocart.html",manager=username,rate=rate,available=available,itemcode=itemcode)
    
#To display Cart
@app.route('/customerlogin/customerdash/viewcart/<string:username>',methods=['GET','POST'])
def viewcart(username):
    conn=sqlite3.connect('grocery1.sqlite3')
    cursor=conn.cursor()
    string="SELECT * from cart where username=?"
    cursor.execute(string,(username,))
    result=cursor.fetchall()
    conn.close()
    n=len(result)
    totalcost=0
    tc=None
    for x in range(0,n):
        totalcost+=int(result[x][5])
    if totalcost!=0:
        tc=totalcost
    if len(result)==0:
        return render_template('usercart.html',cart_items=result,error="No items in Cart",manager=username,totalcost=tc)
    else:
        return render_template('usercart.html',cart_items=result,manager=username,totalcost=tc)

#To Checkout    
@app.route('/customerlogin/cart/<string:username>',methods=["GET","POST"])
def checkout(username):
    conn=sqlite3.connect('grocery1.sqlite3')
    cursor=conn.cursor()
    string="DELETE from cart where username=?"
    cursor.execute(string,(username,))
    for x in temp:
        str="UPDATE items set stock=? where itemcode=?"
        cursor.execute(str,(temp[x]['presentstock'],x,))
    
    conn.commit()
    conn.close()
    str1="Thank you for shopping with Us !"
    str2="Your Products would be delivered in 5 working days."
    return render_template("thankyou.html",manager=username,str1=str1,str2=str2)
 
#To Remove an item from the cart. 
@app.route('/customerlogin/cart/remove/<string:itemcode>/<string:username>',methods=["GET","POST"])
def remove_item(itemcode,username):
    conn=sqlite3.connect('grocery1.sqlite3')
    cursor=conn.cursor()
    string="DELETE from cart where username=? and itemcode=?"
    cursor.execute(string,(username,itemcode,))
    for x in temp:
        if x==itemcode:
            str="UPDATE items set stock=stock+? where itemcode=?"
            print(temp)
            cursor.execute(str,(temp[x]['quantitypurchased'],x,))
    conn.commit()
    conn.close()
    return redirect(url_for('viewcart',username=username))


@app.route("/searchcust/<string:username>",methods=["POST"])
def choosesearch2(username):
    option=request.form['option']
    searchvariable=request.form['searched']
    if option=="Category":
        return redirect(url_for('search_categoriescust',username=username,value=searchvariable))
    elif option=="Product":
        return redirect(url_for('search_itemscust',username=username,value=searchvariable))

@app.route('/customerlogin/customerdash/search/<string:username>/<string:value>',methods=["GET","POST"])
def search_categoriescust(username,value):
    catname=value
    api_url="http://localhost:5000/api/category1/"+str(catname.lower())
    response = requests.get(api_url)
    categories = {}
    categories = response.json()
    if response.status_code != 200:
        return render_template('customerdash.html', error="No such Category", manager=username)
    if response.status_code == 200:
        return render_template('customerdash.html', categories=categories, manager=username) 

#To Search for a particular Items
@app.route('/customerlogin/customerdash/searchproduct/<string:username>/<string:value>',methods=["GET","POST"])
def search_itemscust(username,value):
    productname=value
    api_url1="http://localhost:5000/api/items/"+str(productname.lower())
    response = requests.get(api_url1)
    items = response.json()
    for x in items:
         categories=items[x]['catcode']
    api_url2="http://localhost:5000/api/category1/"+str(categories.lower())
    response = requests.get(api_url2)
    catego=response.json()     
    if response.status_code != 200:
        return render_template('customeritems.html',categories=catego[1], error="No such Item", manager=username,items=[])
    if response.status_code == 200:
        return render_template('customeritems.html',categories=catego[1] ,manager=username,items=items)     

if __name__ == "__ main__":
    app.run(debug=True)