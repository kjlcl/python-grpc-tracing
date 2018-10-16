import logging
import re

SPAN_KIND = 'span.kind'

COMPONENT = 'component'

# Marks a span representing the client-side of an RPC or other remote call
SPAN_KIND_RPC_CLIENT = 'client'

# Marks a span representing the server-side of an RPC or other remote call
SPAN_KIND_RPC_SERVER = 'server'


# PEER_SERVICE (string) records the service name of the peer
PEER_SERVICE = 'peer.service'

# PEER_HOSTNAME (string) records the host name of the peer
PEER_HOSTNAME = 'peer.hostname'

# PEER_ADDRESS (string) suitable for use in a networking client library.
# This may be a "ip:port", a bare "hostname", a FQDN, or even a
# JDBC substring like "mysql://prod-db:3306"
PEER_ADDRESS = 'peer.address'

# PEER_HOST_IPV4 (uint32) records IP v4 host address of the peer
PEER_HOST_IPV4 = 'peer.ipv4'

# PEER_HOST_IPV6 (string) records IP v6 host address of the peer
PEER_HOST_IPV6 = 'peer.ipv6'

# PEER_PORT (uint16) records port number of the peer
PEER_PORT = 'peer.port'


def add_peer_tags(peer_str, tags):
    ipv4_re = r"ipv4:(?P<address>.+):(?P<port>\d+)"
    match = re.match(ipv4_re, peer_str)
    if match:
        tags[PEER_HOST_IPV4] = match.group('address')
        tags[PEER_PORT] = match.group('port')
        return
    ipv6_re = r"ipv6:\[(?P<address>.+)\]:(?P<port>\d+)"
    match = re.match(ipv6_re, peer_str)
    if match:
        tags[PEER_HOST_IPV6] = match.group('address')
        tags[PEER_PORT] = match.group('port')
        return
    logging.warning('Unrecognized peer: \"%s\"', peer_str)