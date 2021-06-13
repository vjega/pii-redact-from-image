from PIL import Image, ImageDraw
import pytesseract as ocr

import spacy
from spacy.matcher import Matcher
from collections import Counter
from string import punctuation

nlp = spacy.load('en_core_web_lg')

class ImageRedact():
    '''
    '''

    def _remove_trailing_punctuation(self, text):
        punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''
        text = text.strip()
        if text[-1] in punc:
            return text[:-1]
        return text


    def __init__(self, imagefile: str):
        self.image = imagefile
        self.img = Image.open(self.image)
        self._readtext()
        self._todict()
        self._find_pii()


    def _find_pii(self):
        self.cleaneduptree = []
        redactkeys = " ".join(self.redact_words).split()
        for t in self.texttree:
            if t['text'] in redactkeys:
                self.cleaneduptree.append(t)


    def _readtext(self):
        self.textdata = ocr.image_to_data(self.img)
        self.text = ocr.image_to_string(self.img)
        self.redact_words = []
        doc = nlp(self.text)
        
        for token in doc:
            if token.text:
                print(f'text : {token.text} key : {token.tag_}, desc : {spacy.explain(token.tag_)}')
            if (
                token.like_email or
                token.like_url or
                token.tag_ == 'NNP' or
                token.tag_ == 'CD' or
                token.tag_ == 'ADD'
            ):
                self.redact_words.append(token.text)
            

    def _todict(self):
        self.texttree = []
        lines = self.textdata.splitlines()
        head = lines[0].split("\t")
        cols = lines[1:]
        
        for col in cols:
            d = {}
            value = col.split("\t")
            for idx, h in enumerate(head):
                if h in ["left", "top", "height", "width"]:
                    d[h] = int(value[idx])
                elif h == "text" :
                    d[h] = self._remove_trailing_punctuation(value[idx]) if value[idx] else ''
            if d['text']:
                self.texttree.append(d)

    def redact(self):
        dr = ImageDraw.Draw(self.img)
        for text in self.cleaneduptree:
            xy = (text['left'],text['top']), (text['left']+text['width'],text['top']+text['height'])
            dr.rectangle(
                xy,
                fill = "#666"
            )
        self.img.save("output.png")



