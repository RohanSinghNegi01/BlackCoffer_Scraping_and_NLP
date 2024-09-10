def load_word_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        words = file.read().splitlines()
    return set(words)

 #**Integrate the loaded lists into the analysis functions**:
    #```python
import nltk
from textblob import TextBlob
import re
import os
import numpy as np
import pandas as pd
import chardet

# Ensure nltk resources are downloaded
nltk.download('punkt')
nltk.download('cmudict')
nltk.download('stopwords')

from nltk.corpus import cmudict, stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Load syllable dictionary and stopwords
d = cmudict.dict()

# Load the word lists
def load_word_list(file_path):
    with open(file_path, 'r', encoding='utf-8' , errors='ignore') as file:
        words = file.read().splitlines()
    return set(words)

stop_words = load_word_list(r'C:\Users\ROHAN\Desktop\NLP\stopwords.txt')
positive_words = load_word_list(r'C:\Users\ROHAN\Desktop\NLP\positive-words.txt')
negative_words = load_word_list(r'C:\Users\ROHAN\Desktop\NLP\negative-words.txt')

def count_syllables(word):
    try:
        return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
    except KeyError:
        return 0

def compute_readability_metrics(text):
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    words = [word for word in words if word.isalpha() and word.lower() not in stop_words]
    word_count = len(words)
    sentence_count = len(sentences)
    syllable_count = sum(count_syllables(word) for word in words)
    complex_words = [word for word in words if count_syllables(word) > 2]
    complex_word_count = len(complex_words)
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    percentage_complex_words = complex_word_count / word_count if word_count > 0 else 0
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
    avg_syllables_per_word = syllable_count / word_count if word_count > 0 else 0
    avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
    personal_pronouns = len(re.findall(r'\b(I|we|my|ours|us)\b', text, re.I))
    
    return {
        'WORD_COUNT': word_count,
        'AVG_SENTENCE_LENGTH': avg_sentence_length,
        'PERCENTAGE_OF_COMPLEX_WORDS': percentage_complex_words,
        'FOG_INDEX': fog_index,
        'AVG_NUMBER_OF_WORDS_PER_SENTENCE': avg_sentence_length,  # Same as avg_sentence_length
        'COMPLEX_WORD_COUNT': complex_word_count,
        'SYLLABLE_PER_WORD': avg_syllables_per_word,
        'PERSONAL_PRONOUNS': personal_pronouns,
        'AVG_WORD_LENGTH': avg_word_length,
    }

def sentiment_analysis(text):
    blob = TextBlob(text)
    return {
        'POLARITY_SCORE': blob.sentiment.polarity,
        'SUBJECTIVITY_SCORE': blob.sentiment.subjectivity
    }

def analyze_texts(input_dir, output_file):
    # Load the input Excel file
    input_df = pd.read_excel('Input.xlsx')
    
    # Initialize output DataFrame
    output_df = pd.DataFrame(columns=[
        'URL_ID', 'URL', 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY_SCORE', 'SUBJECTIVITY_SCORE',
        'AVG_SENTENCE_LENGTH', 'PERCENTAGE_OF_COMPLEX_WORDS', 'FOG_INDEX', 'AVG_NUMBER_OF_WORDS_PER_SENTENCE',
        'COMPLEX_WORD_COUNT', 'WORD_COUNT', 'SYLLABLE_PER_WORD', 'PERSONAL_PRONOUNS', 'AVG_WORD_LENGTH'
    ])

    for index, row in input_df.iterrows():
        url_id = row['URL_ID']
        url = row['URL']
        
        # Load article text from file
        file_path = os.path.join(input_dir, f"{url_id}.txt")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Compute sentiment scores
            sentiment_scores = sentiment_analysis(text)
            
            # Compute readability metrics
            readability_metrics = compute_readability_metrics(text)
            
            # Count positive and negative words
            words = word_tokenize(text.lower())
            positive_score = sum(1 for word in words if word in positive_words)
            negative_score = sum(1 for word in words if word in negative_words)
            
            # Create a new row with all the computed metrics
            new_row = {
                'URL_ID': url_id,
                'URL': url,
                'POSITIVE SCORE': positive_score,
                'NEGATIVE SCORE': negative_score,
                'POLARITY_SCORE': sentiment_scores['POLARITY_SCORE'],
                'SUBJECTIVITY_SCORE': sentiment_scores['SUBJECTIVITY_SCORE'],
                'AVG_SENTENCE_LENGTH': readability_metrics['AVG_SENTENCE_LENGTH'],
                'PERCENTAGE_OF_COMPLEX_WORDS': readability_metrics['PERCENTAGE_OF_COMPLEX_WORDS'],
                'FOG_INDEX': readability_metrics['FOG_INDEX'],
                'AVG_NUMBER_OF_WORDS_PER_SENTENCE': readability_metrics['AVG_NUMBER_OF_WORDS_PER_SENTENCE'],
                'COMPLEX_WORD_COUNT': readability_metrics['COMPLEX_WORD_COUNT'],
                'WORD_COUNT': readability_metrics['WORD_COUNT'],
                'SYLLABLE_PER_WORD': readability_metrics['SYLLABLE_PER_WORD'],
                'PERSONAL_PRONOUNS': readability_metrics['PERSONAL_PRONOUNS'],
                'AVG_WORD_LENGTH': readability_metrics['AVG_WORD_LENGTH']
            }
            output_df = output_df._append(new_row, ignore_index=True)

    # Save the output DataFrame to an Excel file
    output_df.to_excel(output_file, index=False)

# Run the analysis
analyze_texts(input_dir=r'C:\Users\ROHAN\Desktop\NLP\URL_ID', output_file=r'C:\Users\ROHAN\Desktop\NLP\Output_Data_Structure.xlsx')
