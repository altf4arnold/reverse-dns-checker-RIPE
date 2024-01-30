from dns.asyncresolver import Resolver
import dns.resolver
import dns.rrset
import asyncio
from typing import Tuple


async def dns_query(domain: str, rtype: str = 'A', **kwargs) -> dns.rrset.RRset:
    kwargs, res_cfg = dict(kwargs), {}
    # extract 'filename' and 'configure' from kwargs if they're present
    # to be passed to Resolver. we pop them to avoid conflicts passing kwargs
    # to .resolve().
    if 'filename' in kwargs: res_cfg['filename'] = kwargs.pop('filename')
    if 'configure' in kwargs: res_cfg['configure'] = kwargs.pop('configure')

    # create an asyncio Resolver instance
    rs = Resolver(**res_cfg)

    # call and asynchronously await .resolve() to obtain the DNS results
    res: dns.resolver.Answer = await rs.resolve(domain, rdtype=rtype, **kwargs)

    # we return the most useful part of Answer: the RRset, which contains
    # the individual records that were found.
    return res.rrset


async def dns_bulk(*queries: Tuple[str, str], **kwargs):
    ret_ex = kwargs.pop('return_exceptions', True)

    # Iterate over the queries and call (but don't await) the dns_query coroutine
    # with each query.
    # Without 'await', they won't properly execute until we await the coroutines
    # either individually, or in bulk using asyncio.gather
    coros = [dns_query(dom, rt, **kwargs) for dom, rt in list(queries)]

    # using asyncio.gather, we can effectively run all of the coroutines
    # in 'coros' at the same time, instead of awaiting them one-by-one.
    #
    # return_exceptions controls whether gather() should immediately
    # fail and re-raise as soon as it detects an exception,
    # or whether it should just capture any exceptions, and simply
    # return them within the results.
    #
    # in this example function, return_exceptions is set to True,
    # which means if one or more of the queries fail, it'll simply
    # store the exceptions and continue running the remaining coros,
    # and return the exceptions inside of the tuple/list of results.
    return await asyncio.gather(*coros, return_exceptions=ret_ex)


async def main():
    queries = [
        ('adechamps.net', 'AAAA'),
        ('adechamps.net', 'TXT'),
        ('google.com', 'A'),
        ('google.com', 'AAAA'),
        ('examplesitedoesnotexist.test', 'A'),
    ]
    print(f"\n [...] Sending {len(queries)} bulk queries\n")
    res = await dns_bulk(*queries)
    print(f"\n [+++] Got {len(res)} results! :)\n\n")

    for i, a in enumerate(res):
        print("\n------------------------------------------------------------\n")
        if isinstance(a, Exception):
            print(f" [!!!] Error: Result {i} is an exception! Original query: {queries[i]} || Exception is: {type(a)} - {a!s} \n")
            continue
        print(f" [+++] Got result for query {i} ( {queries[i]} )\n")
        print(f"  >>>  Representation: {a!r}")
        print(f"  >>>  As string:")
        print(f"    {a!s}")
        print()
    print("\n------------------------------------------------------------\n")

asyncio.run(main())