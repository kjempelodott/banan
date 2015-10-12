Collect all you bank statements in various formats in one place. A simple web interface lets you query the database and display the results as a plot or in plain text.

#### Setup

Unless your bank is yAbank or BankNorwegian, you have to add your own parser class to [banan/parser.py](https://github.com/kjempelodott/banan/tree/master/banan/parser.py). It must be a subclass of `Parser`. If possible, export your bank statements to CSV and make a subclass of `CSVParser` (least pain). The new class must be registered in `map_of_maps` in [main](https://github.com/kjempelodott/banan/tree/master/main).

Please read [labels.conf.example](https://github.com/kjempelodott/banan/tree/master/labels.conf.example) to figure out how to put labels on different transactions. There are also a few options that can be set. Remember to save you config file as `labels.conf`.

After you have added your FooBank CSV parser

```python
map_of_maps = { 'foobank' : { '.csv' : FooBankCSVParser } }
```

and created a `labels.conf`, insert your bank statement file(s) with the command

```
./main -f foobar.csv -b foobank
```

#### Web interface

Start the server with the command

```
./main start
```

Go to [localhost](http://127.0.0.1:8000). You can also `restart` and `stop` the server. 

Note that the web interface can only *read* from the database. Any adding, updating or deleting must be done with [main](https://github.com/kjempelodott/banan/tree/master/main) or a Python shell.

##### Requirements:
* python-buzhug
* internet connection (jQuery is fecthed from Google)
* a browser
* (python-pypdf)

##### TODO
* Make it cross-browser (only tested with latest Firefox)
* Fix long labels in plot
* Pipe server output to banan.log