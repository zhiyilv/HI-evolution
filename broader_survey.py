import survey as s
import resume
import pickle


with open('{}.pickle'.format(s.file_name), 'rb') as f:
    results = pickle.load(f)

# resume point
start = len(results)
print('found {} existing papers...'.format(start-1))

# search criteria
input_at_least_one = ['air', 'environment', 'hazards', 'pollution']
input_all_words = 'happiness measurement'
search_result_page = s.search_springer(keys_all_words=input_all_words,
                                       keys_least_words=input_at_least_one)
srs = s.parse_search_results(search_result_page)
print('there are {} papers found for this search'.format(len(srs)))

# filter those already collected
already = [i[0] for i in results[1:]]  # those have already collected
srs_filtered = [sr for sr in srs if sr[0] not in already]
results = [*results, *srs_filtered]
print('added {} papers'.format(len(srs_filtered)))

# resume collection
print('resume collecting...')
results = resume.resume_from(number=start, results=results)






