## news_crawl

Crawling news and generates local webpages with specific interest on topics 

## Setups

Dependencies setup, including binary dependencies and python dependencies. Run 

```
$ ./bin_deps.sh
```

to setup binary dependencies. If OS is not Debian derived, change `INSTALLER` variable in the script, and this
hopefully should work. If OS is windows, good luck, binary depedencies need to be resolved by hand.

Then run

```
$ ./py_deps.sh
```

to setup python dependencies. Python version should be >2.7 but not 3. There are python modules depend on certain
binaries, so make sure binaries are all installed properly.

It might also be a good idea to install python dependencies in virtualenv.

## How it works

`run.sh` is the main entry. It launches http server, crawling, and then html generation.

```
$ ./run.sh -h
./run.sh -p port -o output_folder -t target

options:
-p              the port to open the http server.
-o              output folder.
-t              target to crawl. CNN for example.
-h              display rhis help.

```

A sample run might be:

```
$ ./run.sh -p 8000 -t CNN -o /tmp/news
```

### Web Crawling

Web Crawling is implemented using [scrapy](https://scrapy.org/). What the app does is basically starting from the
mainpage, say [CNN](http://cnn.com), then recursively go down to sub-brands, and grab the news in those pages. please
check `crawler/crawler/spiders` for concrete spider implementations.

After that, the article pages will be parsed, and filtered based on certain predicates in order to capture the users'
preferrence. For example, in `crawler/crawler/spiders/CNN.py`, preferences are:

```python
    targets = {
        'Trump': Target("Trump", lambda s: 'Trump' in s),
        'Clinton': Target("Clinton", lambda s: 'Clinton' in s),
        'Obama': Target("Obama", lambda s: 'Obama' in s)
    }
```

It means we will be targeting three political figures, based on whether their family names appear in certain text
regions.

Then we generate meta data and put it into a `.jsonl` file for each target.

### Front End

Front end is implemented with [bootstrap](http://getbootstrap.com/), and the HTML generation is done by both raw text
generation and [wheezy.template](https://pypi.python.org/pypi/wheezy.template), which is a light weight and blazingly
fast html template framework.

`template.py` is the entry point. It will generate 25 latest topics for the targets. It can be changed by modifying the
variable `TOP` in the file.
