import pymysql
from app import app
from bd_inv import mysql
from flask import jsonify
from flask import flash, request
from auth import BasicAuth
from flask import Response
import requests

key = "Basic YWRtaW46MTIzNA=="




@app.route('/api/vendas', methods=['POST'])
def add_venda():
 
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        _json = request.get_json(force = True)        
        _data_venda = _json['data_venda']
        _id_cliente = _json['id_cliente']
        _id_produto = _json['id_produto']

        if _data_venda and _id_cliente and _id_produto  and request.method == 'POST':
            sqlQuery = "INSERT INTO inventario_produtos (data_venda, id_cliente, id_produto) VALUES (%s,%s,%s)"
            bindData = (_data_venda, _id_cliente, _id_produto)
            try:
                cliente = requests.get(f'http://127.0.0.1:5000/api/clientes/{_id_cliente}', headers = {"Authorization":key})
                produto = requests.get(f'http://127.0.0.1:8000/api/produtos/{_id_produto}', headers = {"Authorization":key})
               # status_prod = requests.get(f'http://127.0.0.1:8000/api/produtos/status/{_id_produto}', headers = {"Authorization":key})

                ##############################################################################
                
            
                ###############################################################################
            except Exception as e:
                return jsonify({"error":'Comunicação falhou...'}), 500
            if cliente.status_code == 404:
                return jsonify('Cliente não encontrado.'), 404
            ###################################################################
            elif produto.status_code == 404 :
                return jsonify('Produto não encontrado '), 404
            ###################################################################
            
            status = produto.json()['status']
            if status == 'I':

                return jsonify('Produto indisponível, compra não cadastrada!'), 404

            elif status == 'D':
            


                cursor.execute(sqlQuery, bindData)
                conn.commit()
                response = jsonify('Venda cadastrado com sucesso!')
                response.status_code = 200
                return response
    
    except Exception as error:
        return f'{error}', 500
    finally:
        cursor.close()
        conn.close()           

@app.route('/api/vendas/<int:id_venda>', methods=['PUT']) 
def update_venda(id_venda):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        _json = request.get_json(force = True)
        
        _data_venda = _json['data_venda']
        _id_produto = _json['id_produto']
        _id_cliente = _json['id_cliente']
        _id_venda =_json['id_venda']
        
        if _data_venda and _id_produto and _id_cliente and _id_venda and request.method == 'PUT':
            sqlQuery = "SELECT * FROM inventario_produtos WHERE id_venda=%s"
            cursor.execute(sqlQuery,id_venda)
            select = cursor.fetchone()
            if not select:
                return Response('Venda não cadastrada', status=400) 
            sqlQuery = "UPDATE inventario_produtos SET data_venda=%s, id_produto=%s, id_cliente=%s  WHERE id_venda=%s"
            bindData = (_data_venda,_id_produto,_id_cliente,_id_venda)
              # Verificação se o Id do cliente confere com o db_clientes
            try:
                cliente = requests.get(f'http://127.0.0.1:5000/api/clientes/{_id_cliente}', headers = {"Authorization":key})
                produto = requests.get(f'http://127.0.0.1:8000/api/produtos/{_id_produto}', headers = {"Authorization":key})
            except Exception as e:
                return jsonify({"error":'Comunicação falhou...'}), 500 
            if cliente.status_code == 404:
                return jsonify('Cliente não encontrado'), 404 
            elif produto.status_code == 404:
                return jsonify('Produto não encontrado.'), 404 
                  
            cursor.execute(sqlQuery, bindData)
            conn.commit() 
            response = jsonify('Dados alterados com sucesso!')
            response.status_code = 200
            return response
            print(response)
        else:
            return  jsonify({"error":f"Erro"}),500
    except Exception as error:
        return jsonify({"error":f"{error}"}), 500
        print(error)
    finally:
        cursor.close()
        conn.close()


@app.route('/api/vendas/<int:id_venda>', methods=['DELETE'])
def delete_venda(id_venda):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        sqlQuery = "SELECT * FROM inventario_produtos WHERE id_venda=%s"
        cursor.execute(sqlQuery, id_venda)
        select = cursor.fetchone()
        if not select:
            return Response('Venda não cadastrada.'),404
        cursor.execute("DELETE FROM inventario_produtos WHERE id_venda =%s", (id_venda))
        conn.commit()
        respone = jsonify('Venda deletada com sucesso!')
        respone.status_code = 200
        return respone
    except Exception as error:
        return jsonify({"error":f"{error}"}), 500
    finally:
        cursor.close()
        conn.close()
        

@app.route('/api/vendas', methods = ['GET'])
def show_venda():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute ("SELECT id_venda,id_produto,id_cliente,DATE_FORMAT(data_venda,'%Y-%m-%d') as data_venda FROM inventario_produtos")
        empRows = cursor.fetchall()
        respone = jsonify(empRows)
        respone.status_code = 200
        return respone
    except Exception as error:
        return f'{error}', 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/vendas/clientes/<int:id_cliente>', methods = ['GET'])
def show_sales_client_id (id_cliente):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute ('SELECT id_cliente, id_venda, data_venda, id_produto FROM inventario_produtos WHERE id_cliente = %s', id_cliente)
        vendRow = cursor.fetchall()
        
        if not vendRow:
            return Response('Venda não cadastrada.'),404
        venda = [] #Cria um array vazio para adcionar produtos contratados por um determinado cliente
        cliente = requests.get(f'http://127.0.0.1:5000/api/clientes/{id_cliente}', headers = {"Authorization":key})
        for i in (vendRow):
            produto = requests.get(f'http://127.0.0.1:8000/api/produtos/{i["id_produto"]}', headers = {"Authorization":key})
           
            venda.append(produto.json())
            i["data_venda"] = f"{i['data_venda']}"
        response = jsonify(cliente.json(), venda, vendRow)        
        response.status_code = 200
        return response
    except Exception as error:
        return f'{error}', 500
    finally:
        cursor.close() 
        conn.close()


@app.route('/api/vendas/<int:id_venda>', methods = ['GET'])
def show_sale_id (id_venda):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute ('SELECT  data_venda, id_cliente, id_produto FROM inventario_produtos WHERE id_venda = %s', id_venda)
        vendRow = cursor.fetchall()
        if not vendRow:
            return Response('Venda não cadastrada.'), 404
        venda = [] #Cria um array vazio para adcionar produtos contratados por um determinado cliente
        for i in (vendRow):
            cliente = requests.get(f'http://127.0.0.1:5000/api/clientes/{i["id_cliente"]}', headers = {"Authorization":key})
            produto = requests.get(f'http://127.0.0.1:8000/api/produtos/{i["id_produto"]}', headers = {"Authorization":key})
            i["data_venda"] = f"{i['data_venda']}"
            venda.append(produto.json())
        response = jsonify( vendRow,venda,cliente.json())        
        response.status_code = 200
        return response
    except Exception as error:
        return f'{error}', 500
    finally:
        cursor.close() 
        conn.close()
        

if __name__ == "__main__":
    app.run(debug=True, port=5004)
    