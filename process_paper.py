import pandas as pd
import re
from selenium import webdriver
import time


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


def citatons_google(fn):
    file_to_save = 'updated_citations.xlsx'

    b = webdriver.Chrome()
    b.get('https://scholar.google.com.hk/')
    blank_keys = b.find_element_by_css_selector('form>div>input')
    button_submit = b.find_element_by_css_selector('form>button')
    df = pd.read_excel(fn)
    for i, r in df.iterrows():
        title = r['title'].replace('\n', ' ')
        df.loc[i, 'title'] = title
        blank_keys.send_keys(title)
        button_submit.click()
        time.sleep(10)
        if '验证' in b.page_source:
            time.sleep(200)
        result_box = b.find_elements_by_css_selector('div#gs_res_ccl_mid>div')
        if len(result_box) == 1:
            print('#{}, found the paper: {}'.format(i, title), end=' ')
            info = result_box[0].find_elements_by_css_selector('div.gs_fl>a')
            try:
                citation_no = info[2].text.split('：')[-1]
                citation_no = int(citation_no)
                print('with citations {}'.format(citation_no))
            except:
                print('found no citations')
                citation_no = 0

            citation_no_previous = int(r['citation_count'])
            if not citation_no == citation_no_previous:
                df.loc[i, 'citation_count'] = citation_no
                print('#{}, found the paper: {}'.format(i, title), end=' ')
                print('with citations {}'.format(citation_no))

        blank_keys = b.find_element_by_css_selector('form>div>input')
        blank_keys.clear()
        button_submit = b.find_element_by_css_selector('form>button')
        time.sleep(100)

    df.to_excel(file_to_save, index=False)


if __name__ == '__main__':
    # filter_keywords()
    # filter_abstract()
    citatons_google(file_abstract)



