import pandas as pd
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import pickle
import os


file_key = 'papers_key.xlsx'
file_abstract = 'papers_key_ab.xlsx'
keywords = ['happiness', 'subjective well-being', 'life satisfaction', 'quality of life', 'quality-of-life']
abstract = ['pollution', 'environment']


def filter_keywords():
    keywords_pattern = r"|".join(keywords)
    df_total = pd.DataFrame()
    for publisher in ['taylor', 'wiley']:  # these two are OK
        df = pd.read_excel('{}_papers.xlsx'.format(publisher))
        # print(df.shape)
        df_total = df_total.append(df, ignore_index=True)
        # print(df_total.shape)

    for publisher in ["elsevier", "springer"]:  # these two need filtering
        df = pd.read_excel('{}_papers.xlsx'.format(publisher))

        selected_idx = df.apply(lambda x: bool(re.search(keywords_pattern, str(x.keywords).lower())), axis=1)
        df = df[selected_idx]
        # print(df.shape)
        print('{}: {}'.format(publisher, df.shape))
        df_total = df_total.append(df, ignore_index=True)
        # print(df_total.shape)

    df_total.to_excel(file_key, index=False)


def filter_abstract():
    abstract_pattern = r"|".join(abstract)
    df = pd.read_excel(file_key)
    selected_idx = df.apply(lambda x: bool(re.search(abstract_pattern, str(x.abstract).lower())), axis=1)
    df = df[selected_idx]
    df.to_excel(file_abstract, index=False)


def click_with_check_bot(b, ele, df, fn):
    ele.click()
    # time.sleep(2)
    if '验证' in b.page_source:
        if input('  *already passed the check? y/n').lower() == 'y':
            save_cookies(b)
            return True
        else:
            df.to_excel(fn, index=False)
            print('!!!failed due to bot check. All info saved.')
            return False
    return True


def citations_google(fn, b=None):
    file_to_save = 'final.xlsx'

    if not b:
        b = webdriver.Chrome()
    b.get('https://scholar.google.com.hk/')
    if 'cookies.pickle' in os.listdir(os.getcwd()):
        with open('cookies.pickle', 'rb') as f:
            cookies = pickle.load(f)
        for c in cookies:
            b.add_cookie(c)
    blank_keys = b.find_element_by_css_selector('form>div>input')
    button_submit = b.find_element_by_css_selector('form>button')
    df = pd.read_excel(fn)
    # df['citations'] = pd.Series(['' for _ in range(df.shape[0])], index=df.index)
    for i, r in df.iterrows():
        if i < 128:  # resume point
            continue

        # check whether is has been crawled already
        citations_record = r['citations']
        citation_no_previous = int(r['citation_count'])
        if not pd.isnull(citations_record):
            if len(citations_record.split('\n')) == citation_no_previous:
                print('#{} has been crawled already'.format(i))
                continue

        # only deal with relevant ones
        if pd.isnull(r['relevant']):
            continue

        # deal with those with abnormal spaces
        title = ' '.join(r['title'].split())
        print('#{}, {}'.format(i, title))
        df.loc[i, 'title'] = title

        # submit query
        blank_keys.send_keys(title)
        if not click_with_check_bot(b, button_submit, df, file_to_save):
            return b, df

        # parse results
        result_box = b.find_elements_by_css_selector('div#gs_res_ccl_mid>div')
        if len(result_box) == 1:
            result_index = 0
        else:
            result_index = int(input('      *found multiple results, input the index (404 to skip): '))
            if result_index == 404:
                blank_keys = b.find_element_by_css_selector('form>div>input')
                blank_keys.clear()
                button_submit = b.find_element_by_css_selector('form>button')
                continue
        title_found = result_box[result_index].find_elements_by_css_selector('h3.gs_rt>*')
        title_found = ' '.join([i.text for i in title_found])
        print('     *found the paper: {}'.format(title_found))

        # parse the citation info
        info = result_box[result_index].find_elements_by_css_selector('div.gs_fl>a')
        citation_no = -1
        for seg in info:
            if '被引用次数' in seg.text:
                citation_no = seg.text.split('：')[-1].strip()
                citation_no = int(citation_no)
                print('     *with citations {}'.format(citation_no), end=' ')
                if not click_with_check_bot(b, seg, df, file_to_save):
                    return b, df
                break

        # update the citation count and crawl citations
        if citation_no == -1:
            print('     *with 0 citations')
            if citation_no_previous > 0:
                print('     !!! the record shows nonzero citations, manually check')
                if input('stop? no to continue. y/n ') == 'y':
                    return b, df
                else:
                    blank_keys = b.find_element_by_css_selector('form>div>input')
                    blank_keys.clear()
                    button_submit = b.find_element_by_css_selector('form>button')
                    continue
        else:
            if citation_no == citation_no_previous:
                print('     --the same citation count with record.', end=' ')
            else:
                df.loc[i, 'citation_count'] = citation_no
                print('     --updated the citation count.', end=' ')
            # crawl citations
            citations = parse_titles(b)
            try:
                next_button = b.find_element_by_css_selector('button[aria-label="下一页"]')
            except NoSuchElementException:
                next_button = None
            while next_button:
                if not click_with_check_bot(b, next_button, df, file_to_save):
                    return b, df
                citations += parse_titles(b)
                next_button = b.find_element_by_css_selector('button[aria-label="下一页"]')
                if not next_button.get_attribute('onclick'):
                    next_button = None
            df.loc[i, 'citations'] = '\n'.join(citations)
            if len(citations) == citation_no:
                print('~~citations are collected.')
                df.to_excel(file_to_save, index=False)
            else:
                print('\n\nSomething goes wrong.')
                print('\n'.join(citations))
                if input('stop? no to continue. y/n ') == 'y':
                    return b, df
                else:
                    break

        blank_keys = b.find_element_by_css_selector('form>div>input')
        blank_keys.clear()
        button_submit = b.find_element_by_css_selector('form>button')
        # time.sleep(100)

    df.to_excel(file_to_save, index=False)
    return b, df


def parse_titles(b):
    result_box = b.find_elements_by_css_selector('div#gs_res_ccl_mid>div')
    return [' '.join([j.text for j in i.find_elements_by_css_selector('h3.gs_rt> *')]) for i in result_box]


def save_cookies(b):
    cookies = b.get_cookies()
    with open('cookies.pickle', 'wb') as f:
        pickle.dump(cookies, f)


if __name__ == '__main__':
    # filter_keywords()
    # filter_abstract()
    br = webdriver.Chrome()
    # file_name = 'papers_key_ab - exclude chapter.xlsx'
    file_name = 'final.xlsx'
    br, data = citations_google(fn=file_name, b=br)



