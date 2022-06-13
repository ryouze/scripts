# python
scripts written in python

---



## bibliography_check
python script for checking your bibliography for predatory publishers



* automatically downloads the latest list of predatory publishers from: https://beallslist.net/
* checks your bibliography against that list


requires requests, bs4


```console
pip install requests beautifulsoup4
```

steps:
1. paste your entire bibliography into `./input/your_bibliography.txt`
2. see results printed to console

**note**: since only a simple "in" check is done, it could potentially mark a title or an author as a predatory publisher, e.g., finding `Example` in `Smith. 2009. 'On the notion of Examples". Journal of Things`


```
publisher 'ARPN Journals' found in bibliography: Brown. 2009. 'The title', ARPN Journals 1.
```


***




## grade_avg
python script for calculating grades in my uni


requires bs4


```console
pip install beautifulsoup4
```

steps:
1. log into usos
2. go to student's section -> final grades
3. hit ctrl+s and save entire webpage as html called `my_grades.html`
4. run `main.py`
5. see results in `output.txt`


```
Total average grade overall: x


## Academic year xxxx/xxxx, xxxx semester ##
[subject]
* x
[subject | average: x]
* x
* x
[subject]
* x
...
```


***


## survey_stats
python script for comparing survey results from google forms in two languages


* translates column names and answers into english
* removes participants who click the same answer more than X times (default: 80%)
* removes participants based on conditions, e.g., english not L2
* calculates when began to learn L2, age, gender, city size, uni year
* calculates mean values for each condition and language
* outputs: two cleaned up csv files (en & pl), participants' statistics, mean values condition
* output can be manually edited and used as input again (e.g., when removing based on z-score)


requires pandas


```console
pip install pandas
```

steps:
1. save results of two google forms as csv (e.g., `Survey research EN.csv`, `Survey research PL.csv`)
2. place them into `./input` directory
3. edit `./input/lang_db.json` so your column names and answers match (columns are queried by name instead of index)
4. edit `./input/column_names.txt` so your custom column names match the condition (e.g., `congruent`)
5. edit `comp.py` -> `remove_participants` to remove participants based on your conditions (e.g., if L2 not English)
6. edit `main.py` to enable/disable features you want (e.g., removing participants)
7. run `main.py`
8. see results in `./output`: processed csvs (based on your conditions), participant's statistics, means per each condition


**tip:** if you want to remove participants later (manually), edit the processed `res_*.csv` in `./output` and set `main.py` -> `enabled` -> `use_csv_from_input` to False; all the statistics will be re-done automatically.


example output:


| Participant | Language | Congruent | Incongruent |
| :--: | :--: | :--: | :--: |
| 1 | English | 6.70 | 6.17 |
| 2 | English | 6.03 | 6.01 |
| 3 | Polish | 6.13 | 5.84 |
