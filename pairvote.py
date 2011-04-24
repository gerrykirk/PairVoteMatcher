#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import sys

def pairvote(csv):
    engine = PairingEngine()
    engine.pair(csv)

def log(*args):
    return
    print >>sys.stderr, ' '.join([repr(a) for a in args])
    
class PairingEngine:
    # initialize lists for storing results
    empty_will_vote = []
    ordered_ridings = []
    party_ridings = {}

    # list of all the parties, must be in same order as the columns in
    # rankedridings.csv
    parties = ["Liberal","NDP","Green"]

    def __init__(self):
        self._init_ranked_ridings()
    
    def _init_ranked_ridings(self):
        # First, populate the dictionary of party ridings with empty lists
        for p in self.parties:
            self.party_ridings[p] = []
            
        # read all ridings from the csv file
        ranked_ridings_csv = csv.reader(open("rankedridings.csv","rb"))
        #self.ranked_ridings = [row for row in ranked_ridings_csv]   

        for row in ranked_ridings_csv:
            self.party_ridings[row[0]].append(row[1])
            
            # I'm not sure yet how ordered_ridings will work in the new version of the algorithm
            self.ordered_ridings.append(row[1])
        
    def pair(self, csv_data=None):
        # create list of voter dictionaries for clear access to column names
        if csv_data:
            voters_csv = csv.reader(csv_data.split("\n"))
            voters_csv.next()
        else:
            voters_csv = csv.reader(open("pairvoterlist.csv","rb"))
        
        voters = []
        pairs = []
        
        # sequential = 0
        # sequentials = {}
        
        for row in voters_csv:
            if not row:
                continue
                
            row_data = { 'riding': row[5].upper(), 'preferred': row[6], 'willing': row[7], 'paired': row[9],
                          'commit':'','name':row[2],'email':row[3],'form':row[0],'date':row[1],
                          'sequential':row[11],    'pair':row[12],'telephone':row[8],'postal':row[4],'problem':row[10]}
            log(row)
            # if row_data['sequential']:
            #     sequentials[row_data['sequential']] = 1
            # else:
            #     while sequentials.has_key(sequential):
            #         seq
            voters.append(row_data)
            # print >>sys.stderr, repr(row_data)

        # make sure preferred party is not on will vote list 
        for voter in voters:
            voter['willing']=voter['willing'].split(',')
            if voter['preferred'] in voter['willing']:
                voter['willing'].remove(voter['preferred'])
                if voter['willing']==[]:
                    self.empty_will_vote.append(voter)
                    voter['problem']='Y'

        # start pairing process
        log(repr(self.ordered_ridings))
        for party,riding in self.ordered_ridings:
            # willing voters must be on the party's riding, still not
            # paired and willing to vote for this party
            willing_voters = [voter for voter in voters if (party in voter['willing']) and (voter['riding']==riding) and (voter['paired']=='') and (voter['problem']!='Y')]
    
            if willing_voters: 
                names = [guy['name'] for guy in willing_voters]
                log((party, riding), names)

            for willing_voter in willing_voters:
                # possible pairings include someone in a swing riding of
                # willing voter's preferred party willing to vote for it
                if voter['preferred'] == 'Pick one':
                    swing_possible_pairings = []
                else:
                    swing_possible_pairings = [voter for voter in voters if (voter['preferred']==party) and (voter['riding'] in self.party_ridings[willing_voter['preferred']]) and (voter['riding']!=riding) and (willing_voter['preferred'] in voter['willing']) and (voter['paired']=='') and (voter['problem']!='Y')]

                if swing_possible_pairings!=[]:
                    pairs.append((willing_voter,swing_possible_pairings[0]))
                    willing_voter['paired']='Y'
                    willing_voter['commit']=party
                    willing_voter['swing']='Y'
                    willing_voter['pair']=swing_possible_pairings[0]['sequential']
                    swing_possible_pairings[0]['paired']='Y'
                    swing_possible_pairings[0]['swing']='Y'
                    swing_possible_pairings[0]['commit']=willing_voter['preferred']
                    swing_possible_pairings[0]['pair']=willing_voter['sequential']

        # we are done, spit results
        f = open('pairings.csv', 'wb')
        writer = csv.writer(f)
        #print pairs
        for pair in pairs:
            def extractpair(pair):
                return [pair['name'], pair['email'], pair['riding'], pair['preferred'], pair['swing']]
            writer.writerow(extractpair(pair[0]) + extractpair(pair[1]))
        f.close()
        
        #print
        #print "Pairings made"
        #print "-------------"
        #print "'Voter A Name','Voter A Email','Voter A Riding','Voter A Party','Voter A Swing','Voter B Name','Voter B Email','Voter B Riding','Voter B Party','Voter B Swing'"
        #for pair in pairs:
        #    print "'%(name)s','%(email)s','%(riding)s','%(preferred)s','%(swing)s'" % pair[0],
        #    print "'%(name)s','%(email)s','%(riding)s','%(preferred)s','%(swing)s'" % pair[1]

        # write updated csv
        
        updated_voters=[ [voter['form'],voter['date'],voter['name'],voter['email'],
                voter['postal'],voter['riding'],voter['preferred'],
                ','.join(voter['willing']),voter['telephone'],voter['paired'],voter['problem'],
                voter['sequential'],voter['pair']] for voter in voters]
        if csv_data:
            fp = sys.stdout
        else:
            fp = open("pairingresults.csv", "wb")
            
        writer = csv.writer(fp)
        writer.writerows(updated_voters)

def main():
    engine = PairingEngine()
    engine.pair()
    
if __name__ == "__main__":
    main()
