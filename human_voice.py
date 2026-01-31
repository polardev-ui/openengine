import random
import re


class HumanVoiceEngine:
    def __init__(self):
        self.filler_words = ["um", "uh", "like", "you know", "I mean", "well"]
        self.thinking_phrases = ["let me think", "hmm", "let's see", "oh"]
        self.reactions = ["oh wow", "interesting", "cool", "nice", "awesome", "oh"]
        self.confirmations = ["yeah", "sure", "absolutely", "definitely", "totally", "of course"]
        
        self.personality_traits = {
            'enthusiasm': 0.7,
            'casual': 0.8,
            'filler_frequency': 0.15,
            'reaction_frequency': 0.3
        }
    
    def add_human_elements(self, text: str, context: str = "general") -> str:
        if not text or len(text) < 10:
            return text
        
        sentences = self._split_into_sentences(text)
        humanized_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            humanized = sentence
            
            if i == 0 and random.random() < self.personality_traits['reaction_frequency']:
                if any(word in sentence.lower() for word in ['see', 'detect', 'found', 'there']):
                    humanized = f"{random.choice(self.reactions)}, {humanized}"
            
            if random.random() < self.personality_traits['filler_frequency']:
                words = humanized.split()
                if len(words) > 5:
                    insert_pos = random.randint(2, min(len(words) - 2, 5))
                    filler = random.choice(self.filler_words)
                    words.insert(insert_pos, filler)
                    humanized = ' '.join(words)
            
            if i > 0 and random.random() < 0.2:
                connectors = ["so", "and", "also", "plus"]
                humanized = f"{random.choice(connectors)}, {humanized.lower()}"
            
            humanized_sentences.append(humanized)
        
        result = ' '.join(humanized_sentences)
        
        result = self._add_prosody_markers(result)
        
        return result
    
    def _split_into_sentences(self, text: str) -> list:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s.strip()]
    
    def _add_prosody_markers(self, text: str) -> str:
        text = re.sub(r'([.!?])', r'\1 [[slnc 200]]', text)
        
        text = re.sub(r',', r', [[slnc 100]]', text)
        
        if '!' in text:
            text = re.sub(r'!', '! [[emph +]]', text)
        
        return text
    
    def add_casual_response(self, text: str) -> str:
        casual_starters = [
            "Alright, ",
            "Okay, ",
            "So, ",
            "Well, ",
            "Right, "
        ]
        
        if random.random() < 0.3 and not text.startswith(tuple(casual_starters)):
            text = random.choice(casual_starters) + text.lower()[0] + text[1:]
        
        return text
    
    def add_excitement(self, text: str) -> str:
        excited_words = {
            'good': 'great',
            'nice': 'awesome',
            'okay': 'perfect',
            'yes': 'yeah',
            'sure': 'absolutely'
        }
        
        for bland, excited in excited_words.items():
            if random.random() < 0.5:
                text = re.sub(r'\b' + bland + r'\b', excited, text, flags=re.IGNORECASE)
        
        return text
    
    def make_conversational(self, text: str, question: str = "") -> str:
        text = self.add_casual_response(text)
        
        text = self.add_excitement(text)
        
        text = self.add_human_elements(text)
        
        return text
