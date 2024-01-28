"""
Script written by Arnold DECHAMPS for the RIPE LABS article :
"""
import io, re


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
    """
    totalobjects = len(sorteddata)
    dnssecenabled = 0
    for object in sorteddata:
        if len(object["dnssec"]) > 0:
            dnssecenabled += 1
    print("DNSSec configuration is :  " + str(dnssecenabled) + "/" + str(totalobjects) + " total objects.")


def main():
    """
    main function
    :nothing:
    """
    statmaker(sorter(filemanager()))

if __name__ == '__main__':
    main()
