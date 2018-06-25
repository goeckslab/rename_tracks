# -*- coding: utf8 -*-

"""
Rename the custom evidence tracks so that the tracks use the same sequence names as the renamed reference 
"""
import sys
import csv
import subprocess
import tempfile

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

def rename_bigwig(inputFile, renamedReference, nameDict, renamedFile):
    bedGraphFile = tempfile.NamedTemporaryFile(bufsize=0)
    chrom_sizes = tempfile.NamedTemporaryFile(bufsize=0)
    sorted_bedGraphFile = tempfile.NamedTemporaryFile(bufsize=0)
    renamed_sorted_bedGraphFile = tempfile.NamedTemporaryFile(bufsize=0)

    subprocess.call(['bigWigToBedGraph', inputFile, bedGraphFile.name])
    subprocess.call(['faSize', '-detailed', '-tab', renamedReference], stdout=chrom_sizes)
    subprocess.call(['sort', '-k1,1', '-k2,2n', bedGraphFile.name], stdout=sorted_bedGraphFile)
    rename_interval(sorted_bedGraphFile.name, nameDict, renamed_sorted_bedGraphFile.name)
    subprocess.call(['bedGraphToBigWig', renamed_sorted_bedGraphFile.name, chrom_sizes.name, renamedFile])
   
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
    elif inputFormat == "bigwig":
        renamedReference = sys.argv[5]
        rename_bigwig(inputFile, renamedReference, nameDict, outputfile)

if __name__ == "__main__":
    main()