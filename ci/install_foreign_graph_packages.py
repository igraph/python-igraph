# Install foreign graph packages to test import/export functions on CI
import sys
import subprocess as sp


# Networkx is installed in tox later on


# Graph-tool
calltext = ''
if sys.platform == 'linux':
    calltext += '''
    sudo deb http://downloads.skewed.de/apt/bionic bionic universe
    sudo deb-src http://downloads.skewed.de/apt/bionic bionic universe
    sudo apt-key adv --keyserver keys.openpgp.org --recv-key 612DEFB798507F25
    '''
    calltext += '\n'
    if sys.version[0] == '2':
        calltext += 'sudo apt-get install python-graph-tool'
    else:
        calltext += 'sudo apt-get install python3-graph-tool'

else:
    print('Graph-tool installation on OSX and Windows missing for now')

for call in calltext.split('\n'):
    if call == '':
        continue
    print(call)
    call = call.split()
    try:
        sp.run(call)
    except AttributeError:
        sp.call(call)
