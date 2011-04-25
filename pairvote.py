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
                       
    def candidate_voter(self, voter, party):
        return party in voter['willing'] and voter['paired'] == '' and voter['problem'] != 'Y'
    
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
        
    def pair(self, csv_data=None):
        swing_voters = {}
        non_swing_voters = []
        pairs = []
        
        # sequential = 0
        # sequentials = {}

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
                if not swing_voters.has_key(voter['riding']):
                    swing_voters[voter['riding']] = []
                swing_voters[voter['riding']].append(voter)
            else:
                # Possibly we could divide them up by who they're willing to vote for?
                non_swing_voters.append(voter)
                
        for riding in swing_voters.keys():
            for voter in swing_voters[riding]:
                self.check_voter(voter)
        for voter in non_swing_voters:
            self.check_voter(voter)
        
        # start pairing process
        for party in self.parties:
            for riding in self.party_ridings[party]:
                if not swing_voters.has_key(riding): continue
                
                # We're looking for an unmatched voter in a swing-riding willing to vote
                # for the current party.
                for swing_voter in swing_voters[riding]:
                    if not self.candidate_voter(swing_voter, party):
                        continue
                                                
                    # Now see if we can find a match in a non-swing riding
                    for voter in non_swing_voters:
                        # A valid match is a non-paired voter in a non-swing riding
                        # who is willing to vote for the swing voter's prefered party,
                        # and where the swing_voter is willing to vote for the non-swing's
                        # preferred party.
                        if self.candidate_voter(voter, swing_voter['preferred']) and self.candidate_voter(swing_voter, voter['preferred']):
                            # match!
                            pairs.append((swing_voter, voter))
                            swing_voter['paired'] = 'Y'
                            swing_voter['commit'] = party
                            swing_voter['swing'] = 'Y'
                            swing_voter['pair'] = voter['sequential']
                            voter['paired']='Y'
                            voter['swing']='Y'
                            voter['commit'] = swing_voter['preferred']
                            voter['pair'] = swing_voter['sequential']
                            break
                            
        # we are done, spit results
        f = open('pairings.csv', 'wb')
        writer = csv.writer(f)

        for pair in pairs:
            def extractpair(pair):
                return [pair['name'], pair['email'], pair['riding'], pair['commit'], pair['swing']]
            writer.writerow(extractpair(pair[0]) + extractpair(pair[1]))
        f.close()
        
        updated_voters = []
        for riding in swing_voters.keys():
            for v in swing_voters[riding]:
                updated_voters.append([v['form'], v['date'], v['name'], v['email'], v['postal'], v['riding'], v['preferred'],
                ','.join(v['willing']), v['telephone'], v['paired'], v['problem'], v['sequential'], v['pair']])
        for v in non_swing_voters:
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
