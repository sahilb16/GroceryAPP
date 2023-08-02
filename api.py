from flask_restful import Api, Resource, reqparse, abort,fields,marshal_with
from flask import request,jsonify
from errors import BusinessValidationError
from datetime import datetime
import sqlite3
import json

login_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str, required=True, help='Username is required')
login_parser.add_argument('password', type=str, required=True, help='Password is required')

users_parser = reqparse.RequestParser()
users_parser.add_argument('username', type=str, required=True, help='Username is required')
users_parser.add_argument('address', type=str, required=True, help='Address is required')
users_parser.add_argument('email',type=str)
users_parser.add_argument('phno', type=int, required=True, help='Phone Number is required')

category_parser = reqparse.RequestParser()
category_parser.add_argument('catcode', type=str, required=True, help='Category code is required')
category_parser.add_argument('catname', type=str, required=True, help='Category name is required')

items_parser = reqparse.RequestParser()
items_parser.add_argument('itemcode', type=str, required=True, help='Item code is required')
items_parser.add_argument('catcode', type=str, required=True, help='Category code is required')
items_parser.add_argument('name', type=str, required=True, help='Item Name is required')
items_parser.add_argument('rate', type=int, required=True, help='Rate is required')
items_parser.add_argument('manufacturedate',type=datetime,required=True)
items_parser.add_argument('expirydate',type=datetime,required=True)
items_parser.add_argument('stock', type=int)

# class Users(Resource):

#     def get(self):
#         conn = sqlite3.connect('grocery1.sqlite3')
#         cursor = conn.cursor()
#         result={}
#         cursor.execute(
#         "SELECT username from users ")
#         result = cursor.fetchall()
#         print(result)
#         cursor.close()
#         return result,200
        
#     def post(self):
#         args = users_parser.parse_args()
#         conn = sqlite3.connect('grocery1.sqlite3')
#         data = request.get_json()
#         cursor = conn.cursor()
#         cursor.execute(
#         "INSERT into users values(?,?,?,?,?)",(data.get('username'),data.get('name'),data.get('address'),data.get('email'),data.get('phno')))
#         conn.commit()
#         conn.close()
#         return "",200  
    
        

class Category1(Resource):

    category_output={
        'catcode' : fields.String,
        'catname' : fields.String
    }

    # @marshal_with(category_output)
    def get(self,catcode):
        conn = sqlite3.connect('grocery1.sqlite3')
        cursor = conn.cursor()
        if catcode=="None":
            result={}
            cursor.execute(
            "SELECT catcode from category")
            numberofcodes = cursor.fetchall()
            for x in numberofcodes:
                cursor.execute(
                "SELECT * from category where catcode=?",(x[0],))
                r=cursor.fetchone()
                
                result[r[0]]=r[1]
            conn.close()
            return result,200
        
        else:
            result={}
            catcode_final=catcode[0].lower()+catcode[1:]
            print(catcode_final)
            if "cat" in catcode:
                cursor.execute(
                "SELECT * from category where catcode=?",(catcode,))
                result = cursor.fetchone()
                conn.close()
            else:
                cursor.execute(
                "SELECT * from category where catname=?",(catcode_final,))
                rt = cursor.fetchone()
                if len(rt)==0:
                    conn.close()
                    raise BusinessValidationError(status_code=404,error_code="ITEM1003",error_message="Item not found")
                result[rt[0]]=rt[1]
            if result is None:
                conn.close()
                raise BusinessValidationError(status_code=404,error_code="CAT1003",error_message="Category not found")
            else:
                conn.close()
                return result,200
        
    def put(self,catcode):
        conn = sqlite3.connect('grocery1.sqlite3')
        cursor = conn.cursor()
        data=request.get_json()
        catcod=data.get('catcode')
        catname=data.get('catname').lower()
        if not catname:
            raise BusinessValidationError(status_code=400,error_code="CAT1001",error_message="Category name is required")
        if not catcod:
            raise BusinessValidationError(status_code=400,error_code="CAT1002",error_message="Category code is required")
        
        else :
            args = category_parser.parse_args()
            cursor.execute(
            "UPDATE category SET catcode=?,catname=? where catcode=?",(catcod,catname,catcode))
            cursor.execute(
            "UPDATE items SET catcode=? where catcode=?",(catcod,catcode))
            conn.commit()
            conn.close()
            return "",200
        
    def delete(self, catcode):
        conn = sqlite3.connect('grocery1.sqlite3')
        cursor = conn.cursor()
        cursor.execute(
        "SELECT * from category where catcode=?",(catcode,))
        category = cursor.fetchone()
        if category is None:
            raise BusinessValidationError(status_code=404,error_code="CAT1003",error_message="Category not found")
        else:   
            cursor.execute(
            "DELETE from category where catcode=?",(catcode,))
            conn.commit()
            conn.close()
            return "", 200

    def post(self):
        conn = sqlite3.connect('grocery1.sqlite3')
        data = request.get_json()
        cursor = conn.cursor()
        cursor.execute(
        "INSERT into category values(?,?)",(data.get('catcode'),data.get('catname').lower()))
        conn.commit()
        conn.close()
        return "",200




class Items(Resource):

    product_output={
        'itemcode' : fields.String,
        'catcode' : fields.String,
        'name' : fields.String,
        'rate' : fields.Integer,
        'manufacturedate' : fields.DateTime,
        'expirydate' : fields.DateTime,
        'stock' : fields.Integer,
    }

    def get(self, itemcode):
        conn = sqlite3.connect('grocery1.sqlite3')
        cursor = conn.cursor()
        if itemcode=="None":
            result={}
            cursor.execute(
            "SELECT itemcode from items")
            result = cursor.fetchall()
            conn.close()
            return result,200
        elif "cat" in itemcode:
            result={}
            cursor.execute(
            "SELECT itemcode from items where catcode=?",(itemcode,))
            numberofcodes = cursor.fetchall()
            for x in numberofcodes:
                cursor.execute(
                "SELECT * from items where itemcode=?",(x[0],))
                r=cursor.fetchone()
                z={'name':r[2],
                   'rate':r[3],
                   'mdate':r[4],
                   'edate':r[5],
                   'stock':r[6]
                   }
                result[r[0]]=z
            conn.close()
            return result,200
        
        elif "item" in itemcode:
            result={}
            cursor.execute(
            "SELECT * from items where itemcode=?",(itemcode,))
            r=cursor.fetchone()
            z={'name':r[2],
               'catcode':r[1],
                   'rate':r[3],
                   'mdate':r[4],
                   'edate':r[5],
                   'stock':r[6]
                   }
            result[r[0]]=z  
            conn.close()   
            if result is None:
                raise BusinessValidationError(status_code=404,error_code="ITEM1003",error_message="Item not found")
            else:
                
                return result,200

        else:
            result={}
            cursor.execute(
            "SELECT * from items where name=?",(itemcode,))
            r=cursor.fetchall()
            if len(r)==0:
                raise BusinessValidationError(status_code=404,error_code="ITEM1003",error_message="Item not found")
            else:
                z={ 'itemcode':r[0][0],
                    'catcode':r[0][1],
                    'name':r[0][2],
                    'rate':r[0][3],
                    'mdate':r[0][4],
                    'edate':r[0][5],
                    'stock':r[0][6]
                    }
                result[r[0][0]]=z  
                conn.close()   
                if result is None:
                    raise BusinessValidationError(status_code=404,error_code="ITEM1003",error_message="Item not found")
                else:
                    return result,200
        
    def put(self, itemcode):
        data = request.get_json()
        itemco = data.get('itemcode')
        catcode = data.get('catcode')
        name = data.get('name').lower()
        rate = data.get('rate')
        manufacturedate = data.get('manufacturedate')
        expirydate = data.get('expirydate')
        stock = data.get('stock')

        conn = sqlite3.connect('grocery1.sqlite3')
        cursor = conn.cursor()
        cursor.execute(
        "UPDATE items SET itemcode=?,catcode=?,name=?,rate=?,manufacturedate=?,expirydate=?,stock=? where itemcode=?",(itemco,catcode,name,rate,manufacturedate,expirydate,stock,itemcode,))
        conn.commit()
        conn.close()
        return '',200
        
    def delete(self, itemcode):
        conn = sqlite3.connect('grocery1.sqlite3')
        cursor = conn.cursor()
        
        
        if "cat" in itemcode:
            print("123")
            cursor.execute(
            "DELETE from items where catcode=?",(itemcode,))
            conn.commit()
            conn.close()
            return "", 200
        else:   
            cursor.execute(
            "SELECT * from items where itemcode=?",(itemcode,))
            item = cursor.fetchone()
            if item is None:
                raise BusinessValidationError(status_code=404,error_code="Item1003",error_message="Item not found")
            else:
                cursor.execute(
                "DELETE from items where itemcode=?",(itemcode,))
                conn.commit()
                conn.close()
                return "", 200

    def post(self):
        conn = sqlite3.connect('grocery1.sqlite3')
        data = request.get_json()
        cursor = conn.cursor()
        print(data)
        cursor.execute(
        "INSERT into items values(?,?,?,?,?,?,?)",(data.get('itemcode'),data.get('catcode'),data.get('itemname').lower(),data.get('itemrate'),data.get('manufacturedate'),data.get('expirydate'),data.get('stock'),))
        conn.commit()
        conn.close()
        return "",200