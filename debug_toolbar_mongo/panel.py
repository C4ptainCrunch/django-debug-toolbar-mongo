from debug_toolbar.panels import Panel

from .tracker import QueryTracker


class MongoPanel(Panel):
    name = "MongoDB"
    has_content = True
    template = "mongodb-panel.html"

    def title(self):
        return "MongoDB Operations"

    def nav_title(self):
        return "MongoDB"

    def nav_subtitle(self):
        stats = self.get_stats()
        count = len(stats["queries"])
        time_total_ms = sum([query["duration_ms"] for query in stats["queries"]])
        return f"{count} queries in {round(time_total_ms)} ms"

    def enable_instrumentation(self):
        QueryTracker.enable()

    def disable_instrumentation(self):
        QueryTracker.disable()

    def process_request(self, request):
        QueryTracker.reset()
        result = super().process_request(request)
        QueryTracker._save_last_refresh_query()
        return result

    def generate_stats(self, request, response):
        queries = QueryTracker.queries
        if queries:
            min_start = min([query["start_time"] for query in queries])
            max_end = max(
                [query["start_time"] + query["duration"] for query in queries]
            )
            total_duration = max_end - min_start
            for query in queries:
                query["start_offset"] = (
                    (query["start_time"] - min_start) / total_duration * 100
                )
                query["width_ratio"] = query["duration"] / total_duration * 100
                query["trace_color"] = "#ccc"
                query["duration_ms"] = query["duration"] * 1000
        self.record_stats({"queries": queries})

    def generate_server_timing(self, request, response):
        stats = self.get_stats()
        title = "MongoDB {} queries".format(len(stats.get("queries", [])))
        value = stats.get(
            "mongodb_time",
            sum([query["duration_ms"] for query in stats.get("queries", [])]),
        )
        self.record_server_timing("mongodb_time", title, value)
