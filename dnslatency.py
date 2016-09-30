import random
import socket
import dns.resolver
from timeit import default_timer as timer

DEBUG = 0
descriptors = []

def resolve_name(name):
    """ Convert a name to an IP address """
    try:
        ip = socket.gethostbyname(name)
    except socket.herror:
        ip = "8.8.8.8"
    return ip

def time_name_resolution(name_server, name, rr_type):
    """
       Calculate the time it takes to resolve a domain name
    """
    resolver = dns.resolver.Resolver()
    resolver.nameservers = name_server
    
    start_time = timer()
    try:
        dns_answer = resolver.query(name, rr_type)
    except:
        # TODO: Adjust error handling return value
        return 60

    end_time = timer()        
    return (end_time - start_time)

def query_handler(name):
    """ 
       Callback invoked by ganglia to measure metrics
    """
    name_servers = []
    metric, dns_server_name, domain, rrec = name.split('_')
    name_servers.append(resolve_name(dns_server_name))
    resolution_time =  time_name_resolution(name_servers, domain, rrec)
    
    if DEBUG:
        print "DNSINFO: Query handler variables:"
        print "  DNSINFO: DNS Server name " + dns_server_name
        print "  DNSINFO: DNS List ", name_servers
        print "  DNSINFO: DOmain: " + domain
        print "  DNSINFO: Record type: " + rrec
        print "  DNSINFO: Resolution time: ", resolution_time

    return resolution_time


def metric_init(params):
    for site, values in params.items():
        dns_server_name, domain, rrec = values.split()

        desc = { 'name': 'dnslatency_' + dns_server_name + '_' + domain + '_' + rrec,
                 'call_back': query_handler,
                 'time_max': 60,
                 'value_type': 'double',
                 'units': 'Query Time',
                 'slope': 'both',
                 'format': '%.4f',
                 'description': 'DNS resolution time',
                 'groups': 'dns_latency'
               }
        
        descriptors.append(desc)

    return descriptors

if __name__ == "__main__":
    # Code to test the script w/o involving ganglia
    params = { 'googlednsa_dns_resolution': 'google-public-dns-a.google.com google.com A',
               'googlednsb_dns_resolution': 'google-public-dns-b.google.com google.com A',
             }
    descriptors = metric_init(params)
    for desc in descriptors:
        latency = desc['call_back'](desc['name'])
        metric, dns_server, domain, rrec = desc['name'].split("_")
        print "It took %f to resolve %s on %s" % (latency, domain, dns_server)
