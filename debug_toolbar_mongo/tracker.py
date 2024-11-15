import time
import typing

import bson.json_util
import pymongo
from pymongo.synchronous.collection import Collection


class QueryTracker:
    _original_methods: typing.ClassVar = {
        "refresh": pymongo.cursor.Cursor._refresh,
        "count_documents": Collection.count_documents,
        "insert_one": Collection.insert_one,
        "insert_many": Collection.insert_many,
        "update_one": Collection.update_one,
        "update_many": Collection.update_many,
        "replace_one": Collection.replace_one,
        "delete_one": Collection.delete_one,
        "delete_many": Collection.delete_many,
        "aggregate": Collection.aggregate,
    }

    queries: typing.ClassVar = []

    _cur_refresh_query = None
    _cur_refresh_cursor_hash = None

    @staticmethod
    def enable() -> None:
        pymongo.cursor.Cursor._refresh = QueryTracker._refresh
        Collection.count_documents = QueryTracker._count_documents
        Collection.insert_one = QueryTracker._insert_one
        Collection.insert_many = QueryTracker._insert_many
        Collection.update_one = QueryTracker._update_one
        Collection.update_many = QueryTracker._update_many
        Collection.replace_one = QueryTracker._replace_one
        Collection.delete_one = QueryTracker._delete_one
        Collection.delete_many = QueryTracker._delete_many
        Collection.aggregate = QueryTracker._aggregate

    @staticmethod
    def disable() -> None:
        pymongo.cursor.Cursor._refresh = QueryTracker._original_methods["refresh"]
        Collection.count_documents = QueryTracker._original_methods["count_documents"]
        Collection.insert_one = QueryTracker._original_methods["insert_one"]
        Collection.insert_many = QueryTracker._original_methods["insert_many"]
        Collection.update_one = QueryTracker._original_methods["update_one"]
        Collection.update_many = QueryTracker._original_methods["update_many"]
        Collection.replace_one = QueryTracker._original_methods["replace_one"]
        Collection.delete_one = QueryTracker._original_methods["delete_one"]
        Collection.delete_many = QueryTracker._original_methods["delete_many"]
        Collection.aggregate = QueryTracker._original_methods["aggregate"]

    @staticmethod
    def reset() -> None:
        QueryTracker.queries = []
        QueryTracker._cur_refresh_query = None
        QueryTracker._cur_refresh_cursor_hash = None

    @staticmethod
    def _profile_simple_op(name, collection: Collection, filter, *args, **kwargs):
        QueryTracker._save_last_refresh_query()
        start_time = time.perf_counter()
        result = QueryTracker._original_methods[name](
            collection, filter, *args, **kwargs
        )
        total_time = time.perf_counter() - start_time

        QueryTracker.queries.append(
            {
                "type": name,
                "collection": collection.full_name,
                "query": bson.json_util.dumps(filter),
                "hint": kwargs.get("hint"),
                "start_time": start_time,
                "duration": total_time,
            }
        )
        return result

    @staticmethod
    def _count_documents(collection: Collection, filter, *args, **kwargs):
        return QueryTracker._profile_simple_op(
            "count_documents", collection, filter, *args, **kwargs
        )

    @staticmethod
    def _insert_one(collection: Collection, filter, *args, **kwargs):
        return QueryTracker._profile_simple_op(
            "insert_one", collection, filter, *args, **kwargs
        )

    @staticmethod
    def _insert_many(collection: Collection, filter, *args, **kwargs):
        return QueryTracker._profile_simple_op(
            "insert_many", collection, filter, *args, **kwargs
        )

    @staticmethod
    def _update_one(collection: Collection, filter, *args, **kwargs):
        return QueryTracker._profile_simple_op(
            "update_one", collection, filter, *args, **kwargs
        )

    @staticmethod
    def _update_many(collection: Collection, filter, *args, **kwargs):
        return QueryTracker._profile_simple_op(
            "update_many", collection, filter, *args, **kwargs
        )

    @staticmethod
    def _replace_one(collection: Collection, filter, *args, **kwargs):
        return QueryTracker._profile_simple_op(
            "replace_one", collection, filter, *args, **kwargs
        )

    @staticmethod
    def _delete_one(collection: Collection, filter, *args, **kwargs):
        return QueryTracker._profile_simple_op(
            "delete_one", collection, filter, *args, **kwargs
        )

    @staticmethod
    def _delete_many(collection: Collection, filter, *args, **kwargs):
        return QueryTracker._profile_simple_op(
            "delete_many", collection, filter, *args, **kwargs
        )

    @staticmethod
    def _aggregate(collection: Collection, filter, *args, **kwargs):
        return QueryTracker._profile_simple_op(
            "aggregate", collection, filter, *args, **kwargs
        )

    @staticmethod
    def _refresh(cursor: pymongo.cursor.Cursor):
        cursor_hash = QueryTracker._cursor_to_hash(cursor)

        start_time = time.perf_counter()
        result = QueryTracker._original_methods["refresh"](cursor)
        total_time = time.perf_counter() - start_time

        if cursor_hash == QueryTracker._cur_refresh_cursor_hash:
            QueryTracker._cur_refresh_query["duration"] += total_time
        else:
            QueryTracker._save_last_refresh_query()
            QueryTracker._new_refresh_query(cursor, total_time, start_time)

        if not cursor.alive:
            QueryTracker._save_last_refresh_query()

        return result

    @staticmethod
    def _cursor_to_dict(cursor) -> dict[str, typing.Any]:
        return {
            "collection": cursor.collection.full_name,
            "query": bson.json_util.dumps(cursor._spec),
            "projection": cursor._projection,
            "ordering": cursor._ordering,
            "skip": cursor._skip,
            "limit": cursor._limit,
            "hint": cursor._hint,
        }

    @staticmethod
    def _cursor_to_hash(cursor) -> str:
        d = QueryTracker._cursor_to_dict(cursor)
        return bson.json_util.dumps(d)

    @staticmethod
    def _new_refresh_query(cursor, total_time, start_time) -> None:
        QueryTracker._cur_refresh_cursor_hash = QueryTracker._cursor_to_hash(cursor)
        QueryTracker._cur_refresh_query = {
            "type": "find",
            "duration": total_time,
            "start_time": start_time,
        } | QueryTracker._cursor_to_dict(cursor)

    @staticmethod
    def _save_last_refresh_query() -> None:
        if QueryTracker._cur_refresh_query:
            QueryTracker.queries.append(QueryTracker._cur_refresh_query)
            QueryTracker._cur_refresh_query = None
            QueryTracker._cur_refresh_cursor_hash = None
