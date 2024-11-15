from django.conf import settings
from django.db import connection
from django.shortcuts import render
from pymongo import MongoClient

collection = MongoClient(settings.MONGO_CONN)[settings.MONGO_DB][
    settings.MONGO_COLLECTION
]


def index(request):
    collection.find_one({"job.title": "Developer"})

    collection.count_documents(
        {"name": "Alice", "job.title": "Developer"},
        hint="name_1",
    )

    list(collection.find({"name": "Alice"}))

    list(collection.find({"name": "Alice"}).hint("name_1"))

    collection.find_one({"idx": 25})

    list(collection.find({"job.title": "Developer"}, {"job": 1}))

    list(collection.find())

    list(collection.find({"job.title": "Developer"}).sort("age", -1))

    list(
        collection.find(
            {"job.title": "Developer", "name": "Bob"},
        ).sort("age", -1)
    )

    list(collection.find({"job.title": "Developer"}).sort("job.salary", -1))

    list(
        collection.find(
            {"job.title": "Developer"},
            {"_id": 0, "job.title": 1, "age": 1},
        ).sort("age", -1)
    )

    list(collection.find({"job.title": "Developer"}).skip(20).limit(50))

    list(
        collection.find(
            {"job.title": "Developer", "age": {"$gte": 30, "$lte": 40}},
        )
    )

    collection.update_many({"name": "Alice"}, {"$set": {"job.salary": 3500}})

    collection.aggregate(
        [{"$project": {"food": 0}}, {"$set": {"money": "$job.salary"}}],
    )

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.execute("SELECT 2")
        cursor.fetchone()

    return render(request, "index.html")
