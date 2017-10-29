Collect all you bank statements in various formats in one place. A simple web interface lets you query the database and display the results as a graph or in plain text.

#### Setup

Unless your bank is yAbank or BankNorwegian, you have to add your own parser class to [banan/parser.py](https://github.com/kjempelodott/banan/tree/master/banan/parser.py). It must be a subclass of `Parser`. If possible, export your bank statements to CSV and make a subclass of `CSVParser` (least pain). The new class must be registered in `map_of_maps` in [main](https://github.com/kjempelodott/banan/tree/master/main).

Please read [labels.conf.example](https://github.com/kjempelodott/banan/tree/master/labels.conf.example) to figure out how to put labels on different transactions. There are also a few options that can be set. Remember to save your config file as `labels.conf`.

After you have added your FooBank BAZ parser

```python
map_of_maps = { 'foobank' : { '.baz' : FooBankBAZParser } }
```

and created a `labels.conf`, insert your bank statement file(s) with the command

```
./main -f foobar.baz -b foobank
```

##### Requirements:
* A modern browser
* python3
* For PDF-support: pyPdf (pip3 install pypdf)
* For Excel-support: xlrd (pip3 install xlrd)

#### Web interface

Start the server with the command

```
./main start
```

Go to [localhost](http://127.0.0.1:8000) to browse your transactions history. You can also `restart` and `stop` the server.

##### TODO
* Make it cross-browser (only tested with latest Firefox)
* Fix long labels in plot
* Pipe server output to banan.log