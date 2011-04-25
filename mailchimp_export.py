import csv

# There is a fair bit of duplicated code from pairvote.py that I plan to refactor/cleanup
# but I'm just doing this quickly so we can test the export for use in mailchimp.

parties = ["GREEN", "LIBERAL", "NDP", "BLOC"]

# First, read in list of swing ridings
swing_ridings = {}

ranked_ridings_csv = csv.reader(open("rankedridings.csv","rb"))        
for row in ranked_ridings_csv:
    riding = row[1].strip().upper()
    if not swing_ridings.has_key(riding):
        swing_ridings[riding] = row[0]
        
# Second, read in the master list of voters.
def parse_row(row, count):
    riding = row[9].upper()
    swinger = True if swing_ridings.has_key(riding) else False
    voter = { 'riding': riding, 'preferred': row[6], 'willing': row[10], 'paired': '',
                  'commit':'','firstname' : row[1], 'lastname' : row[2],'email':row[0],'form':'','date':'',
                  'sequential':count, 'pair':'','telephone':'','postal':5,'problem':'',
                  'swinger' : swinger}

    return voter
    
voters = {}
voters_csv = csv.reader(open("pairvoterlist.csv","rb"))
voters_csv.next()

count = 0
for row in voters_csv:
    if not row:
        continue
    
    count += 1
    voter = parse_row(row, count)
    voters[voter['email']] = voter
    
# Third, read in the list of paired voters
pairs = []
paired_voters_csv = csv.reader(open("pairings.csv", "rb"))
for row in paired_voters_csv:
    swinger = { 'riding' : row[2], 'email' : row[1], 'voting-for' : row[3]}
    non_swinger = { 'riding' : row[7], 'email' : row[6], 'voting-for' : row[8]}
    pairs.append( (swinger, non_swinger) )

print "Participant Email, Participant Party Vote, Riding Swing Status, Pairee Email, Pairee First Name, Pairee Lastname, Pairing Riding, Pairee Riding Swing Status, Pairee Party Vote"

for pair in pairs:
    swing = pair[0]
    pairee = pair[1]

    print swing['email'], ',', swing['voting-for'], ',swing,', 
    
    if swing['email'] == pairee['email']:
        print '-,,,,,'
    else:
        vp = voters[pairee['email']]
        print pairee['email'], ',', vp['firstname'], ',', vp['lastname'], ',', vp['riding'], ',nonswing,', pairee['voting-for']
