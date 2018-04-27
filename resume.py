import survey as s
import pickle


def resume_from(number=-1, results=None):
    # note the resume point is the paper number instead of line number
    if number == -1:
        with open('resume_point.log') as f:
            number = int(f.readline())

    if not results:
        with open('{}.pickle'.format(s.file_name), 'rb') as f:
            results = pickle.load(f)

    print('resuming from paper # {}'.format(number))
    for index, paper in enumerate(results[number:]):
        s.update_pickle(fn=s.file_name, line_number=number + index)

    s.pickle2excel(s.file_name)
    return results


if __name__ == '__main__':
    r = resume_from(-1)



