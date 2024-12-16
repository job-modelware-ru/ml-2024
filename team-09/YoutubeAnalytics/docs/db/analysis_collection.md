# Analysis collection description

```json
{
    "id": "g_sA8hYU3b8", // id of video or channel
    "type": 7, // type of metric from 7 to 13
    "updated": "2023-12-11T20:21:15.488055", // last analysis time
    "metric": "depends on type" // results of analysis
}
```
## Types of metric:
* 7 -- Two same size arrays: first contains times, second cumulative count of comments
* 8 -- Dictionary with keys: two letter name of language, and values: number of that languages 
* 9 -- Dictionary with keys: names of emotions and, values: counts 
* 10 -- Dictionary with two keys: reply and like counts, and values: dictionaries with keys: comments ids and values: counts
* 11 -- Dictionary with three keys: positive, negative and neutral, and values: counts
* 12 -- Number: special metric
* 13 -- WordCloud as numpy  array 
