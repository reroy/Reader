import csv
from string import punctuation
from nltk.stem import PorterStemmer

porter = PorterStemmer()


def import_data_from_csv():
    extracted_data = {}
    with open('records.csv', 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if row[4] == 'English':
                extracted_data[row[0]] = format_string(row[7].lower())
    csv_file.close()
    return extracted_data


def format_string(title):
    modified = ''
    for word in title.split():
        if word.isdigit():
            modified += ' {}'.format(word.lstrip())
            continue

        new_word = ''
        for char in word:
            if char.isalnum() and char not in set(punctuation):
                new_word += char.encode('utf-8').decode('utf-8').encode('ascii', 'ignore').decode('utf-8')
            elif char in ['/', '-'] and new_word:
                new_word += ' '
        modified += ' {}'.format(new_word.lstrip())
    return modified.lstrip()


def save_extracted_data_in_new_file(extracted_data):
    with open('filtered_records.csv', 'w') as new_csv_file:
        writer = csv.writer(new_csv_file)
        for record, title in extracted_data.items():
            writer.writerow([record, title])
    new_csv_file.close()


def stemming(extracted_data):
    stemmed_data = {}
    for record, title in extracted_data.items():
        stemmed_data[record] = ' '.join(porter.stem(word) for word in title.split())

    return stemmed_data


def encode_data_with_bow(stemmed_data):
    unique_words = {}
    for record, title in stemmed_data.items():
        for word in title.split():
            if word not in unique_words:
                unique_words[word] = 1
            else:
                unique_words[word] += 1
    sorted_unique_words = dict(sorted(unique_words.items(), key=lambda kv: kv[1], reverse=True)[:1000])
    vectors, unique_words = bag_of_words(sorted_unique_words, stemmed_data)
    return vectors, unique_words


def bag_of_words(unique_words, stemmed_data):
    vectors = {}
    for record, title in stemmed_data.items():
        words_in_title = title.split()
        vector = []
        for word in unique_words.keys():
            if word in words_in_title:
                vector.append(1)
            else:
                vector.append(0)
        vectors[record] = vector
    return vectors, unique_words
