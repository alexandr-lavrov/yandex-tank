import time


def uts(dt):
    return int(time.mktime(dt.timetuple()))


class Decoder(object):
    def __init__(self, tank_tag, uuid):
        self.tank_tag = tank_tag
        self.uuid = uuid

    def decode_monitoring_item(self, item):
        host, metrics, _, ts = item
        return {
            "measurement": "monitoring",
            "tags": {
                "tank": self.tank_tag,
                "host": host,
                "uuid": self.uuid,
            },
            "time": ts,
            "fields": metrics,
        }

    def decode_monitoring(self, data):
        points = []
        for second_data in data:
            timestamp = second_data["timestamp"]
            for host, host_data in second_data["data"].iteritems():
                points += [{
                    "measurement": "monitoring",
                    "tags": {
                        "tank": self.tank_tag,
                        "uuid": self.uuid,
                        "host": host,
                        "comment": host_data["comment"],
                    },
                    "time": timestamp,
                    "fields": {  # quantiles
                        metric: value
                        for metric, value in host_data["metrics"].iteritems()
                    },
                }]
        return points

    def decode_aggregate(self, data, stat):
        timestamp = int(data["ts"])
        points = [
            {
                "measurement": "overall_quantiles",
                "tags": {
                    "tank": self.tank_tag,
                    "uuid": self.uuid,
                },
                "time": timestamp,
                "fields": {  # quantiles
                    'q' + str(q): value / 1000.0
                    for q, value in zip(data["overall"]["interval_real"]["q"]["q"],
                                        data["overall"]["interval_real"]["q"]["value"])
                },
            }, {
                "measurement": "overall_meta",
                "tags": {
                    "tank": self.tank_tag,
                    "uuid": self.uuid,
                },
                "time": timestamp,
                "fields": {
                    "active_threads": stat["metrics"]["instances"],
                    "RPS": data["overall"]["interval_real"]["len"],
                    "planned_requests": float(stat["metrics"]["reqps"]),
                },
            }, {
                "measurement": "net_codes",
                "tags": {
                    "tank": self.tank_tag,
                    "uuid": self.uuid,
                },
                "time": timestamp,
                "fields": {
                    str(code): int(cnt)
                    for code, cnt in data["overall"]["net_code"]["count"].items()
                },
            }, {
                "measurement": "proto_codes",
                "tags": {
                    "tank": self.tank_tag,
                    "uuid": self.uuid,
                },
                "time": timestamp,
                "fields": {
                    str(code): int(cnt)
                    for code, cnt in data["overall"]["proto_code"]["count"].items()
                },
            }, {
                "measurement": "time_intervals",
                "tags": {
                    "tank": self.tank_tag,
                    "uuid": self.uuid,
                },
                "time": timestamp,
                "fields": {
                    'q' + str(point['to']): point['count']
                    for point in self.convert_hist(
                        data["overall"]["interval_real"]["hist"]
                    )
                },
            },
        ]
        return points

    def convert_hist(self, hist, sep=None):
        points = sep or (0, 1, 10, 100, 1000, 10000)

        data = hist['data']
        bins = hist['bins']
        return [
            {
                'from': left,
                'to': right,
                'count': sum(
                    d for b, d in zip(bins, data)
                    if left <= b / 1000 < right
                )
            } for left, right in zip(points[:-1], points[1:])
        ]
