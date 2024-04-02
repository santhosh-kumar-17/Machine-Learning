from textblob import TextBlob

def analyze_sentiment(text):
    # Create a TextBlob object
    blob = TextBlob(text)
    
    # Get the polarity score
    polarity = blob.sentiment.polarity
    
    # Classify sentiment based on polarity score
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# Example text for analysis
text = input('Enter your statement: ')

# Analyze sentiment
sentiment = analyze_sentiment(text)

# Print the sentiment analysis result
print("Sentiment:", sentiment)

text.lower()
if "yes" in text:
    print("dei veliya jav")
# Check if the user's input matches "yes" or "aama"
if text.lower() == "yes" or text.lower() == "aama":
    print("gotha veliya po da kk")
