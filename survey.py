from selenium import webdriver
import time


def search_springer(keys_all_words='', keys_exact_phrase='', keys_least_words=[],
                    keys_without_words=[], keys_title=[]):
    # load the advanced search page
    mybrowser = webdriver.Chrome()
    springer_advanced = 'https://link.springer.com/advanced-search'
    mybrowser.get(springer_advanced)

    # find blanks for keywords
    blank_all_words = mybrowser.find_element_by_css_selector('input.all-words')
    blank_exact_phrase = mybrowser.find_element_by_css_selector('input.exact-phrase')
    blank_least_words = mybrowser.find_element_by_css_selector('input.least-words')
    blank_without_words = mybrowser.find_element_by_css_selector('input.without-words')
    blank_title_is = mybrowser.find_element_by_css_selector('input.title-is')

    # send keywords
    blank_all_words.send_keys(keys_all_words)
    blank_exact_phrase.send_keys(keys_exact_phrase)
    blank_least_words.send_keys(' '.join(keys_least_words))
    blank_without_words.send_keys(' '.join(keys_without_words))
    blank_title_is.send_keys(' '.join(keys_title))
    time.sleep(5)

    # search and return
    button_cookie = mybrowser.find_element_by_css_selector('button.cookie-banner__right-ui')
    button_cookie.click()
    button_submit = mybrowser.find_element_by_css_selector('button#submit-advanced-search.btn.btn-primary.btn-monster')
    button_submit.click()
    return mybrowser


def parse_search_page(b):
    return [[art.get_attribute('text'), art.get_attribute('href')]
            for art in b.find_elements_by_css_selector('a.title')]

def visit_article(url):
    browser_article = webdriver.Chrome()
    browser_article.get(url)



if __name__ == '__main__':
    input_title = ['happiness']
    input_at_least_one = ['air', 'environmental', 'environment', 'hazards', 'measurement', 'pollution']
    page_result = search_springer(keys_least_words=input_at_least_one, keys_title=input_title)







