from flask import Flask, request, jsonify
import nltk
from nltk.corpus import words

# Download the words corpus if not already done
nltk.download('words')

app = Flask(__name__)

# Function definitions as before

def counting_words(word_list):
    word_count = {}
    for word in word_list:
        word_count[word] = word_count.get(word, 0) + 1
    return word_count

def prob_cal(word_count):
    total_words = sum(word_count.values())
    probabilities = {word: count / total_words for word, count in word_count.items()}
    return probabilities

def get_corrections(word, probabilities, word_list, n=2):
    """
    Return the n most probable corrections for the input word.
    """
    def colab_1(word):
        """Return words that are one edit away from the input word."""
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def colab_2(word):
        """Return words that are two edits away from the input word."""
        return set(e2 for e1 in colab_1(word) for e2 in colab_1(e1))

    suggested_word = list(colab_1(word).intersection(word_list)) or list(colab_2(word).intersection(word_list))

    # Filter out words not in probabilities and sort suggested words by their probabilities in descending order
    best_suggestion = [[s, probabilities[s]] for s in sorted(suggested_word, key=lambda x: probabilities.get(x, 0), reverse=True) if s in probabilities]

    # Return the top n suggestions
    return best_suggestion[:n]

# Get the list of all words
word_list = words.words()

# Count the occurrences of each word
wordcount = counting_words(word_list)

# Calculate probabilities of each word
probs = prob_cal(wordcount)

@app.route('/')
def home():
    return '''
    <form action="/correct" method="post">
        Enter any word: <input type="text" name="word"><br>
        <input type="submit" value="Submit">
    </form>
    '''

@app.route('/correct', methods=['POST'])
def correct():
    user_input = request.form['word']
    corrected_word = get_corrections(user_input, probs, word_list, n=2)
    return jsonify(corrected_word)

if __name__ == '__main__':
    app.run(debug=True)
