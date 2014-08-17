import re

def configure_groups(conf = "groups.conf"):
    f = open(conf, 'r')
    sections = {}
    for line in f.read().split('\n'):
        if not line or line[0] == "#":
            continue
        sm = re.match('^\[(.+)\]$', line)
        if sm:
            name = sm.groups()[0]
            sections[name] = []
            continue
        if sections.has_key(name):
            sections[name].append(line.replace('*','.*').upper())
            continue
        print "Not able to parse line '" + line + "' in config"
    return sections
