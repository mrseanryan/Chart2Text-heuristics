# Chart2Text-heuristics
Chart-to-Text: Generating Natural Language Explanations for Charts via heuristics.

Given chart data in CSV format, generate natural language to describe the data.

Inspired by https://github.com/JasonObeid/Chart2Text but taking a simpler approach.

## Usage

1. Convert your chart data into the required file format:

- a CSV file with datapoints. See [example](./examples/dataset/data/1.csv).
- mark important datapoints with a *
- [optional] a matching text file with the chart title. See [example](./examples/dataset/titles/1.txt).

2. Generate a text summary:

```
python3 ./src/generate_summary.py <path to data CSV file>
```

## Dependencies

- pandas 1.4.3
- pymannkendall 1.4.3

`python3 -m pip install pandas==1.4.3 pymannkendall==1.4.3`

### Demo

```
./test.sh
```

OUTPUT:

```
LeBron James had 33655 number of points scored. Carmelo Anthony had 26067 number of points scored. Vince Carter had 25623 number of points scored. Kevin Durant had 22940 number of points scored. Wilt Chamberlain had highest number of points scored 38387.
```

### Examples

Example data is provided in `./dataset`.

The images for the examples are at https://github.com/JasonObeid/Chart2TextImages

#### Example captions generated, with matching chart images

| Chart | Caption (auto-generated) |
|---|---|
| ![1.png](./examples/images/1.png) | Carmelo Anthony, Kevin Durant, LeBron James and Vince Carter had an average 27071.25 number of points scored. Kareem Abdul-Jabbar had highest number of points scored 38387. |
| ![2.png](./examples/images/2.png) | Instagram had highest number of followers in millions 334.72. |
| ![3.png](./examples/images/3.png) | Pittsburgh Steelers had highest super bowl wins 6. |
| ![4.png](./examples/images/4.png) | Apple had highest market value in billion u.s. dollars 961.3. |
| ![5.png](./examples/images/5.png) | League of Legends had highest share of playing time  22.92%. |

Time-based charts:


| Chart | Caption (auto-generated) |
|---|---|
| ![0.time.png](./examples/images/0.time.png) | Q3 '08 to Q4 '19 had an overall increasing trend. Q4 '19 had highest number of users in millions 2498. |
| ![101.time.png](./examples/images/101.time.png) | 2019, 2020, 2021, 2022, 2023 and 2024 had an average 2.12% inflation rate compared to previous year. 1984 to 2024* had an overall decreasing trend. 1997 had lowest inflation rate compared to previous year 0.23%. |
| ![104.time.png](./examples/images/104.time.png) | 2006 to 2019 had an overall increasing trend. 2019 had highest billion u.s. dollars 514.41. |
| ![105.time.png](./examples/images/105.time.png) | 2010/11 to 2018/19 had an overall increasing trend. 2018/19 had highest vehicle sales in million units 21.18. |
| ![115.time.multiple-peaks.png](./examples/images/115.time.multiple-peaks.png) | No overall trend. '10 had highest unemployment rate 9.6%. |

#### More images
The full set of images can be downloaded with the script:

```
./download_images.sh
```

Generate captions for the examples:

```
./test.sh
```

# References

| Topic | Links |
|---|---|
| Trend detection | https://stackoverflow.com/questions/42920537/finding-increasing-trend-in-pandas - https://abhinaya-sridhar-rajaram.medium.com/mann-kendall-test-in-python-for-trend-detection-in-time-series-bfca5b55b |
| Time series support | https://ourcodingclub.github.io/tutorials/pandas-time-series/ ??? https://towardsdatascience.com/analyzing-time-series-data-in-pandas-be3887fdd621?gi=fabb1396ed42 |
