"""
Script written by Arnold DECHAMPS for the RIPE LABS article :
"""
import io, re
import dns.resolver


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
            domain = line.lstrip("domain:         ")
        elif re.match(r'^\s*nserver:', line) is not None:
            dns.append(line.lstrip("nserver:        "))
        elif re.match(r'^\s*ds-rdata:', line) is not None:
            dnssec.append(line.lstrip("ds-rdata:       "))
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

def dnstester(sorteddata):
    """
    Takes the data and tests the DNS servers
    """
    working = 0
    for object in sorteddata:
        try:
            dns.resolver.resolve(object["domain"], "SOA")
            working += 1
        except Exception as e:
            print(e)
            print(object["domain"] + " Not Working !")
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
