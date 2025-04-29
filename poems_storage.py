import json
import os
import datetime
from typing import List, Dict

class PoemsStorage:
    def __init__(self, storage_file: str = 'poems.json'):
        self.storage_file = storage_file
        self.poems = self._load_poems()

    def _load_poems(self) -> Dict:
        """Загружает сохранённые стихи из файла"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_poems(self):
        """Сохраняет стихи в файл"""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.poems, f, ensure_ascii=False, indent=2)

    def add_poem(self, user_id: int, poem: str, theme: str, style: str):
        """Добавляет стихотворение в хранилище"""
        if str(user_id) not in self.poems:
            self.poems[str(user_id)] = []
        
        self.poems[str(user_id)].append({
            'poem': poem,
            'theme': theme,
            'style': style,
            'timestamp': str(datetime.datetime.now())
        })
        self._save_poems()

    def get_user_poems(self, user_id: int) -> List[Dict]:
        """Возвращает все стихи пользователя"""
        return self.poems.get(str(user_id), []) 