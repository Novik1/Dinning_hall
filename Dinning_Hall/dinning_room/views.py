from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.core.cache import caches
import requests
from django.views.decorators.csrf import csrf_exempt
import time
import random
import threading
from threading import Thread
import json
import queue

foods = [{
"id": 1,
"name": "pizza",
"preparation-time": 20 ,
"complexity": 2 ,
"cooking-apparatus": "oven"
},
 {
"id": 2,
"name": "salad",
"preparation-time": 10 ,
"complexity": 1 ,
"cooking-apparatus": "null"
},
{
"id": 3,
"name": "zeama",
"preparation-time": 7 ,
"complexity": 1 ,
"cooking-apparatus": "stove"
},
{
"id": 4,
"name": "Scallop Sashimi with Meyer Lemon Confit",
"preparation-time": 32 ,
"complexity": 3 ,
"cooking-apparatus": "null"
},
{
"id": 5,
"name": "Island Duck with Mulberry Mustard",
"preparation-time": 35 ,
"complexity": 3 ,
"cooking-apparatus": "oven"
},
{
"id": 6,
"name": "Waffles",
"preparation-time": 10 ,
"complexity": 1 ,
"cooking-apparatus": "stove"
},
{
"id": 7,
"name": "Aubergine",
"preparation-time": 20 ,
"complexity": 2 ,
"cooking-apparatus": "null"
},
{
"id": 8,
"name": "Lasagna",
"preparation-time": 30 ,
"complexity": 2 ,
"cooking-apparatus": "oven"
},
{
"id": 9,
"name": "Burger",
"preparation-time": 15 ,
"complexity": 1 ,
"cooking-apparatus": "oven"
},
{
"id": 10,
"name": "Gyros",
"preparation-time": 15 ,
"complexity": 1 ,
"cooking-apparatus": "null"
}]

global number_of_tables
global number_of_waiters
global waiter_semaphore
global table_name
global order_id
global table_queue

waiter_semaphore = 0
number_of_tables = 10
number_of_waiters = 5
order_id = 0
table_queue = []

lock = threading.Lock()


def table(request, table_name, status, number):
    order = ""
    received_id = {'order_id': -1}
    stars = 0
    print(table_name + " is generating an order")
    order = generate_order()
    start_time = time.time()
    call_waiter(table_name, order)
    while (received_id['order_id'] != order['id']):
        print("received id " + str(received_id['order_id']) + " order_id " + str(order['id']))
        print("Table loop while")
        if request.method == 'POST':
            received_id = request.POST.get('order_id')
            print("Received id: " + str(received_id['order_id']))
    end_time = time.time()
    general_time = start_time - end_time
    if (general_time <= order['max_wait']):
        stars = 5
    elif (general_time <= order['max_wait'] * 1.1):
        stars = 4
    elif (general_time <= order['max_wait'] * 1.2):
        stars = 3
    elif (general_time <= order['max_wait'] * 1.3):
        stars = 2
    elif (general_time <= order['max_wait'] * 1.4):
        stars = 1
    print("Max wait time: " + str(order['max_wait']) + ",  General time: " + str(general_time) + ",  " + table_name + " puts " + str(stars) + " stars")
    table_queue[number] = 0
    print(table_name + " is free now!!!")

def generate_order():
    global order_id

    items = []

    id = order_id
    lock.acquire()
    order_id += 1
    lock.release()
    random_counter = random.randint(1, 11)
    max_wait = 0
    order_priority = '0'

    for dish in range(random_counter):
        random_id = random.randint(1, 10)
        items.append(random_id)
        if max_wait < foods[int(random_id - 1)]["preparation-time"]:
            max_wait = foods[int(random_id - 1)]["preparation-time"]
    if max_wait == 35:
        order_priority = '5'
    elif max_wait == 32:
        order_priority = '4'
    elif max_wait == 30:
        order_priority = '3'
    elif max_wait == 20:
        order_priority = '2'
    else:
        order_priority = '1'

    max_wait *= 1.3

    print("Order of " + table_name + " is ready")
    order = {"id" : order_id, "items": items, "priority": order_priority, "max_wait": max_wait}
    print(order)
    return order


@csrf_exempt
def call_waiter(table_name, order):
    global waiter_semaphore

    if waiter_semaphore < number_of_waiters:
        waiter_semaphore += 1
        print(str(waiter_semaphore) + " waiters are busy now")
        waiter_name = table_name + " waiter"
        thread_waiter = threading.Thread(target=waiter, name=waiter_name, args=('http://127.0.0.2:8000/kitchen/', order,))
        thread_waiter.start()
    else:
        time.sleep(1)
        call_waiter(table_name, order)

@csrf_exempt
def waiter(request, order):
    global waiter_semaphore

    time.sleep(2)
    waiter_semaphore -= 1
    headers = {'Content-Type' : 'application/json'}
    response = requests.post('http://127.0.0.2:8000/kitchen/', data=json.dumps(order), headers = headers)
    print(response.content)
    return HttpResponse(order)

@csrf_exempt
def main(request):
    global table_name
    global table_queue

    for i in range(0, number_of_tables):
        table_queue.append(0)

    while True:
        for i in range (0, number_of_tables):
            if (table_queue[i] == 0):
                table_queue[i] = 1
                status = 1
                table_name = "Table " + str(i+1)
                thread_table = threading.Thread(target=table, name=table_name, args=(request, table_name, 1, i))
                thread_table.start()
    return HttpResponse("Ready!")
