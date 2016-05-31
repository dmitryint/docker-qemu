#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from procwrapper import EtcdLock, Qemu
import os
import signal
import sys

if __name__ == "__main__":
        vm = Qemu(
            prog_args=sys.argv[1:],
            lock=EtcdLock(
                lock_file=os.environ.get('LOCK'),
                lock_ttl=os.environ.get('TTL',30),
                endpoints=[{
                                'protocol': endpoint.split(':')[0],
                                'host': endpoint.split(':')[1],
                                'port': int(endpoint.split(':')[2]),
                            } for endpoint in os.environ.get('ETCD_ENDPOINTS').replace('/','').split(',')]
            ),
            cloud_config_url=os.environ.get('CLOUD_CONFIG', None),
            bridge_if=os.environ.get('BRIDGE_IF', 'qemu0'),
            shutdown_timeout=300
        )
        signal.signal(signal.SIGTERM, vm.sigterm_handler)
        sys.exit(
            vm.start().communicate()
        )

