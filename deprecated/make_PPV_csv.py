#!/usr/bin/env python

'''
Only compares identically named .CT files between directory to get the PPV between the RNA structures.
Calls scorer iteratively on all such files and puts the output in a simple .csv
Only works if the -mfe option was selected during folding; impossible to calculate PPV between multiple structure (for now).
'''

#Imports
import os
import subprocess
import argparse

def get_symmetrical_files(dir_accepted,dir_predicted):
    '''return a set of files wherein both exist and can be scored against each other.'''
    control,treatment = set(os.listdir(dir_accepted)),set(os.listdir(dir_predicted))
    true_iteration = control.intersection(treatment)
    return true_iteration

def get_symmetrical_files_suffixes(dir_accepted,suffix_accepted,dir_predicted,suffix_predicted):
    '''Looks for congruent files of different names between directories'''
    control,treatment = os.listdir(dir_accepted),os.listdir(dir_predicted)
    control_2, treatment_2 = set([x.replace(suffix_accepted,'') for x in control]),set([y.replace(suffix_predicted,'') for y in treatment])
    true_iteration = control_2.intersection(treatment_2)
    return true_iteration

def score_spammer(fyles,dir_accepted,dir_predicted,out_suffix='.txt'):
    '''Call the RNAstructure scorer between two directories, save to an out directory'''
    os.mkdir('Out')
    for fyle in fyles:
        outfile = fyle.split('_')[0]+out_suffix
        subprocess.call(' '.join(['scorer',dir_predicted+'/'+fyle,dir_accepted+'/'+fyle,'Out/'+outfile]),shell=True)

def score_spammer_suffixes(fyle_prefixes,dir_accepted,suffix_accepted,dir_predicted,suffix_predicted,out_suffix='.txt'):
    '''Call the RNAstructure scorer between two directories, save to an out directory'''
    os.mkdir('Out')
    for fyle_prefix in fyle_prefixes:
        outfile = fyle_prefix + out_suffix
        subprocess.call(' '.join(['scorer',dir_predicted+'/'+fyle_prefix+suffix_predicted,dir_accepted+'/'+fyle_prefix+suffix_accepted,'Out/'+outfile]),shell=True)

def generate_stitched_file():
    '''Iterate through the directory, read in all the PPVs and sensitivies'''
    x_dict = {}
    os.chdir('Out')
    for fyle in os.listdir('.'):
        with open(fyle) as f:
            content = f.readlines()
            sensitivity,PPV = content[3].strip().split()[-1][:-1],content[4].strip().split()[-1][:-1]
            if sensitivity == '-nan':
                sensitivity = 'NA'
            if PPV == '-nan':
                PPV = 'NA'
            x_dict[fyle[:-4]] = (sensitivity,PPV)
    os.chdir('..')
    return x_dict
    
def dump_stats_dict(adict,outfyle='stats.csv'):
    '''Dumps the dictionary to a flat file'''
    with open(outfyle,'w') as f:
        f.write(','.join(['transcript','sensitivity','PPV'])+'\n')
        for k, v in sorted(adict.items()):
            f.write(','.join([k,v[0],v[1]])+'\n')

def main():
    print ''
    print '\033[1;4;94mStructureFold2:\033[0;0;92m make_PPV_csv.py\033[0m'
    print ''
    parser = argparse.ArgumentParser(description='Compares two directories of <.ct> files and calculates PPV and Sensitivity between the MFE structures of any shared transcripts.')
    parser.add_argument('accepted', type=str, help='Accepted Structure Directory (full path)')
    parser.add_argument('predicted', type=str, help='Predicted Structure Directory (full path)')
    parser.add_argument('-n',type=str, default='stats.csv', help='<str> [default = stats.csv] outfile',dest='name')
    parser.add_argument('-suffix_1',type=str,default=None,help='Suffix from directory 1, if files do not share name')
    parser.add_argument('-suffix_2',type=str,default=None,help='Suffix from directory 2, if files do not share name')
    args = parser.parse_args()
    
    if not args.suffix_1 and not args.suffix_2:
        sym_fyles = get_symmetrical_files(args.accepted,args.predicted)
        score_spammer(sym_fyles,args.accepted,args.predicted)
        stats = generate_stitched_file()
        dump_stats_dict(stats,args.name)
        subprocess.call(' '.join(['rm','-r','Out/']),shell=True)
        print ''
        print '\033[92mYour outfile \033[0m{}\033[92m contains \033[0m{}\033[92m calculated stats\033[0m'.format(args.name,str(len(stats)))
        print ''
    if args.suffix_1 and args.suffix_2:
        sym_frags = get_symmetrical_files_suffixes(args.accepted,args.suffix_1,args.predicted,args.suffix_2)
        score_spammer_suffixes(sym_frags,args.accepted,args.suffix_1,args.predicted,args.suffix_2)
        stats = generate_stitched_file()
        dump_stats_dict(stats,args.name)
        subprocess.call(' '.join(['rm','-r','Out/']),shell=True)
        print ''
        print '\033[92mYour outfile \033[0m{}\033[92m contains \033[0m{}\033[92m calculated stats\033[0m'.format(args.name,str(len(stats)))
        print ''

if __name__ == '__main__':
    main()

