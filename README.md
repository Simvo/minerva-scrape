# minerva-scrape

### Setup

Upgrade to latest version of pip:
```
$ pip install --upgrade pip
```

Install virtualenv:
```
$ pip install virtualenv
```

Set virtualenv to use python3 (if your python3 is installed in a different location, set the path from `/usr/bin/python3` to that location):
```
$ virtualenv -p /usr/bin/python3 minerva_scrape_env
```

Activate virtualenv:
```
$ source minerva_scrape_env/bin/activate
```

### Dependencies

Install dependencies
```
$ pip install -r requirements.txt
```

Note that if you install more libraries that are required, update requirements.txt  
You can add all current installed dependencies to requirements.txt with:
```
$ pip freeze > requirements.txt 
```

### Running

Run scrape-ctlg.py:
```
$ python scraper.py
```
