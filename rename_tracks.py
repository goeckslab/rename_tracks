# -*- coding: utf8 -*-

"""
Rename the custom evidence tracks so that the tracks use the same sequence names as the renamed reference 
"""
import sys
import csv
import subprocess

def rename_interval(inputFile, nameDict, renamedFile):
    writer = open(renamedFile, 'w')
    with open(inputFile, 'r') as f:
        lines = f.readlines()
        for l in lines:
            if not l.startswith("#"):
                scaffold_name = l.split()[0]
                if scaffold_name in nameDict:
                    l = l.replace(scaffold_name, nameDict[scaffold_name])
            writer.write(l)
    writer.close()

def rename_bam(inputFile, nameDict, renamedFile):
    header = subprocess.Popen(['samtools', 'view', '-H', inputFile], stdout=subprocess.PIPE)
    array_call = ['sed']
    for k,v in nameDict.items():
        substitute = "s/%s/%s/" % (str(k), str(v))
        array_call.append('-e')
        array_call.append(substitute)
    reheader = subprocess.Popen(array_call, stdin=header.stdout, stdout=subprocess.PIPE)
    out = open(renamedFile, 'w')
    subprocess.Popen(['samtools', 'reheader', '-', inputFile], stdin=reheader.stdout, stdout=out)
   
def getNameDict(nameMapping):
    nameDict = {}
    with open(nameMapping, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            nameDict[row[0]] = row[1]
    return nameDict

def main():
    inputFile = sys.argv[1]
    nameMapping = sys.argv[2]
    inputFormat = sys.argv[3]
    outputfile = sys.argv[4]
    nameDict = getNameDict(nameMapping)
    if inputFormat == "bed" or inputFormat == "gff3" or inputFormat == "gtf":
        rename_interval(inputFile, nameDict, outputfile)
    elif inputFormat == "bam":
        rename_bam(inputFile, nameDict, outputfile)

if __name__ == "__main__":
    main()