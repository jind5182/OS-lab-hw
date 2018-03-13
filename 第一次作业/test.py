import lxc
import sys

# Setup the container object
c = lxc.Container("test5")
if c.defined:
    print("Container already exists", file=sys.stderr)
    sys.exit(1)
else:
    print("success")

# Create the container rootfs
if not c.create(template="debian"):
    print("Failed to create the container rootfs", file=sys.stderr)
    sys.exit(1)
else:
    print("create succeed")

# Start the container
if not c.start():
    print("Failed to start the container", file=sys.stderr)
    sys.exit(1)
else:
    print("start succeed")

# Run command
if c.attach_wait(lxc.attach_run_command, ['bash', '-c', 'echo "jindian\n1500012815" > Hello-Container']):
    print("Failed to run command in the container", file=sys.stderr)
    sys.exit(1)
else:
    print("run succeed")

# Stop the container
if not c.shutdown(10):
    print("Failed to cleanly shutdown the container, forcing.")
    if not c.stop():
        print("Failed to kill the container", file=sys.stderr)
        sys.exit(1)
    else:
        print("stop succeed")

# Destroy the container
if not c.destroy():
    print("Failed to destroy the container.", file=sys.stderr)
    sys.exit(1)
else:
    print("destroy succees")
