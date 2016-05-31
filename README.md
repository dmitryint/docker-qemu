# QEMU/KVM on Docker and CoreOS

Original idea belongs to: Seán C. McCord (@Ulexus)

## Usage

0. `docker pull intersoftlab/qemu:stable`
0. 
```
docker run --privileged --net=host --pid=host --ipc=host \
-e ETCD_ENDPOINTS=http://172.16.0.1:2379,http://172.16.0.2:2379 \
-e LOCK=/kvm/%i/lock \
-e BRIDGE_IF=qemu0 \
intersoftlab/qemu:stable QEMU_OPTIONS
```

Note that `--privileged` is required in order to run with the kernel-level virtualization (kvm) optimization.


## Background
For the most part, it is fairly easy to run qemu within docker.  The only real hiccup is that /dev/kvm (the device node for the kernel hypervisor access) isn't reissued (or permitted) within docker.  That means we have to do two things for basic usage:

0.  Make the device node
0.  Execute the docker container with `--privileged`

While this is obviously not ideal, it isn't actually _that_ bad, since you are running a full VM, in the container, which _itself_ should isolate the client.

## Why

It's better not to ask.  I really like CoreOS (http://coreos.com), and I am in the process of migrating all my servers over to it.  That means I need somewhere to put all my various full VMs.  While many components can be converted over to Docker-native formats, some customers want or need full VMs even still.  Rather than have a separate OpenStack or Corosync+libvirt system, I can now simply use CoreOS and fleet.

## Networking

One of my gripes with Docker right now is that it's not easy for me to manage my own networking.  Also, it has abysmal support for things like IPv6.  The idea of NATing every connection is repugnant and backward to me.  Never-the-less, I understand the motivations.

Still, for my use, I needed the ability to attach to my network bridge instead of the default `docker0` bridge.  The entrypoint script allows you to pass the `$BRIDGE_IF` environment variable.  If set, it will add that bridge interface to the container's `/etc/qemu/bridge.conf` file which, in turn, allow your qemu instance to attach to that bridge using the built-in `qemu-bridge-helper`.

Note, however, that if you want to do this, you'll need to pass the `--net=host` option to your `docker run` command, in order to access the host's networking namespace.

## Ceph/RBD support

Included in this image is support for Ceph/RBD volumes.  In order to use Ceph, you should probably bind-mount your `/etc/ceph` directory which contains your ceph.conf and client keyring.  I use `docker run -v /etc/ceph:/etc/ceph` for this purpose on my CoreOS boxes.

NOTE:  using qemu's bridge networking with docker's `--net=host` with RBD block storage creates switch loops for me, even with STP.  Removing any one of those three seems to work fine.  To work around this problem, you can also run with `--privileged --pid=host --ipc=host`.

## Service file

Also included in this repo is a service file, suitable for use with systemd (CoreOS and fleet), provided as an example.  You'll need to fill in your own val

## Entrypoint script

The entrypoint script is site-specific for me, but you can override most of it simply by passing arguments to the execution of this container (which will, in turn, be passed as arguments to `qemu`).

If you intend to use the entrypoint script as is, it expects `etcd` to be populated with some keys.  (`%i` below refers to the unit instance, such as `1` for the unit `kvm@1`):
  * `/kvm/%i/host` - Should match host's hostname; used as a mutex for this VM
  * `/kvm/%i/ram` - The amount of RAM to allocate to this VM
  * `/kvm/%i/mac` - The MAC address to assign to the NIC of this VM
  * `/kvm/%i/rbd` - The RBD image (of the form `/<pool-name>/<rbd-name>`)
  * `/kvm/%i/spice_port` - The TCP port to use for the spice server
  * `/kvm/%i/extra_flags` - (optional) Free-form qemu flags to append
  * `/kvm/%i/cloud-config` - (optional) Url for cloud-config file

