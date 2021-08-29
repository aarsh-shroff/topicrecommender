def main(webpages):
    import os
    import itertools
    import numpy as np
    import pandas as pd
    from pprint import pprint
    from collections import Counter

    # Web scraping
    from requests_html import HTMLSession
    from bs4 import BeautifulSoup

    # Text preprocessing
    import nltk
    from nltk.stem import WordNetLemmatizer
    from nltk.corpus import wordnet
    import re

    # Gensim topic modelling
    import gensim
    import gensim.corpora as corpora
    from gensim.utils import simple_preprocess
    from gensim.models import CoherenceModel

    # Plotting tools
    '''
    import pyLDAvis
    import pyLDAvis.gensim
    '''

    # Enable logging for gensim
    import logging
    logging.basicConfig(filename='scraper.log', level=logging.ERROR, datefmt='%d/%b/%y %H:%M:%S',
                        format='%(asctime)s: %(levelname)s- %(message)s', filemode='w')

    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # NLTK Stop words
    from nltk.corpus import stopwords
    stop_words = stopwords.words('english')
    stop_words.extend(['from', 'subscribe'])

    # Get POS tags for words
    def get_wordnet_pos(words):
        '''Map POS tag to first character lemmatize() accepts'''
        tag = nltk.pos_tag([words])[0][1][0].upper()
        tag_dict = {'J': wordnet.ADJ,
                    'N': wordnet.NOUN,
                    'V': wordnet.VERB,
                    'R': wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)
    
    topic_terms = list()

    for webpage in webpages:
        try:
            # Scrape the webpage and retrieve its HTML
            session = HTMLSession()
            resp = session.get(webpage)
            soup = BeautifulSoup(resp.content, 'lxml')

            #text = soup.get_text().strip()
            
            # Get the text from the HTML
            text = list()
            p_tags = soup.find_all('p')
            for tag in p_tags:
                text.append(tag.text)
            text = ''.join(text)
            
            # Remove emails
            text = re.sub('\S*@\S*\s?', '', text)

            # Remove new line characters
            text = re.sub('\s+', ' ', text)

            # Remove single quotes
            text = re.sub("\'", "", text)

            # Tokenize text and remove punctuation
            words = simple_preprocess(str(text), deacc=True)

            # Build the bigram and trigram models
            bigram = gensim.models.Phrases(words, min_count=5, threshold=100)
            trigram = gensim.models.Phrases(bigram[words], threshold=100)

            # Club a sentence as a bigram/trigram
            bigram_mod = gensim.models.phrases.Phraser(bigram)
            trigram_mod = gensim.models.phrases.Phraser(trigram)

            # Remove Stop Words
            words_nostops = [word for word in words if word not in stop_words]

            # Form Bigrams
            words_bigrams = bigram_mod[words_nostops]
            
            # Do lemmatization
            lemmatizer = nltk.WordNetLemmatizer()
            lemmatized_words = [lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in words_bigrams]

            # Create dictionary
            words_lemmatized = list()
            words_lemmatized.append(lemmatized_words)
            id2word = corpora.Dictionary(words_lemmatized)

            # Create corpus
            texts = words_lemmatized

            # Term Document Frequency
            corpus = [id2word.doc2bow(text) for text in texts]

            def compute_coherence_values(limit, start=2, step=3):
                ''' Compute c_v coherence for various number of topics'''
                coherence_values = list()
                model_list = list()
                for num_topics in range(start, limit, step):
                    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=id2word, num_topics=num_topics, 
                                                        random_state=100, update_every=1, chunksize=100,
                                                        passes=10, alpha='auto', per_word_topics=True)
                    model_list.append(lda_model)
                    coherence_model = CoherenceModel(model=lda_model, texts=words_lemmatized, dictionary=id2word,
                                                        coherence='c_v')
                    coherence_values.append(coherence_model.get_coherence())
                return model_list, coherence_values

            model_list, coherence_values = compute_coherence_values(start=2, limit=40, step=6)

            # Select the model and print the topics
            optimal_value = max(coherence_values)
            optimal_index = coherence_values.index(optimal_value)
            optimal_model = model_list[optimal_index]
            #pprint(optimal_model.print_topics())
            doc_lda = optimal_model[corpus]
            
            '''
            # Compute Perplexity
            print('\nPerplexity: {}'.format(optimal_model.log_perplexity(corpus)))

            # Print Coherence Score
            print('\nCoherence Score: {}'.format(optimal_value))

            # Visualize the topics
            vis = pyLDAvis.gensim.prepare(optimal_model, corpus, id2word)
            page_index = int(webpages.index(webpage)) + 1
            if os.path.exists('LDA_Visualization{}.html'.format(page_index)) == True:
                os.remove('LDA_Visualization{}.html'.format(page_index))
            pyLDAvis.save_html(vis, 'LDA_Visualization{}.html'.format(page_index))
            '''
            
            top_topics = optimal_model.top_topics(corpus=corpus, texts=words_lemmatized, dictionary=id2word, coherence='c_v')
            terms = list()
            for topic in top_topics:
                if topic[1] >= 0.2:
                    for term in itertools.islice(topic[0], 0, 5):
                        terms.append(term[1])
            topic_terms.append(terms)

        except Exception as e:
            logging.error(e)
    
    flat_list = [item for sublist in topic_terms for item in sublist]
    c = Counter(flat_list)
    terms = c.most_common(5)
    final_terms = [term[0] for term in terms]
    return final_terms