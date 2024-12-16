import os
from collections import defaultdict

import torch
from pysentimiento import create_analyzer
from pysentimiento.analyzer import AnalyzerOutput
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          pipeline)


class Analyser:
    def __init__(self, lang='en'):
        # self._emotion_analyzer2 = create_analyzer(task="emotion", lang=lang)
        self._hate_speech_analyzer = create_analyzer(task="hate_speech", lang=lang)
        self._sentiment_analyzer = create_analyzer(task="sentiment", lang=lang)

        # Resolve absolute path to the fine_tuned_rubert directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "fine_tuned_rubert")

        # Load the model
        self._emotion_analyzer = AutoModelForSequenceClassification.from_pretrained(
            pretrained_model_name_or_path=path,
            local_files_only=True)
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=path, local_files_only=True)
        self._emotion_analyzer.eval()  # Set model to evaluation mode
        self._language_recognizer = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")
        # self._translator = Translator()
        self.result = None

    def recognise_lang(self, text: str) -> str:
        return self._language_recognizer(text)

    def analyse_emotion_old(self, data: str, lang='en'):
        return self._emotion_analyzer2.predict(data)

    def analyse_emotion(self, data: str, lang='en'):
        # print("analyse_emotion",data)
        inputs = self.tokenizer(data, truncation=True, padding='max_length', max_length=128, return_tensors="pt")
        # print(data)
        with torch.no_grad():
            outputs = self._emotion_analyzer(**inputs)
            logits = outputs.logits

        # Convert logits to probabilities
        probabilities = torch.nn.functional.softmax(logits, dim=1)


        label_to_emotion = {
            0: "sadness",
            1: "joy",
            2: "love",
            3: "anger",
            4: "fear",
            5: "surprise",
            6: "neutral"
        }
        # Get the predicted label
        predicted_label = torch.argmax(probabilities).item()
        probabilities = probabilities.squeeze().tolist()

        # Get the predicted label
        if max(probabilities) < 0.3:
            probabilities.append(1)
            predicted_label = 6

        # Map probabilities to their labels
        probas_dict = {label_to_emotion[i]: prob for i, prob in enumerate(probabilities)}

        # Create the AnalyzerOutput
        output = AnalyzerOutput(probas=probas_dict, sentence=data, context=None)
        # print(output)
        return output, predicted_label

    def analyse_hate_speech(self, data: str, lang='en'):
        return self._hate_speech_analyzer.predict(data)

    def analyse_sentiment(self, data: str, lang='en'):
        return self._sentiment_analyzer.predict(data)

    def analyse_comments(self, comments: dict, analysis_types: dict):
        print("analyse_comments", analysis_types, analysis_types.get('emotion'))
        res = dict()
        frequency = defaultdict(int)
        for key, entry in comments.items():
            text = entry[1]
            ans = dict()
            if len(text) > 256:
                text = text[:256]
            if analysis_types.get('lang') is not None:
                lang = self.recognise_lang(text)
                ans['lang'] = lang
            # if lang not in ['es', 'en', 'it', 'pt']:
            # text = self.translate(text)
            # lang = 'en'
            if analysis_types.get('sentiment') is not None:
                sentiment = self.analyse_sentiment(text)
                ans['sentiment'] = sentiment
            if analysis_types.get('hate') is not None:
                hate = self.analyse_hate_speech(text)
                ans['hate'] = hate
            if analysis_types.get('emotion') is not None:
                emotion, label = self.analyse_emotion(text)
                comments[key] = label
                ans['emotion'] = emotion

            if analysis_types.get('word_count') is not None:
                words = "".join(c for c in text if c.isalnum() or c.isspace())
                words = words.lower().split()
                for word in words:
                    frequency[word] += 1
            res[entry[8]] = ans
        if analysis_types.get('word_count') is not None:
            res['word_count'] = frequency
        self.result = res
        return res
