# elasticsearch-DSL
## Features
* Collecting metricbeats index through elasticsearch-DSL.
* Filter time range from current to 10s before.
* Form .csv files according to different [system fields](https://www.elastic.co/guide/en/beats/metricbeat/current/exported-fields-system.html#_users) in Metricbeat.

## Timestamp mismatch issue
* Reference
  * [Timestamps from Filebeat to Elasticsearch](https://re-ra.xyz/Timestamps-from-Filebeat-to-Elasticsearch/#timestamp-mismatch)
  * [容器目录下的日志time字段总是比正常时间晚8小时](https://github.com/rootsongjc/kubernetes-handbook/issues/209)
* Solution
  * Set filter time range to 28800s earlier.
  * Simply convert the timestamp retrieve from metricbeats index into unix time.
  * Add 28800s (UTC+8) to the timestamp and then convert it back to datetime format.
  * Write it to the .csv files.
