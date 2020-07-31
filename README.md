# elasticsearch-DSL
## Require Libraries
* elasticsearch, elasticsearch_dsl
## Features
* Collecting metricbeats index through elasticsearch-DSL.
* Filter time range from current to 10s before.
* Form .csv files according to different [system fields](https://www.elastic.co/guide/en/beats/metricbeat/current/exported-fields-system.html#_users) in Metricbeat.

## Timestamp mismatch issue
* Detail explanation of mismatch issue
  * [Timestamps from Filebeat to Elasticsearch](https://re-ra.xyz/Timestamps-from-Filebeat-to-Elasticsearch/#timestamp-mismatch)
* Solution
  * Use ES pipeline to preprocess the time to local time.
  * Add a pipeline name `timestamp_pipeline` to handle time issue.
  * Elasticsearch search API as follow
  ``` 
    curl -X PUT "localhost:9200/_ingest/pipeline/timestamp_pipeline?pretty" -H 'Content-Type: application/json' -d'
    {
        "description" : "Revise timestamp",
        "processors":[
        {
            "date":{
            "field": "@timestamp",
            "target_field": "@timestamp",
            "timezone": "Asia/Taipei",
            "formats":[
                "ISO8601"
            ],
            "ignore_failure":false
            }    
        }
        ]
    }
    '
  ```
    * Configure file in `/etc/metricbeat/metricbeat.yml`
    * Add setting under `output.elasticsearch`
        ```
        pipelines:
            - pipeline: "timestamp_pipeline"
        ```
     * Reference: [容器目录下的日志time字段总是比正常时间晚8小时](https://github.com/rootsongjc/kubernetes-handbook/issues/209)
