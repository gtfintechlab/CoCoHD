import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# reading txt files into dataframe of words
transcripts_dir = '/home/congress-user/data_collection/transcripts'
transcripts_df = pd.DataFrame(columns=['date','hearing_num','title','subcommittee','content','present_member','present_staff'])

for subdir, dirs, files in os.walk(transcripts_dir):
    for file in files:
        date, hearing_num = str(file).split('.')[0].split('_')
        date_obj = datetime.strptime(date,'%Y-%m-%d')
        if date_obj >= datetime.strptime('2000-01-01','%Y-%m-%d'):
            # title = titles[titles['serial no.'] == hearing_num]['title'].values[0]
            file_path = os.path.join(subdir,file)
            file = open(file_path,'r')
            full_file = "".join(file.readlines())
            
            # unorganized file omit
            if '[TEXT NOT AVAILABLE REFER TO PDF]' in full_file:
                # example: 116-65
                continue
            elif '[TEXT NOT AVAILABLE]' in full_file:
                # example: 112-132
                continue
            elif '<TEXT NOT AVAILABLE>' in full_file:
                # example: 110-127
                continue
            elif '[NO TEXT AVAILABLE]' in full_file:
                # example: 112-119
                continue
            elif '<TEXT NOT AVAILABLE IN TIFF FORMAT>' in full_file:
                # example: 109-53
                continue
            elif '<TEXT FILE NOT AVAILABLE IN WAIS FORMAT>' in full_file:
                # example: 109-61
                continue
            elif '(Text Not Available In WAIS Format)' in full_file:
                # example: 109-63
                continue
            # elif '[GRAPHIC] [TIFF OMITTED]' in full_file:
            #     # example: 107-82
            #     continue
            # elif '[GRAPHIC(S) NOT AVAILABLE IN TIFF FORMAT]' in full_file:
            #     # example: 112-166
            #     continue
            elif '[ERRATA]' in full_file:
                # example: 109-131
                continue
                
            # extract file title
            try:
                title = full_file.split('<title> -',1)[1].split('</title>')[0].strip()
            except:
                title = ''

            # extract subcommittee
            file_split = full_file.split('COMMITTEE ON ENERGY AND COMMERCE')[0].split('SUBCOMMITTEE ON')
            if len(file_split) == 1:
                subcommittee = ''
            else:
                subcommittee = file_split[1].lower().replace('of the','').replace('\n','').strip()
                if 'committee' in subcommittee:
                    subcommittee = subcommittee.split('committee')[0]
                # if 'committee on energy and commerce house of representatives'
                subcommittee = re.sub(' +', ' ', subcommittee)

            # extract content
            if 'OPENING STATEMENT OF' in full_file:
                content = ''.join(full_file.split('OPENING STATEMENT OF')[1:])
                # content = 'OPENING STATEMENT OF' + content
            elif 'Prepared Statement of' in full_file:
                content = ''.join(full_file.split('Prepared Statement of')[1:])
                # content = 'Prepared Statement of' + content
            else:
                content = ''
                
            # extract member list
            # present members
            if 'Members present:' in full_file:
                members = full_file.split('Members present: ',1)[1]
                if 'Members present:' in members:
                    # example: 109-15 (two days hearing)
                    member1 = members.split('.',1)[0]
                    member2 = members.split('Members present: ',1)[1]
                    members = member1+','+member2
            elif 'Member present:' in full_file:
                members = full_file.split('Member present:',1)[1]
            elif 'Members present from' in full_file:
                members = full_file.split('Members present from',1)[1]
                members = members.split(":",1)[1]
            elif 'Present from' in full_file:
                members = full_file.split('Present from',1)[1]
                members = members.split(":",1)[1]
            elif 'Members resent:' in full_file:
                members = full_file.split('Members resent:',1)[1]
            elif 'Members praesent:' in full_file:
                members = full_file.split('Members praesent:',1)[1]
            elif 'Present:' in full_file:
                members = full_file.split('Present: ',1)[1]
            else:
                # examples: 107-143, 110-141
                present_member = ''
                present_staff = ''
                transcripts_df.loc[len(transcripts_df.index)] = [date, hearing_num, title, subcommittee, content, present_member, present_staff]
                continue
            
            # present staffs
            if 'Staff present:' in members:
                present_member = members.split('Staff present:')[0]
                present_staff = members.split('Staff present:')[1].split('.',1)[0]
            elif 'Staff Present:' in members:
                present_member = members.split('Staff Present:')[0]
                present_staff = members.split('Staff Present:')[1].split('.',1)[0]
            else:
                # members = members.replace('Also present:',)
                if 'Also present:' in members:
                    temp_members = members.split('Also present:')[0]
                    also_present = 'Also present:'+ members.split('Also present:')[1].split('.',1)[0]
                    present_member = temp_members + also_present
                    present_staff = ''
                else:
                    present_member = members.split('.',1)[0]
                    present_staff = ''
            
            # present members
            present_member = present_member.replace('Representatives','').replace('and','').replace(';','').replace('\n','').replace('Representative','')
            if 'Also present:' in present_member:
                member1 = present_member.split('Also present:')[0].strip().replace('.',',')
                member2 = present_member.split('Also present:')[1].strip()
                present_member = member1+member2
            elif 'Also Present:' in present_member:
                member1 = present_member.split('Also Present:')[0].strip().replace('.',',')
                member2 = present_member.split('Also Present:')[1].strip()
                present_member = member1+member2
            present_member = present_member.split(',')
            present_member = [m.replace('.','').strip() for m in present_member]
            
            # present staffs
            present_staff = present_staff.replace('and','').replace('\n','')
            present_staff = present_staff.split(';')
            # present_staff = [m.strip() for m in present_staff]
            present_staff = [tuple(m.strip().split(',')) for m in present_staff]
            # for i in range(len(present_staff)):
            #     # edge case: misuse of ','
            #     if len(present_staff[i]) > 2:
            #         print(file_path)
            #         print(present_staff[i])
            
            # print(content)
            # lines = [re.subn(r'[^A-Za-z0-9 ]+','',line.strip())[0].split(' ') for line in file.readlines() if line.strip()]
            # print(lines)
            # words = [item for sublist in lines for item in sublist]
            
            transcripts_df.loc[len(transcripts_df.index)] = [date, hearing_num, title, subcommittee, content, present_member, present_staff]  

# subcommittee cleaning
# create a list text
text = list(transcripts_df['subcommittee'])

# preprocessing loop
lemmatizer = WordNetLemmatizer()
corpus = []

for i in range(len(text)):
    r = re.sub('[^a-zA-Z]', ' ', text[i])
    r = r.lower().split()
    r = [word for word in r if word not in stopwords.words('english')]
    r = [lemmatizer.lemmatize(word) for word in r]
    r = ' '.join(r)
    corpus.append(r)

#assign corpus to data['text']
transcripts_df['subcom_corpus'] = corpus
# transcripts_df[transcripts_df['subcom_corpus'].str.contains('energy')]['subcom_corpus'] = 'energy'
conditions= [(transcripts_df['subcom_corpus'].str.contains('energy') | transcripts_df['subcom_corpus'].str.contains('enegy')),
             transcripts_df['subcom_corpus'].str.contains('health'),
             (transcripts_df['subcom_corpus'].str.contains('communication') | transcripts_df['subcom_corpus'].str.contains('communicatons')),
             transcripts_df['subcom_corpus'].str.contains('environment'),
             (transcripts_df['subcom_corpus'].str.contains('commerce') | transcripts_df['subcom_corpus'].str.contains('trade')),]
choices = ['energy','health','communication','environment','commerce']
transcripts_df['subcom_corpus'] = np.select(conditions, choices,default=transcripts_df['subcom_corpus'])

transcripts_df = transcripts_df.drop(columns={'subcommittee'})
transcripts_df = transcripts_df.rename(columns={'subcom_corpus':'subcom'})
# transcripts_df.to_csv('transcripts.csv')