"""
Script written by Arnold DECHAMPS for the RIPE LABS article :
"""
import io, re
import dns.resolver
import dns.rrset
import asyncio
from dns.asyncresolver import Resolver
from typing import Tuple


def filemanager():
    """
    Opens the file and reads every line to a list
    :returns the list of all lines:
    """
    dbobjects = io.open("ripe.db.domain", "r", encoding='latin-1')
    rawlines = dbobjects.readlines()
    for i in range(len(rawlines)):
        rawlines[i] = rawlines[i].strip("\n")
    return rawlines


def sorter(rawlines):
    """
    Takes the Data of all the object lines and makes them processable in a form of list/dictionary
    :param rawlines:
    :return sorted-data:
    """
    objects = []
    dns = []
    dnssec = []
    for line in rawlines:
        if re.match(r'^\s*domain:', line) is not None:
            if len(dns) != 0:
                objects.append({"domain": domain, "nameserver": dns, "dnssec": dnssec})
                dnssec = []
                dns = []
            domain = line.replace("domain:         ", "")
        elif re.match(r'^\s*nserver:', line) is not None:
            dns.append(line.replace("nserver:        ", ""))
        elif re.match(r'^\s*ds-rdata:', line) is not None:
            dnssec.append(line.replace("ds-rdata:       ", ""))
    return objects


def statmaker(sorteddata):
    """
    makes statistics on the objects
    :param sorteddata:
    :return int with non-dnssec objects
    """
    dnssecenabled = 0
    for object in sorteddata:
        if len(object["dnssec"]) > 0:
            dnssecenabled += 1
    return dnssecenabled


async def dns_query(domain: str, rtype: str = 'A', **kwargs) -> dns.rrset.RRset:
    kwargs, res_cfg = dict(kwargs), {}
    rs = Resolver(**res_cfg)
    res: dns.resolver.Answer = await rs.resolve(domain, rdtype=rtype, **kwargs)
    return res.rrset


async def dns_bulk(*queries: Tuple[str, str], **kwargs):
    ret_ex = kwargs.pop('return_exceptions', True)
    coros = [dns_query(dom, rt, **kwargs) for dom, rt in list(queries)]
    return await asyncio.gather(*coros, return_exceptions=ret_ex)


async def dnstest(queries):
    success = 0
    res = await dns_bulk(*queries)
    for i, a in enumerate(res):
        if isinstance(a, Exception):
            print(
                f" [!!!] Error: Result {i} is an exception! Original query: {queries[i]} || Exception is: {type(a)} - {a!s} \n")
            continue
        else:
            success += 1
    return success


def dnstester(sorteddata):
    """
    Takes the data and tests the DNS servers
    """
    queries = []
    working = 0
    runs = 0
    status = 0
    for object in sorteddata:
        if runs == 10000:
            runs = 0
            working = working + asyncio.run(dnstest(queries))
            print("object : " + str(status))
            queries = []
            queries.append((object["domain"], "SOA"))
        else:
            runs += 1
            queries.append((object["domain"], "SOA"))
        status += 1
        if status == len(sorteddata):
            working = working + asyncio.run(dnstest(queries))
            print("done")
    return working


def main():
    """
    main function
    :nothing:
    """
    data = sorter(filemanager())
    dnssec = statmaker(data)
    operational = dnstester(data)
    print("These are the test results :")
    print("Total amount of objects      : " + str(len(data)))
    print("Total amount of working ones : " + str(operational))
    print("Total with DNSSEC enabled    : " + str(dnssec))


if __name__ == '__main__':
    main()
