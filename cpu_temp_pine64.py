import collectd

PATH = '/sys/class/thermal/thermal_zone0/temp'


def config_func(config):
    path_set = False

    for node in config.children:
        key = node.key.lower()
        val = node.values[0]

        if key == 'path':
            global PATH
            PATH = val
            path_set = True
        else:
            collectd.info('cpu_temp plugin: Unknown config key "%s"' % key)

    if path_set:
        collectd.info('cpu_temp plugin: Using overridden path %s' % PATH)
    else:
        collectd.info('cpu_temp plugin: Using default path %s' % PATH)


def read_func():
    # Read raw value
    with open(PATH, 'rb') as f:
        temp = f.read().strip()

    # Temperature on Pine64 is reported in Celcius. We don't need to convert.
    deg = float(temp)

    # Dispatch value to collectd
    val = collectd.Values(type='temperature')
    val.plugin = 'cpu_temp'
    val.dispatch(values=[deg])


collectd.register_config(config_func)
collectd.register_read(read_func)
