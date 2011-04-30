#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import sys

def pairvote(csv, ridings_file="ridings.csv"):
    engine = PairingEngine(ridings_file)
    engine.pair(csv)

def log(*args):
    return
    print >>sys.stderr, ' '.join([repr(a) for a in args])
    
class PairingEngine:
    def __init__(self, ridings_file="rankedridings.csv"):
        self.empty_will_vote = []
        self.swing_ridings = {}
        self.party_ridings = {}
        self.parties = ["GREEN", "LIBERAL", "NDP", "BLOC"]
        self.pairs = []
        
        self._init_ranked_ridings(ridings_file)
    
    def _init_ranked_ridings(self, ridings_file):
        # First, populate the dictionary of party ridings with empty lists
        for p in self.parties:
            self.party_ridings[p] = []
            
        # read all ridings from the csv file
        ranked_ridings_csv = csv.reader(open(ridings_file,"rb"))
        #self.ranked_ridings = [row for row in ranked_ridings_csv]   

        for row in ranked_ridings_csv:
            riding = row[1].strip().upper()
            self.party_ridings[row[0]].append(riding)
            if not self.swing_ridings.has_key(riding):
                self.swing_ridings[riding] = True
        
    # make sure preferred party is not on will vote list 
    def check_voter(self, voter):
        voter['willing'] = voter['willing'].split(',')
        if voter['preferred'] in voter['willing']:
            voter['willing'].remove(voter['preferred'])
            if len(voter['willing']) == 0:
                self.empty_will_vote.append(voter)
                voter['problem'] = 'Y'
                       
    def parse_test_row(self, row, count):
        log(row)
        
        voter = { 'riding': row[5].upper(), 'preferred': row[6], 'willing': row[7], 'paired': row[9],
                      'commit':'','name':row[2],'email':row[3],'form':row[0],'date':row[1],
                      'sequential':row[11], 'pair':row[12],'telephone':row[8],'postal':row[4],'problem':row[10]}
        
        return voter
    
    def parse_spreadsheet_row(self, row, count):
        log(row)
        
        voter = { 'riding': row[9].upper(), 'preferred': row[6], 'willing': row[10], 'paired': '',
                      'commit':'','name':row[1] + ' ' + row[2],'email':row[0],'form':'','date':'',
                      'sequential':count, 'pair':'','telephone':'','postal':5,'problem':''}
        
        return voter
        
    def pair_voters(self, swing, pairee, swing_party):
        self.pairs.append((swing, pairee))
        swing['paired'] = 'Y'
        swing['commit'] = swing_party
        swing['pair'] = pairee['sequential']
        pairee['paired']='Y'
        pairee['commit'] = swing['preferred']
        pairee['pair'] = swing['sequential']

    def find_match(self, party, riding, swinger, candidates):
        for candidate in candidates:
            if candidate['riding'] == riding: continue
            if candidate['preferred'] != party: continue              
            if candidate['paired'] == 'Y' or candidate['problem'] == 'Y': continue      
            if swinger['preferred'] in candidate['willing']: 
                self.pair_voters(swinger, candidate, party)                            
                return True

        return False
         
    def pair(self, csv_data=None):
        non_swing_voters = []
        swing_voters = []
        
        # create list of voter dictionaries for clear access to column names
        if csv_data:
            voters_csv = csv.reader(csv_data.split("\n"))
            voters_csv.next()
            parse_f = self.parse_test_row
        else:
            voters_csv = csv.reader(open("pairvoterlist.csv","rb"))
            voters_csv.next()
            parse_f = self.parse_spreadsheet_row
            
        count = 0
        for row in voters_csv:
            if not row:
                continue
            
            count += 1
            voter = parse_f(row, count)
            
            if self.swing_ridings.has_key(voter['riding']):
                voter['swing'] = 'Y'
                swing_voters.append(voter)
            else:
                voter['swing'] = 'N'
                non_swing_voters.append(voter)
        
        for voter in swing_voters:
            self.check_voter(voter)
                
            # Check to see if they already prefer to vote for our party pick
            # in their swing riding
            if voter['problem'] != 'Y' and self.party_ridings.has_key(voter['preferred']):
                for riding in self.party_ridings[voter['preferred']]:
                    if riding == voter['riding']:
                        self.pair_voters(voter, voter, voter['preferred'])
                                                       
        for voter in non_swing_voters:
            self.check_voter(voter)
                    
        # start pairing process
        for party in self.parties:
            for riding in self.party_ridings[party]:  
                matched = False   
                # Loop through the swing riding for current party.  If they are unpaired, try to find them a match.             
                for sv in [v for v in swing_voters if v['riding'] == riding and v['paired'] != 'Y' and v['problem'] != 'Y']:
                    if not party in sv['willing']: continue
                    # Look through the rest of the swing voters and see if we can find a match                    
                    matched = self.find_match(party, riding, sv, swing_voters)
                    # if we couldn't find a match, check the non-swing-voters
                    if not matched:
                        self.find_match(party, riding, sv, non_swing_voters)
                            
        # we are done, spit results
        f = open('pairings.csv', 'wb')
        writer = csv.writer(f)

        for pair in self.pairs:
            def extractpair(pair):
                return [pair['name'], pair['email'], pair['riding'], pair['commit'], pair['swing']]
            writer.writerow(extractpair(pair[0]) + extractpair(pair[1]))
        f.close()
        
        updated_voters = []
        for v in swing_voters + non_swing_voters:
             updated_voters.append([v['form'], v['date'], v['name'], v['email'], v['postal'], v['riding'], v['preferred'],
                ','.join(v['willing']), v['telephone'], v['paired'], v['problem'], v['sequential'], v['pair']])
                
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
