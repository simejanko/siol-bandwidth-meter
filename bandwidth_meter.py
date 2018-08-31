import urllib.request
import time
import argparse

PARSE_VAR = "ifcStatList"
STATS_PATH_FORMAT = "http://{}/statsifc.html"
RESET_PATH_FORMAT = "http://{}/statsifcreset.html"
PORT_NAMES = {'eth0': 'LAN1', 'eth1': 'LAN2', 'eth2': 'LAN3', 'eth3': 'LAN4', 'eth4': 'WAN'}

NAME_COLUMN = 0
UP_USAGE_COLUMN = 1
DOWN_USAGE_COLUMN = 9


def check_positive(value):
    if not value.isdigit():
        raise argparse.ArgumentTypeError("should be a positive int value")
    return int(value)


def get_args():
    """ Defines CLI and returns arguments. """

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='ip', default='192.168.1.1', help='router\'s ip')
    parser.add_argument('-u', dest='user', default='user', help='username for router\'s control center')
    parser.add_argument('-p', dest='password', default='user', help='password for router\'s control center')
    parser.add_argument('-d', dest='delay', type=check_positive, default=5, help='delay (in s) between each update')
    return parser.parse_args()


def set_auth(user, password, ip):
    """ Sets up username and password for HTTP basic auth. """

    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, ip, user, password)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)
    urllib.request.install_opener(opener)


def get_stats(ip, delay):
    """ Returns network usage for each port. """

    try:
        #stats reset doesn't always work if we haven't recently requested stats
        urllib.request.urlopen(STATS_PATH_FORMAT.format(ip))
        urllib.request.urlopen(RESET_PATH_FORMAT.format(ip))
        time.sleep(delay)

        port_stats = []
        with urllib.request.urlopen(STATS_PATH_FORMAT.format(ip)) as response:
            text = response.read().decode('utf8')
            for line in text.split("\n"):
                if PARSE_VAR in line:
                    break
            else:
                return None

            if_stat_list = line.split("=")[1].strip().replace('\'', '')
            if_stat_port = sorted(if_stat_list.split('|'))
            for port_raw in if_stat_port:
                port_data = port_raw.split(',')
                port_id = port_data[NAME_COLUMN]
                if port_id not in PORT_NAMES:
                    continue

                port_name = PORT_NAMES[port_id]
                avg_up_usage = (int(port_data[UP_USAGE_COLUMN]) / 1e3) / delay
                avg_down_usage = (int(port_data[DOWN_USAGE_COLUMN]) / 1e3) / delay
                port_stats.append((port_name, avg_up_usage, avg_down_usage))

        return port_stats

    except (urllib.request.URLError, ValueError) as e:
        return None


if __name__ == '__main__':
    try:
        args = get_args()
        set_auth(args.user, args.password, args.ip)
        print("Retrieving first cycle of stats...\n")

        while True:
            port_stats = get_stats(args.ip, args.delay)

            if port_stats is None:
                print("Error retrieving stats. Make sure your ip, username and password settings are correct.")
                time.sleep(args.delay)
                continue

            for port_data in port_stats:
                print("{:4}: up(kB/s):{:8.2f}   down(kB/s):{:8.2f}".format(*port_data))

            print("-" * 50)
            print()
    except KeyboardInterrupt:
        print("Quitting...")
