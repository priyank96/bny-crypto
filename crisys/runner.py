"""
Runner
Intended to be the entry point
use command line arguments/code flags to start an event processor/data listener/api process
"""
import argparse
from crisys.data_listener import DataListenerFactory

parser = argparse.ArgumentParser(
    prog='CriSys',
    description='A Crypto Risk Indicator',
    epilog='Made with ❤ at CMU'
)
parser.add_argument('component', help='Specify listener, processor or api')

if __name__ == '__main__':
    args = parser.parse_args()
    if args.component == 'listener':
        # do data listener things
        data_listener = DataListenerFactory.get_listener({}, listener_type='batch')
        data_listener.start()
    elif args.component == 'processor':
        # do event processor things
        pass
    elif args.component == 'api':
        # do api things
        pass
    else:
        raise Exception('Invalid component name specified! Try (listener|processor|api)')
